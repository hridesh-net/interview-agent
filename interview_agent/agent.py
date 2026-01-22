from datetime import datetime, timedelta

from .executor import SkillExecutor
from .state import InterviewState, QARecord

from interview_agent.schemas import (
    QuestionGeneratorOutput,
    IntentEvaluationOutput,
    FollowupQuestionOutput,
)

from interview_agent.dapr_publisher import publish_answer_event
from interview_agent.trace import TraceContext
from interview_agent.logger import JsonLogger

# 🔹 Vision perception is session-level context (not skill-level)
from vl_jepa_service.context import PerceptionContext as VISION_PERCEPTION
from vl_jepa_service.context import load_perception_state


class InterviewAgent:
    def __init__(self, skill_engine, state_store):
        self.logger = JsonLogger()
        self.skills = SkillExecutor(skill_engine, logger=self.logger)
        self.store = state_store

    # -----------------------------------------------------
    # Vision Perception Injection (ONLY place it belongs)
    # -----------------------------------------------------
    def _with_vision_perception(self, *, interview_id: str, payload: dict):
        """
        Inject latest vision perception into LLM input if available.
        SkillEngine remains completely interview-agnostic.
        """
        perception = VISION_PERCEPTION.get(interview_id=interview_id)
        perception = load_perception_state(interview_id=interview_id)

        if perception:
            payload["vision_perception"] = {
                "scene": perception["scene_description"],
                "object": perception.get("object"),
                "confidence": perception["confidence"],
            }

        if not perception:
            return payload

        # Shallow copy to avoid mutating original payload
        enriched_payload = dict(payload)
        return enriched_payload

    # -----------------------------------------------------
    # Interview lifecycle
    # -----------------------------------------------------
    def start(self, jd_text: str):
        state = InterviewState(jd=jd_text)
        trace = TraceContext.create(state.interview_id)

        self.logger.log(
            event="interview_started",
            interview_id=state.interview_id,
            trace_id=trace.trace_id,
        )

        questions = self.skills.run(
            skill="question_generator_from_jd",
            input=jd_text,
            schema=QuestionGeneratorOutput,
            trace=trace,
        ).questions

        state.questions = [
            q.model_dump() for q in questions
        ]
        state.status = "running"
        self.store.save(state)

        return state

    def start_or_resume(
        self,
        jd_text: str | None = None,
        interview_id: str | None = None,
    ):
        if interview_id and self.store.exists(interview_id):
            state = self.store.load(interview_id)

            self.logger.log(
                event="interview_resumed",
                interview_id=state.interview_id,
            )
            return state

        if not jd_text:
            raise ValueError("jd_text is required to start a new interview")

        return self.start(jd_text)

    # -----------------------------------------------------
    # Interview flow
    # -----------------------------------------------------
    def next_question(self, state):
        return state.questions[state.current_index]["question"]

    def submit_answer(self, interview_id: str, answer: str):
        # -----------------------------
        # Load state
        # -----------------------------
        state = self.store.load(interview_id)

        if state.status != "running":
            raise RuntimeError(
                f"Interview is not active, current status: {state.status}"
            )

        # -----------------------------
        # Time guard
        # -----------------------------
        elapsed = datetime.utcnow() - datetime.fromisoformat(state.started_at)
        if elapsed > timedelta(minutes=state.max_duration_minutes):
            state.status = "terminated"
            state.terminated_reason = "time_limit_reached"
            self.store.save(state)
            return state

        trace = TraceContext.create(state.interview_id)
        question = state.questions[state.current_index]["question"]

        # -----------------------------
        # Intent evaluation (VISION-AWARE)
        # -----------------------------
        intent = self.skills.run(
            skill="answer_intent_evaluator",
            input=self._with_vision_perception(
                interview_id=state.interview_id,
                payload={
                    "question": question,
                    "answer": answer,
                },
            ),
            schema=IntentEvaluationOutput,
            trace=trace,
        )

        # -----------------------------
        # Persist answer immediately
        # -----------------------------
        state.history.append(
            QARecord(question, answer, intent.model_dump())
        )

        publish_answer_event(
            {
                "interview_id": state.interview_id,
                "turn_id": state.current_index,
                "question": question,
                "answer": answer,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # -----------------------------
        # Follow-up decision (VISION-AWARE)
        # -----------------------------
        followup = self.skills.run(
            skill="followup_question_generator",
            input=self._with_vision_perception(
                interview_id=state.interview_id,
                payload={
                    "previous_question": question,
                    "answer": answer,
                    "intent_analysis": intent.model_dump(),
                },
            ),
            schema=FollowupQuestionOutput,
            trace=trace,
        )

        state_signal = followup.candidate_state or "engaged"
        action = followup.next_action

        # -----------------------------
        # Exit paths
        # -----------------------------
        if action == "end_interview" or state_signal == "exit_intent":
            state.status = "terminated"
            state.terminated_reason = "llm_recommended"
            self.store.save(state)
            return state

        if state_signal == "disengaged":
            state.disengagement_count += 1
        else:
            state.disengagement_count = 0

        if state.disengagement_count >= state.max_disengagements:
            state.status = "terminated"
            state.terminated_reason = "candidate_disengaged"
            self.store.save(state)
            return state

        # -----------------------------
        # Topic & follow-up control
        # -----------------------------
        state.topic_question_count += 1

        if (
            action == "followup"
            and state.topic_question_count
            < state.max_questions_per_topic
            and followup.followup_question
        ):
            state.questions.insert(
                state.current_index + 1,
                {
                    "question": followup.followup_question,
                    "intent_type": followup.intent_type,
                    "skill_focus": "follow-up",
                },
            )
            state.current_index += 1
        else:
            state.current_index += 1
            state.topic_question_count = 0

        # -----------------------------
        # Completion
        # -----------------------------
        if state.current_index >= len(state.questions):
            state.status = "completed"

        self.store.save(state)
        return state