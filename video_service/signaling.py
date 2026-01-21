from aiortc import RTCSessionDescription

async def apply_offer(pc, offer: dict):
    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=offer["sdp"],
            type=offer["type"]
        )
    )

async def create_answer(pc):
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }