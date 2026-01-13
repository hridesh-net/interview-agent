import os
from xml.parsers.expat import model
from openai import OpenAI


class HuggingFaceClient:
    """
    Hugging Face Router client (OpenAI-compatible).
    Works with free / routed models like Groq, OSS, etc.
    """

    def __init__(
        self,
        model_id: str,
        api_key: str | None = None,
        base_url: str = "https://router.huggingface.co/v1",
        temperature: float = 0.2,
        max_tokens: int = 512,
        stream: bool = False,
    ):
        self.model = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key or os.getenv("HF_API_KEY"),
        )

        if not self.client.api_key:
            raise ValueError("HF_API_KEY must be set for Hugging Face Router")

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self.stream:
            return self._invoke_stream(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    def _invoke_stream(self, messages) -> str:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        output = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                output.append(delta)

        return "".join(output)