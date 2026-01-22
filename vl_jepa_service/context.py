from typing import Dict, Optional
import threading

class PerceptionContext:
    """
    Thread-safe store for latest VL-JEPA perception results.
    """

    _lock = threading.Lock()
    _state: Dict[str, object] = {}

    @classmethod
    def update(cls, *, interview_id: str, data: Dict[str, object]):
        with cls._lock:
            cls._state[interview_id] = data

    @classmethod
    def get(cls, *, interview_id: Optional[str] = None) -> Dict[str, object]:
        with cls._lock:
            if interview_id:
                return cls._state.get(interview_id, {})
            return dict(cls._state)

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("state/perception")

def save_perception_state(*, interview_id: str, data: dict):
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "interview_id": interview_id,
        "type": "vision",
        **data,
        "updated_at": datetime.utcnow().isoformat(),
        "version": 1,
    }

    path = BASE_DIR / f"perception_{interview_id}.json"
    path.write_text(json.dumps(payload, indent=2))


def load_perception_state(*, interview_id: str) -> dict | None:
    path = Path("state/perception") / f"perception_{interview_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())