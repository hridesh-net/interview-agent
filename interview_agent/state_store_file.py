import json
from pathlib import Path
from interview_agent.state import InterviewState


class FileStateStore:
    def __init__(self, base_dir="interview_states"):
        self.base = Path(base_dir)
        self.base.mkdir(exist_ok=True)

    def _path(self, interview_id):
        return self.base / f"{interview_id}.json"

    def save(self, state: InterviewState):
        tmp_path = self._path(state.interview_id).with_suffix(".tmp")

        with open(tmp_path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

        # atomic replace
        tmp_path.replace(self._path(state.interview_id))

    def load(self, interview_id) -> InterviewState:
        with open(self._path(interview_id)) as f:
            data = json.load(f)
        return InterviewState.from_dict(data)

    def exists(self, interview_id) -> bool:
        return self._path(interview_id).exists()
