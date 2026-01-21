import json
from pathlib import Path
from scoring_agent.state import ScoringState


class FileStateStore:
    def __init__(self, base_dir="scoring_states"):
        self.base = Path(base_dir)
        self.base.mkdir(exist_ok=True)

    def _path(self, interview_id: str):
        return self.base / f"{interview_id}.json"

    def exists(self, interview_id: str) -> bool:
        return self._path(interview_id).exists()

    def load(self, interview_id: str) -> ScoringState:
        with open(self._path(interview_id)) as f:
            data = json.load(f)
        return ScoringState.from_dict(data)

    def save(self, state: ScoringState):
        tmp = self._path(state.interview_id).with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(state.to_dict(), f, indent=2)
        tmp.replace(self._path(state.interview_id))