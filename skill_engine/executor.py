class Executor:
    """
    Executes prompts using the provided LLM client.
    """

    def __init__(self, llm):
        self.llm = llm

    def run(self, system_prompt: str, user_prompt: str) -> str:
        return self.llm.invoke(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )