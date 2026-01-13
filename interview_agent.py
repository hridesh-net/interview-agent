import sys
from interview_agent.agent import InterviewAgent
from interview_agent.state_store_file import FileStateStore

from skill_engine import SkillEngine, SkillRegistry
from llm.huggingface_client import HuggingFaceClient


def main():
    print("\n=== Interview Agent ===\n")

    # -----------------------------
    # Setup dependencies
    # -----------------------------
    registry = SkillRegistry()
    registry.load("./skills")

    llm = HuggingFaceClient(
        model_id="meta-llama/Llama-3.1-8B-Instruct:novita",
        stream=False,
    )

    skill_engine = SkillEngine(registry, llm)
    state_store = FileStateStore()

    agent = InterviewAgent(
        skill_engine=skill_engine,
        state_store=state_store,
    )

    # -----------------------------
    # Start or Resume
    # -----------------------------
    interview_id = None

    if len(sys.argv) > 1:
        interview_id = sys.argv[1]

    if interview_id:
        state = agent.start_or_resume(interview_id=interview_id)
        print(f"🔁 Resumed interview: {state.interview_id}\n")
    else:
        print("Paste the Job Description (end with ENTER twice):\n")
        jd_lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            jd_lines.append(line)

        jd_text = "\n".join(jd_lines)

        state = agent.start_or_resume(jd_text=jd_text)
        print(f"\n🆕 Interview started: {state.interview_id}\n")

    # -----------------------------
    # Interview Loop
    # -----------------------------
    while state.status == "running":
        q = state.questions[state.current_index]["question"]

        print(f"\n🧑‍💼 Interviewer:\n{q}\n")
        answer = input("🧑‍💻 Candidate: ")

        state = agent.submit_answer(
            interview_id=state.interview_id,
            answer=answer
        )

    # -----------------------------
    # Final Results
    # -----------------------------
    print("\n✅ Interview Completed\n")
    print(f"Interview ID: {state.interview_id}")
    print(f"Total Questions: {len(state.history)}")

    avg_intent = round(
        sum(h.score["intent_score"] for h in state.history) / len(state.history),
        2
    )

    avg_content = round(
        sum(h.score["content_score"] for h in state.history) / len(state.history),
        2
    )

    print(f"Avg Intent Score: {avg_intent}")
    print(f"Avg Content Score: {avg_content}")


if __name__ == "__main__":
    main()