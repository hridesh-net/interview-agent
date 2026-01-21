from .utils import extract_json

class ScoringExecutor:
    def __init__(self, skill_engine, logger=None):
        self.skills = skill_engine
        self.logger = logger

    def evaluate(self, question: str, answer: str):
        intent = self.skills.run_skill(
            skill="answer_intent_evaluator",
            user_input={
                "question": question,
                "answer": answer,
            },
        )

        score_raw = self.skills.run_skill(
            skill="score_calculator",
            user_input={
                "question": question,
                "answer": answer,
                "intent_analysis": intent,
            },
        )

        score = extract_json(score_raw)

        if self.logger:
            self.logger.log(
                event="scoring_completed",
                intent=intent,
                score=score,
            )

        return {
            "intent": intent,
            "score": score,
        }