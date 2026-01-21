from collections import deque

class VLJEPAState:
    def __init__(self):
        self.embedding_buffer = deque(maxlen=5)
        self.last_embedding = None
        self.previous_label = None

        self.CHANGE_THRESHOLD = 0.15