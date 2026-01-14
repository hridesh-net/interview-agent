from dataclasses import dataclass
from typing import Dict


@dataclass
class AnswerScore:
    intent_score: float
    content_score: float
    feedforward: str


@dataclass
class ScoringState:
    interview_id: str
    scores: Dict[int, AnswerScore]

    def to_dict(self):
        return {
            "interview_id": self.interview_id,
            "scores": {
                str(k): {
                    "intent_score": v.intent_score,
                    "content_score": v.content_score,
                    "feedforward": v.feedforward,
                }
                for k, v in self.scores.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            interview_id=data["interview_id"],
            scores={
                int(k): AnswerScore(**v)
                for k, v in data.get("scores", {}).items()
            },
        )