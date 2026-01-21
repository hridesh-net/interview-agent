import asyncio
from typing import Dict

# One queue per peer
FRAME_QUEUES: Dict[str, asyncio.Queue] = {}

def get_frame_queue(peer_id: str) -> asyncio.Queue:
    if peer_id not in FRAME_QUEUES:
        FRAME_QUEUES[peer_id] = asyncio.Queue(maxsize=2)  # backpressure
    return FRAME_QUEUES[peer_id]