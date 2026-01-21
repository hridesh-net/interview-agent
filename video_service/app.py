from fastapi import APIRouter, Request
from video_service.peer import Peer
from video_service.signaling import apply_offer, create_answer

router = APIRouter()
peers: dict[str, Peer] = {}


@router.post("/webrtc/offer/{peer_id}")
async def webrtc_offer(peer_id: str, request: Request):
    offer = await request.json()

    # Create peer
    peer = Peer(peer_id)
    peers[peer_id] = peer

    # Apply offer & create answer
    await apply_offer(peer.pc, offer)
    answer = await create_answer(peer.pc)

    return answer