import os
import re
import yaml

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


class SkillRegistry:
    """
    Holds skill metadata and lazily loads instructions.
    """

    def __init__(self):
        self._skills = {}

    def load(self, skills_dir: str):
        for folder in os.listdir(skills_dir):
            path = os.path.join(skills_dir, folder, "SKILL.md")
            if not os.path.isfile(path):
                continue

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            meta = self._parse_frontmatter(text)
            if not meta or "name" not in meta:
                continue

            self._skills[meta["name"]] = {
                "name": meta["name"],
                "description": meta.get("description", ""),
                "path": path,
            }

    def list_metadata(self) -> list[dict]:
        return [
            {"name": s["name"], "description": s["description"]}
            for s in self._skills.values()
        ]

    def has(self, skill_name: str | None) -> bool:
        return skill_name in self._skills

    def load_instructions(self, skill_name: str) -> str:
        with open(self._skills[skill_name]["path"], "r", encoding="utf-8") as f:
            return f.read()

    def _parse_frontmatter(self, text: str):
        match = _FRONTMATTER.search(text)
        return yaml.safe_load(match.group(1)) if match else None
