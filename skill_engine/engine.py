import json

from skill_engine.planner import SkillPlanner
from skill_engine.prompt import PromptBuilder
from skill_engine.executor import Executor


def _normalize_user_input(user_input):
    if isinstance(user_input, str):
        return user_input
    return json.dumps(user_input, indent=2)

class SkillEngine:
    """
    General-purpose Skill Engine (provider-agnostic).
    """

    def __init__(self, registry, llm):
        self.registry = registry
        self.planner = SkillPlanner(llm)
        self.prompts = PromptBuilder()
        self.executor = Executor(llm)

    def run(self, user_input: str):
        decision = self.planner.decide(
            user_input,
            self.registry.list_metadata(),
        )

        skill_name = decision.get("skill_name")
        if not decision.get("use_skill") or not self.registry.has(skill_name):
            system, user = self.prompts.without_skill(user_input)
            return self.executor.run(system, user)

        instructions = self.registry.load_instructions(skill_name)
        system, user = self.prompts.with_skill(
            skill_name,
            instructions,
            user_input,
        )

        return self.executor.run(system, user)

    def run_skill(self, *, skill: str, user_input):
        """
        Deterministically execute a specific skill.
        Used by production agents.
        """
        print("Executing skill directly:", skill)
        print("--------------------------------")
        print("User input:", user_input)
        print("Available skills:", self.registry.list_metadata())
        instructions = self.registry.load_instructions(skill)
        
        normalized_input = _normalize_user_input(user_input)

        # try 
        system, user = self.prompts.with_skill(
            skill,
            instructions,
            normalized_input
        )

        return self.executor.run(system, user)
