# interview_runtime/events.py
from dataclasses import dataclass
from typing import Any, Dict
import time
import uuid


@dataclass
class RuntimeEvent:
    event_id: str
    interview_id: str
    type: str
    payload: Dict[str, Any]
    timestamp_ms: int
    source: str

    @staticmethod
    def create(interview_id, type, payload, source):
        return RuntimeEvent(
            event_id=str(uuid.uuid4()),
            interview_id=interview_id,
            type=type,
            payload=payload,
            timestamp_ms=int(time.time() * 1000),
            source=source,
        )