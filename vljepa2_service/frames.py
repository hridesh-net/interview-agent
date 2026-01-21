from collections import deque
from typing import Dict
import numpy as np
import asyncio

_CLIP_BUFFERS: Dict[str, deque] = {}

_FRAME_QUEUES: Dict[str, asyncio.Queue] = {}

def get_frame_queue(peer_id: str) -> asyncio.Queue:
    """
    Returns a per-peer asyncio queue for raw frames.
    """
    if peer_id not in _FRAME_QUEUES:
        _FRAME_QUEUES[peer_id] = asyncio.Queue(maxsize=60)
    return _FRAME_QUEUES[peer_id]

def get_clip_buffer(peer_id: str, clip_length: int):
    if peer_id not in _CLIP_BUFFERS:
        _CLIP_BUFFERS[peer_id] = deque(maxlen=clip_length)
    return _CLIP_BUFFERS[peer_id]
