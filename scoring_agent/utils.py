import json
import re
from typing import Any, Dict


class JSONExtractionError(Exception):
    pass


JSON_FENCE_RE = re.compile(
    r"```json\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract the first valid JSON object from LLM output.
    Supports fenced ```json blocks and inline JSON.
    """

    # 1️⃣ Prefer fenced ```json blocks
    fence_match = JSON_FENCE_RE.search(text)
    if fence_match:
        candidate = fence_match.group(1)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # fall through

    # 2️⃣ Fallback: brace-balanced scan
    start = text.find("{")
    if start == -1:
        raise JSONExtractionError("No JSON object found in text.")

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    break

    raise JSONExtractionError("Failed to extract valid JSON object.")