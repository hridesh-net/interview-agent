import torch
from transformers import AutoVideoProcessor, AutoModel
from .config import MODEL_NAME

class VJepa2Models:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"

        print("[VJEP A2] Using device:", self.device)

        self.processor = AutoVideoProcessor.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()

        print("[VJEP A2] Model loaded ✅")