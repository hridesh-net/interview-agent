
import asyncio
from vl_jepa_service.engine import vl_jepa_loop

_running = {}

def ensure_vljepa_running(interview_id: str):
    if interview_id in _running:
        return

    task = asyncio.create_task(vl_jepa_loop(interview_id))
    _running[interview_id] = task