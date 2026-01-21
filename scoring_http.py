from fastapi import FastAPI
from fastapi import Body
from pydantic import BaseModel
from scoring_agent.executor import ScoringExecutor
from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient
from llm.groq_client import GroqClient

app = FastAPI()

# -----------------------------
# Setup scoring dependencies
# -----------------------------
registry = SkillRegistry()
registry.load("./skills")

# llm = HuggingFaceClient(
#     model_id="meta-llama/Llama-3.1-8B-Instruct:novita",
#     stream=False,
# )

llm = GroqClient(
    model_id="openai/gpt-oss-20b",
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
            "pubsubname": "interview-pubsub",
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
def handle_answer(payload: dict = Body(...)):
    event = payload.get("data") or payload

    # Now validate manually or trust it
    interview_id = event.get("interview_id")
    turn_id = event.get("turn_id")
    question = event.get("question")
    answer = event.get("answer")
    timestamp = event.get("timestamp")

    # result = scorer.evaluate(question=question, answer=answer)

    # TODO: persist result (file/db/redis/state store)
    # TODO: optionally publish scoring_completed event

    return {"status": "processed"}