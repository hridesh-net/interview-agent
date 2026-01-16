from .events import RuntimeEvent
from .runtime_state import RuntimeState


class InterviewRuntime:
    def __init__(self, agent, state_store):
        self.agent = agent                  # unchanged InterviewAgent
        self.store = state_store
        self.runtime_states: dict[str, RuntimeState] = {}

    def get_runtime(self, interview_id):
        if interview_id not in self.runtime_states:
            self.runtime_states[interview_id] = RuntimeState(interview_id)
        return self.runtime_states[interview_id]

    def handle_event(self, event: RuntimeEvent):
        rt = self.get_runtime(event.interview_id)
        rt.last_activity_ms = event.timestamp_ms

        # -------------------------------------------------
        # 1. START INTERVIEW (JD ingestion)
        # -------------------------------------------------
        if event.type == "interview.start":
            jd_text = event.payload.get("jd_text")
            if not jd_text:
                raise ValueError("jd_text is required to start interview")

            state = self.agent.start_or_resume(jd_text=jd_text)

            return {
                "type": "interviewer.prompt",
                "question": self.agent.next_question(state),
                "status": state.status,
                "interview_id": state.interview_id,
            }

        # -------------------------------------------------
        # 2. REAL-TIME PARTIAL ANSWERS
        # -------------------------------------------------
        if event.type == "answer.partial":
            rt.partial_answer += event.payload.get("text", "")
            return None

        # -------------------------------------------------
        # 3. FINAL ANSWER (TURN BOUNDARY)
        # -------------------------------------------------
        if event.type == "answer.final":
            state = self.agent.submit_answer(
                interview_id=event.interview_id,
                answer=event.payload["text"],
            )

            return {
                "type": "interviewer.prompt",
                "question": (
                    self.agent.next_question(state)
                ),
                "status": state.status,
            }

        # -------------------------------------------------
        # 4. VIDEO SIGNALS (ASYNC, NON-BLOCKING)
        # -------------------------------------------------
        if event.type == "video.signal":
            rt.video_signals.update(event.payload)
            return None

        # -------------------------------------------------
        # 5. AUDIO TRANSCRIPTS
        # -------------------------------------------------
        if event.type == "audio.transcript":
            rt.audio_buffer.append(event.payload["text"])
            return None

        # -------------------------------------------------
        # 6. HEARTBEAT / KEEPALIVE
        # -------------------------------------------------
        if event.type == "heartbeat":
            return None

        raise ValueError(f"Unhandled event type: {event.type}")