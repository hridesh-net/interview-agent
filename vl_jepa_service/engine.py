import cv2
import torch
import torch.nn.functional as F

from vl_jepa_service.frames import get_frame_queue
from vl_jepa_service.models import VLJEPAModels
from vl_jepa_service.state import VLJEPAState
from vl_jepa_service.context import PerceptionContext, save_perception_state

OBJECTS = [
    "person", "laptop", "phone", "cup", "table",
    "chair", "keyboard", "screen", "book",
    "vanshika", "ujjwal", "shakti"
]

PROMPT = "What objects are visible?"

def describe_scene(current, previous, changed):
    if previous is None:
        return f"I see a {current}."
    if changed and current != previous:
        return f"A {current} has appeared in the scene."
    return f"I still see a {current}."

async def vl_jepa_loop(peer_id: str):
    models = VLJEPAModels()
    state = VLJEPAState()

    queue = get_frame_queue(peer_id)

    q_emb = models.q_encoder.encode([PROMPT]).to(models.device)
    object_embs = models.y_encoder.encode(OBJECTS).to(models.device)

    print(f"[VL-JEPA] Inference loop started for {peer_id}")

    while True:
        # ✅ CORRECT: dequeue from the per-peer queue
        frame = await queue.get()

        print(f"[VL-JEPA][{peer_id}] Dequeued frame:", frame.shape)

        # ----------------------------------
        # Resize frame to model resolution
        # ----------------------------------
        frame_resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_LINEAR)

        img_tensor = (
            torch.from_numpy(frame_resized)
            .permute(2, 0, 1)
            .unsqueeze(0)
            .float()
            .to(models.device) / 255.0
        )

        with torch.no_grad():
            sv = models.vision(img_tensor)
            sy_hat = models.predictor(sv, q_emb)

            state.embedding_buffer.append(sy_hat)

            if len(state.embedding_buffer) < 2:
                stable_emb = sy_hat
            else:
                stable_emb = torch.mean(
                    torch.stack(list(state.embedding_buffer)), dim=0
                )

            changed = False
            if state.last_embedding is not None:
                delta = 1 - F.cosine_similarity(
                    stable_emb, state.last_embedding
                )
                if delta.item() > state.CHANGE_THRESHOLD:
                    changed = True

            state.last_embedding = stable_emb.clone()

            sims = torch.matmul(
                F.normalize(stable_emb, dim=-1),
                F.normalize(object_embs, dim=-1).T
            )

            confidence = sims.max().item()
            best_idx = sims.argmax(dim=-1).item()
            current_label = OBJECTS[best_idx]

            if current_label != state.previous_label:
                changed = True

            sentence = describe_scene(
                current=current_label,
                previous=state.previous_label,
                changed=changed
            )

            state.previous_label = current_label

            save_perception_state(
                interview_id=peer_id,
                data={
                    "scene_description": sentence,
                    "object": current_label,
                    "confidence": round(confidence, 3),
                    "changed": True,
                }
            )

        print(
            f"[VL-JEPA][{peer_id}]",
            sentence,
            "| confidence:",
            f"{confidence:.2f}"
        )