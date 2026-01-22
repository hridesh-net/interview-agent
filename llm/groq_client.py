import os
from openai import OpenAI


class GroqClient:
    """
    Groq LLM client (OpenAI-compatible).

    Designed to be a drop-in replacement for HuggingFaceClient
    in SkillEngine / InterviewAgent pipelines.
    """

    def __init__(
        self,
        model_id: str = "openai/gpt-oss-20b",
        api_key: str | None = None,
        base_url: str = "https://api.groq.com/openai/v1",
        temperature: float = 0.2,
        max_tokens: int = 1000,
        stream: bool = False,
    ):
        self.model = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key or os.getenv("GROQ_API_KEY"),
        )

        if not self.client.api_key:
            raise ValueError("GROQ_API_KEY must be set for GroqClient")

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self.stream:
            return self._invoke_stream(messages)
        
        print("___MESSAGES___")
        print(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        print("___RESPONSE___")
        print(response.choices[0].message.content)

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