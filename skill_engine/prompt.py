class PromptBuilder:
    """
    Builds prompts with strict Skill precedence.
    """

    def with_skill(self, skill_name: str, skill_text: str, user_input: str):
        system = f"""
You are an AI agent.

The Skill "{skill_name}" is ACTIVE.
Skill instructions OVERRIDE all other behavior.

--- BEGIN SKILL ---
{skill_text}
--- END SKILL ---
"""
        return system.strip(), user_input

    def without_skill(self, user_input: str):
        return "You are a helpful AI assistant.", user_input
