import os
import json
import boto3


class BedrockClient:
    """
    Bedrock LLM wrapper compatible with bedrock-skill-engine.
    """

    def __init__(self, model_id: str = None, region: str = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        if not self.model_id:
            raise ValueError(
                "BEDROCK_MODEL_ID must be set "
                "(e.g. anthropic.claude-3-sonnet-20240229-v1:0)"
            )

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region
        )

    def invoke(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.1,
    ) -> str:
        """
        Invoke Bedrock Claude-style models using system + user prompts.
        """

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt}
                    ],
                }
            ],
        }

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body).encode("utf-8"),
        )

        result = json.loads(response["body"].read())

        # Claude response extraction
        return result["content"][0]["text"]