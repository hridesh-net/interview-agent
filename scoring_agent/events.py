from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnswerSubmittedEvent:
    interview_id: str
    turn_id: int
    question: str
    answer: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            interview_id=data["interview_id"],
            turn_id=data["turn_id"],
            question=data["question"],
            answer=data["answer"],
            timestamp=data.get("timestamp") or datetime.utcnow().isoformat(),
        )