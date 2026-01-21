import asyncio
from aiortc import RTCPeerConnection, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaBlackhole
from video_service.tracks import VideoTrackConsumer

from vl_jepa_service.engine import vl_jepa_loop

class Peer:
    def __init__(self, peer_id: str):
        self.peer_id = peer_id
        self.pc = RTCPeerConnection(
            RTCConfiguration(
                iceServers=[
                    RTCIceServer(urls="stun:stun.l.google.com:19302")
                ]
            )
        )

        self.media_sink = MediaBlackhole()
        self.video_consumer = VideoTrackConsumer(peer_id)
        
        asyncio.create_task(vl_jepa_loop(peer_id))
        
        # USE_VJEPA2 = False
        
        # if USE_VJEPA2:
        #     from vljepa2_service.engine import vljepa2_loop
        #     asyncio.create_task(vljepa2_loop(peer_id))
        # else:
        #     from vl_jepa_service.engine import vl_jepa_loop
        #     asyncio.create_task(vl_jepa_loop(peer_id))

        @self.pc.on("track")
        def on_track(track):
            print(f"[{self.peer_id}] Track received:", track.kind)

            if track.kind == "video":
                asyncio.create_task(
                    self.video_consumer.consume(track)
                )

            if track.kind == "audio":
                self.media_sink.addTrack(track)

        @self.pc.on("connectionstatechange")
        async def on_state_change():
            print(
                f"[{self.peer_id}] Connection state:",
                self.pc.connectionState
            )

    async def close(self):
        await self.media_sink.stop()
        await self.pc.close()