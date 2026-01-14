from dapr.clients import DaprClient
import json


def publish_answer_event(event: dict):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="interview-pubsub",
            topic_name="answer_submitted",
            data=json.dumps(event),
            data_content_type="application/json",
        )