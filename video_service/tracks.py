import asyncio
import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame

from vl_jepa_service.frames import get_frame_queue

class VideoTrackConsumer:
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        self.queue = get_frame_queue(peer_id)

    async def consume(self, track: VideoStreamTrack):
        while True:
            frame: VideoFrame = await track.recv()

            img = frame.to_ndarray(format="bgr24")

            # Non-blocking enqueue (drop if slow)
            if self.queue.full():
                try:
                    _ = self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass

            await self.queue.put(img)

            print(f"[{self.peer_id}] Frame enqueued:", img.shape)