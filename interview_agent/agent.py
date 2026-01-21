from datetime import datetime, timedelta

from .executor import SkillExecutor
from .state import InterviewState, QARecord

from interview_agent.schemas import (
    QuestionGeneratorOutput,
    IntentEvaluationOutput,
    ScoreOutput,
    FollowupQuestionOutput,
)

from interview_agent.dapr_publisher import publish_answer_event

from interview_agent.trace import TraceContext
from interview_agent.logger import JsonLogger


class InterviewAgent:
    def __init__(self, skill_engine, state_store):
        self.logger = JsonLogger()
        self.skills = SkillExecutor(skill_engine, logger=self.logger)
        self.store = state_store

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
            trace=trace
        ).questions

        state.questions = questions
        state.status = "running"
        self.store.save(state)

        return state

    def start_or_resume(self, jd_text: str | None = None, interview_id: str | None = None):
        if interview_id and self.store.exists(interview_id):
            state = self.store.load(interview_id)
            
            print("Resuming interview:")

            self.logger.log(
                event="interview_resumed",
                interview_id=state.interview_id,
            )

            return state

        if not jd_text:
            raise ValueError("jd_text is required to start a new interview")

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
            trace=trace
        )
        
        print("Generated Questions:")
        print(questions)
        print(type(questions))
        
        self.logger.log(
            event="question_generated",
            interview_id=state.interview_id,
            trace_id=trace.trace_id,
            questions=len(questions.questions),
        )

        state.questions = [
            q.model_dump() for q in questions.questions
        ]
        state.status = "running"
        
        self.logger.log(
            event="state_generated",
            interview_id=state.interview_id,
            trace_id=trace.trace_id,
            state=state.to_dict(),
        )
        self.store.save(state)

        return state

    def next_question(self, state):
        return state.questions[state.current_index]["question"]

    def submit_answer(self, interview_id: str, answer: str):
        # -----------------------------
        # Load state FIRST
        # -----------------------------
        state = self.store.load(interview_id)
        print(state.status)
        print("----")
        print(state.to_dict())
        print(interview_id)
        print("----")
        

        if state.status != "running":
            raise RuntimeError(f"Interview is not active, current status: {state.status}")

        # -----------------------------
        # Time guard (30 min)
        # -----------------------------
        elapsed = datetime.utcnow() - datetime.fromisoformat(state.started_at)
        if elapsed > timedelta(minutes=state.max_duration_minutes):
            state.status = "terminated"
            state.terminated_reason = "time_limit_reached"
            self.store.save(state)
            return state

        trace = TraceContext.create(state.interview_id)
        q = state.questions[state.current_index]["question"]

        # -----------------------------
        # Intent evaluation
        # -----------------------------
        intent = self.skills.run(
            skill="answer_intent_evaluator",
            input={"question": q, "answer": answer},
            schema=IntentEvaluationOutput,
            trace=trace
        )

        # -----------------------------
        # Persist answer immediately
        # -----------------------------
        state.history.append(QARecord(q, answer, intent.model_dump()))

        publish_answer_event({
            "interview_id": state.interview_id,
            "turn_id": state.current_index,
            "question": q,
            "answer": answer,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # -----------------------------
        # Follow-up decision (LLM-guided)
        # -----------------------------
        followup = self.skills.run(
            skill="followup_question_generator",
            input={
                "previous_question": q,
                "answer": answer,
                "intent_analysis": intent.model_dump(),
            },
            schema=FollowupQuestionOutput,
            trace=trace
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
            and state.topic_question_count < state.max_questions_per_topic
            and followup.followup_question
        ):
            state.questions.insert(
                state.current_index + 1,
                {
                    "question": followup.followup_question,
                    "intent_type": followup.intent_type,
                    "skill_focus": "follow-up",
                }
            )
            state.current_index += 1
        else:
            # Move to next topic
            state.current_index += 1
            state.topic_question_count = 0

        # -----------------------------
        # End interview if no questions left
        # -----------------------------
        if state.current_index >= len(state.questions):
            state.status = "completed"

        self.store.save(state)
        return state