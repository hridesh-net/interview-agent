import torch
from collections import deque

from .src.models.vision_encoder import VisionEncoder
from .src.models.y_encoder import YEncoder
from .src.models.predictor import Predictor
from .src.models.query_encoder import QueryEncoder

def select_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

class VLJEPAModels:
    def __init__(self):
        self.device = select_device()
        print("[VL-JEPA] Using device:", self.device)

        self.vision = VisionEncoder(device=self.device)
        self.y_encoder = YEncoder()
        self.q_encoder = QueryEncoder()

        self.predictor = Predictor().to(self.device)
        self.predictor.load_state_dict(
            torch.load("predictor.pt", map_location=self.device)
        )
        self.predictor.eval()

        print("[VL-JEPA] Models loaded ✅")