from dataclasses import dataclass
import uuid


@dataclass
class TraceContext:
    interview_id: str
    trace_id: str

    @staticmethod
    def create(interview_id: str):
        return TraceContext(
            interview_id=interview_id,
            trace_id=str(uuid.uuid4())
        )