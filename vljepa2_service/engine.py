import torch
from .models import VJepa2Models
from .frames import get_clip_buffer
from .state import VJepa2State
from .config import CLIP_LENGTH
from vljepa2_service.frames import get_frame_queue

async def vljepa2_loop(peer_id: str):
    models = VJepa2Models()
    state = VJepa2State()

    frame_queue = get_frame_queue(peer_id)
    clip_buffer = get_clip_buffer(peer_id, CLIP_LENGTH)

    print(f"[VJEPA2] Inference loop started for {peer_id}")

    while True:
        frame = await frame_queue.get()
        clip_buffer.append(frame)

        if len(clip_buffer) < CLIP_LENGTH:
            continue

        clip = list(clip_buffer)

        inputs = models.processor(
            clip, return_tensors="pt"
        ).to(models.device)

        with torch.no_grad():
            video_emb = models.model.get_vision_features(**inputs)

        state.last_embedding = video_emb

        print(
            f"[VJEPA2][{peer_id}] Clip processed | shape={tuple(video_emb.shape)}"
        )