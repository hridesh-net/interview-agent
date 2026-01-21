class PromptBuilder:
    """
    Builds prompts with strict Skill precedence.
    """

    def with_skill(self, skill_name: str, skill_text: str, user_input: str):
        system = f"""
You have a Skill "{skill_name}".

{skill_text}
"""
        return system.strip(), user_input

    def without_skill(self, user_input: str):
        return "You are a helpful AI assistant.", user_input
