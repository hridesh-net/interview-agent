from scoring_agent.state import ScoringState, AnswerScore
from scoring_agent.events import AnswerSubmittedEvent


class ScoringAgent:
    def __init__(self, executor, state_store, logger=None):
        self.executor = executor
        self.store = state_store
        self.logger = logger

    def handle_answer_event(self, raw_event: dict):
        event = AnswerSubmittedEvent.from_dict(raw_event)

        if self.logger:
            self.logger.info(
                f"Scoring answer | interview={event.interview_id} turn={event.turn_id}"
            )

        if self.store.exists(event.interview_id):
            state = self.store.load(event.interview_id)
        else:
            state = ScoringState(event.interview_id, scores={})

        _, score = self.executor.evaluate(
            question=event.question,
            answer=event.answer,
        )

        state.scores[event.turn_id] = AnswerScore(
            intent_score=score["intent_score"],
            content_score=score["content_score"],
            feedforward=score["feedforward"],
        )

        self.store.save(state)

        if self.logger:
            self.logger.info(
                f"Score saved | interview={event.interview_id} turn={event.turn_id}"
            )

        return state