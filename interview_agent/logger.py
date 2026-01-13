import json
import logging
import sys
from datetime import datetime


class JsonLogger:
    def __init__(self, name="interview-agent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))

        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log(self, event: str, **data):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **data,
        }
        self.logger.info(json.dumps(payload))