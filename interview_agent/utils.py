import json
import re


_JSON_BLOCK = re.compile(
    r"```(?:json)?\s*(\{.*?\})\s*```",
    re.DOTALL
)


def extract_json(raw: str) -> dict:
    """
    Extract JSON object from LLM output.
    Supports fenced and unfenced JSON.
    """
    if not isinstance(raw, str):
        raise TypeError("Raw output must be a string")

    # 1️⃣ Try fenced ```json
    match = _JSON_BLOCK.search(raw)
    if match:
        return json.loads(match.group(1))

    # 2️⃣ Try first {...} block
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end != -1:
        return json.loads(raw[start:end])

    raise ValueError("No valid JSON found in skill output")