# api/ws.py
from fastapi import FastAPI, WebSocket, Request
from interview_agent.runtime import InterviewRuntime
from interview_agent.events import RuntimeEvent

from interview_agent.agent import InterviewAgent
from interview_agent.state_store_file import FileStateStore
from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient
from llm.groq_client import GroqClient
from fastapi.middleware.cors import CORSMiddleware
from video_service.app import router as webrtc_router
# from video_service.webrtc import handle_offer


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten later
    allow_credentials=True,
    allow_methods=["*"],          # includes OPTIONS
    allow_headers=["*"],
)

app.include_router(webrtc_router)

# ---- Boot dependencies ONCE ----
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
state_store = FileStateStore()

agent = InterviewAgent(
    skill_engine=skill_engine,
    state_store=state_store,
)

runtime = InterviewRuntime(agent, state_store)

@app.post("/interview")
def create_interview(payload: dict):
    jd_text = payload.get("jd")
    if not jd_text:
        raise ValueError("JD is required")

    state = agent.start(jd_text)

    return {
        "interview_id": state.interview_id,
        "status": state.status,
    }


# @app.websocket("/ws/interview/{session_id}")
# async def interview_ws(ws: WebSocket, session_id: str):
#     await ws.accept()
    
#     real_interview_id: str | None = None

#     while True:
#         data = await ws.receive_json()
        
#         interview_id = real_interview_id

#         event = RuntimeEvent.create(
#             interview_id=interview_id,
#             type=data["type"],
#             payload=data.get("payload", {}),
#             source="client",
#         )

#         response = runtime.handle_event(event)

#         if response:
#             if data["type"] == "interview.start":
#                 real_interview_id = response["interview_id"]
#                 print(f"Started interview session: {real_interview_id}")

#             await ws.send_json(response)

@app.websocket("/ws/interview/{interview_id}")
async def interview_ws(ws: WebSocket, interview_id: str):
    await ws.accept()

    if not state_store.exists(interview_id):
        await ws.close(code=4001)
        return

    while True:
        data = await ws.receive_json()

        event = RuntimeEvent.create(
            interview_id=interview_id,
            type=data["type"],
            payload=data.get("payload", {}),
            source="client",
        )

        response = runtime.handle_event(event)

        if response:
            await ws.send_json(response)


# @app.post("/webrtc/offer")
# async def webrtc_offer(request: Request):
#     offer = await request.json()
#     answer = await handle_offer(offer)
#     return answer