from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaBlackhole
from video_service.tracks import VideoTrackConsumer

class Peer:
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        self.pc = RTCPeerConnection()
        self.media_sink = MediaBlackhole()

        self.video_consumer = VideoTrackConsumer(peer_id)

        @self.pc.on("track")
        def on_track(track):
            if track.kind == "video":
                self.pc._loop.create_task(
                    self.video_consumer.consume(track)
                )

            if track.kind == "audio":
                self.media_sink.addTrack(track)

        @self.pc.on("connectionstatechange")
        async def on_state_change():
            print(f"[{self.peer_id}] Connection state: {self.pc.connectionState}")

    async def close(self):
        await self.media_sink.stop()
        await self.pc.close()