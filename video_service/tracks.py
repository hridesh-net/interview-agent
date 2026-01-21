import asyncio
from video_service.frames import frame_to_ndarray

class VideoTrackConsumer:
    def __init__(self, peer_id: str):
        self.peer_id = peer_id

    async def consume(self, track):
        print(f"[{self.peer_id}] Video track started")

        while True:
            try:
                frame = await track.recv()
            except Exception as e:
                print(f"[{self.peer_id}] Track ended: {e}")
                break

            img = frame_to_ndarray(frame)

            # PROOF THAT VIDEO IS RECEIVED
            print(f"[{self.peer_id}] Frame received: {img.shape}")