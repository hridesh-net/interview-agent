from pydantic import BaseModel, Field
from typing import Literal, List


# ---------------------------
# Question Generator Schema
# ---------------------------

class InterviewQuestion(BaseModel):
    question: str
    intent_type: Literal["what", "why", "when", "how"]
    candidate_state: str
    skill_focus: str


class QuestionGeneratorOutput(BaseModel):
    questions: List[InterviewQuestion]


# ---------------------------
# Intent Evaluator Schema
# ---------------------------

class IntentEvaluationOutput(BaseModel):
    intent_type: Literal["what", "why", "when", "how"]
    intent_matched: bool
    intent_fulfillment: Literal["complete", "partial", "not_fulfilled"]
    example_provided: bool
    analysis: str


# ---------------------------
# Score Calculator Schema
# ---------------------------

class ScoreOutput(BaseModel):
    intent_score: float = Field(ge=0.0, le=1.0)
    content_score: float = Field(ge=0.0, le=1.0)
    feedforward: str


# ---------------------------
# Follow-up Generator Schema
# ---------------------------

class FollowupQuestionOutput(BaseModel):
    followup_question: str
    intent_type: Literal["what", "why", "when", "how"]
    candidate_state: str
    reason: str
    next_action: str