import json
import re
from typing import Any, Dict, List


class JSONExtractionError(Exception):
    pass


JSON_FENCE_RE = re.compile(
    r"```json\s*(.*?)\s*```",
    re.DOTALL | re.IGNORECASE,
)


def _find_all_json_candidates(text: str) -> List[str]:
    """
    Find all brace-balanced JSON-like substrings.
    """
    candidates = []
    stack = []
    start_idx = None

    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                start_idx = i
            stack.append(ch)
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidates.append(text[start_idx : i + 1])
                    start_idx = None

    return candidates


def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract the first valid JSON object from LLM output.
    Supports:
    - ```json fenced blocks
    - Multiple inline JSON objects
    """

    # 1️⃣ Try fenced blocks first
    fence_matches = JSON_FENCE_RE.findall(text)
    for block in fence_matches:
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue

    # 2️⃣ Extract all brace-balanced candidates
    candidates = _find_all_json_candidates(text)

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise JSONExtractionError("No valid JSON object found in model output.")