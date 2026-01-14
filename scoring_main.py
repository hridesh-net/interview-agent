from scoring_agent.agent import ScoringAgent
from scoring_agent.executor import ScoringExecutor
from scoring_agent.state_store_file import FileStateStore
from scoring_agent.logger import get_logger

from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient


def main():
    logger = get_logger()

    registry = SkillRegistry()
    registry.load("./skills")

    llm = HuggingFaceClient(
        model_id="meta-llama/Llama-3.1-8B-Instruct:novita",
        stream=False,
    )

    skill_engine = SkillEngine(registry, llm)
    executor = ScoringExecutor(skill_engine)
    store = FileStateStore()

    agent = ScoringAgent(executor, store, logger)

    # Simulated event from Interview Agent
    event = {
        "event": "answer_submitted",
        "interview_id": "demo-interview-1",
        "turn_id": 1,
        "question": "Explain abstraction in Java",
        "answer": "Abstraction hides implementation details using interfaces.",
    }

    agent.handle_answer_event(event)

    print("✅ Scoring Agent executed successfully")


if __name__ == "__main__":
    main()