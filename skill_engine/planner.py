import json


class SkillPlanner:
    """
    Uses LLM to decide whether a skill is required.
    Metadata-only planning.
    """

    def __init__(self, llm):
        self.llm = llm

    def decide(self, user_input: str, skills: list[dict]) -> dict:
        skill_list = "\n".join(
            f"- {s['name']}: {s['description']}"
            for s in skills
        )

        system = (
            "You are an AI agent planner.\n"
            "Decide whether a Skill should be used.\n"
            "Respond ONLY with valid JSON."
        )

        user = f"""
User input:
{user_input}

Available Skills:
{skill_list}

Return JSON exactly in this format:
{{
  "use_skill": true | false,
  "skill_name": "<skill-name-or-null>",
  "reason": "<short reason>"
}}
"""

        raw = self.llm.invoke(system, user)
        return self._safe_parse(raw)

    def _safe_parse(self, raw: str) -> dict:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            data = json.loads(raw[start:end])
        except Exception:
            return {
                "use_skill": False,
                "skill_name": None,
                "reason": "planner_parse_failed",
            }

        if not isinstance(data.get("use_skill"), bool):
            data["use_skill"] = False

        if not data["use_skill"]:
            data["skill_name"] = None

        return data
