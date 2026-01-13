from dataclasses import dataclass, field, asdict
from typing import List, Dict
import uuid
import time


@dataclass
class QARecord:
    question: str
    answer: str
    intent_analysis: Dict
    score: Dict
    timestamp: float = field(default_factory=time.time)


@dataclass
class InterviewState:
    interview_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    jd: str = ""
    questions: List[Dict] = field(default_factory=list)
    current_index: int = 0
    history: List[QARecord] = field(default_factory=list)
    status: str = "initialized"  
    version: int = 1          # for future migrations
    consecutive_failures: int = 0
    total_failures: int = 0
    terminated_reason: str | None = None
    disengagement_count: int = 0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        state = InterviewState(
            interview_id=data["interview_id"],
            jd=data["jd"],
            questions=data["questions"],
            current_index=data["current_index"],
            status=data["status"],
            version=data.get("version", 1),
        )

        state.history = [
            QARecord(**h) for h in data.get("history", [])
        ]

        return state