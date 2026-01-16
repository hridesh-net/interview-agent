from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import uuid
import time
from datetime import datetime


def _serialize(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}


@dataclass
class QARecord:
    question: str
    answer: str
    intent_analysis: Optional[Dict] = None
    score: Optional[Dict] = None
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
    started_at: datetime = datetime.utcnow().isoformat()

    topic_question_count: int = 0
    max_questions_per_topic: int = 4

    disengagement_count: int = 0
    max_disengagements: int = 2

    max_duration_minutes: int = 30

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        state = InterviewState(
            interview_id=data["interview_id"],
            jd=data["jd"],
            questions=data["questions"],
            current_index=data["current_index"],
            status=data.get("status") or "initialized",
            version=data.get("version", 1),
        )

        state.history = [
            QARecord(**h) for h in data.get("history", [])
        ]

        return state