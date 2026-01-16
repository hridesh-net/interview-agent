# interview_runtime/runtime_state.py
from dataclasses import dataclass, field
from typing import Dict, Any
import time


@dataclass
class RuntimeState:
    interview_id: str
    last_activity_ms: int = field(default_factory=lambda: int(time.time() * 1000))
    partial_answer: str = ""
    video_signals: Dict[str, Any] = field(default_factory=dict)
    audio_buffer: list[str] = field(default_factory=list)
