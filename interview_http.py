from fastapi import FastAPI
from pydantic import BaseModel

from interview_agent.agent import InterviewAgent
from interview_agent.state_store_file import FileStateStore
from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient
from llm.groq_client import GroqClient

app = FastAPI()

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
store = FileStateStore()
agent = InterviewAgent(skill_engine, store)

class StartReq(BaseModel):
    jd_text: str

@app.post("/start")
def start_interview(req: StartReq):
    state = agent.start(req.jd_text)
    return state.to_dict()

class AnswerReq(BaseModel):
    interview_id: str
    answer: str

@app.post("/answer")
def answer_question(req: AnswerReq):
    state = agent.submit_answer(req.interview_id, req.answer)
    return state.to_dict()

@app.get("/state/{interview_id}")
def get_state(interview_id: str):
    return store.load(interview_id).to_dict()