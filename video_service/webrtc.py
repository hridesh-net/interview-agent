from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole

pcs = set()

async def handle_offer(offer_sdp: dict):
    pc = RTCPeerConnection()
    pcs.add(pc)

    recorder = MediaBlackhole()

    @pc.on("track")
    async def on_track(track):
        if track.kind == "video":
            await recorder.start()
            recorder.addTrack(track)

    offer = RTCSessionDescription(
        sdp=offer_sdp["sdp"],
        type=offer_sdp["type"]
    )

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }