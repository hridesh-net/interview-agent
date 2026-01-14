from fastapi import FastAPI
from pydantic import BaseModel
from scoring_agent.executor import ScoringExecutor
from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient

app = FastAPI()

# -----------------------------
# Setup scoring dependencies
# -----------------------------
registry = SkillRegistry()
registry.load("./skills")

llm = HuggingFaceClient(
    model_id="meta-llama/Llama-3.1-8B-Instruct:novita",
    stream=False,
)

skill_engine = SkillEngine(registry, llm)
scorer = ScoringExecutor(skill_engine)


# -----------------------------
# Dapr subscription discovery
# -----------------------------
@app.get("/dapr/subscribe")
def subscribe():
    return [
        {
            "pubsubname": "pubsub",
            "topic": "answer_submitted",
            "route": "score-answer",
        }
    ]


# -----------------------------
# Event handler
# -----------------------------
class AnswerSubmittedEvent(BaseModel):
    interview_id: str
    turn_id: int
    question: str
    answer: str
    timestamp: str


@app.post("/score-answer")
def handle_answer(event: AnswerSubmittedEvent):
    result = scorer.evaluate(
        question=event.question,
        answer=event.answer,
    )

    # TODO: persist result (file/db/redis/state store)
    # TODO: optionally publish scoring_completed event

    return {"status": "processed"}