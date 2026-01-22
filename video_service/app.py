from fastapi import APIRouter, Request, HTTPException
from video_service.peer import Peer
from video_service.signaling import apply_offer, create_answer
from aiortc.sdp import candidate_from_sdp

from video_service.runtime import ensure_vljepa_running



router = APIRouter()
peers: dict[str, Peer] = {}


@router.post("/webrtc/offer/{interview_id}")
async def webrtc_offer(interview_id: str, request: Request):
    offer = await request.json()

    if "sdp" not in offer or "type" not in offer:
        raise HTTPException(status_code=400, detail="Invalid SDP offer")

    # ---- Replace existing peer cleanly ----
    if interview_id in peers:
        await peers[interview_id].close()
        del peers[interview_id]

    # ---- Create peer bound to interview_id ----
    peer = Peer(peer_id=interview_id)
    peers[interview_id] = peer

    # ---- Start VL-JEPA loop ONCE per interview ----
    ensure_vljepa_running(interview_id)

    # ---- Apply SDP ----
    await apply_offer(peer.pc, offer)
    answer = await create_answer(peer.pc)

    return answer


@router.post("/webrtc/ice/{interview_id}")
async def webrtc_ice(interview_id: str, request: Request):
    data = await request.json()
    peer = peers.get(interview_id)

    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")

    if not data.get("candidate"):
        return {"status": "ignored"}  # end-of-candidates case

    candidate = candidate_from_sdp(data["candidate"])
    candidate.sdpMid = data.get("sdpMid")
    candidate.sdpMLineIndex = data.get("sdpMLineIndex")

    await peer.pc.addIceCandidate(candidate)
    return {"status": "ok"}
