class StateStore:
    """
    Abstract persistence interface.
    """

    def save(self, state):
        raise NotImplementedError

    def load(self, interview_id):
        raise NotImplementedError

    def exists(self, interview_id) -> bool:
        raise NotImplementedError