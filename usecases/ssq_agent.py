from pydantic_ai.agent import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

from config.non_env import CREATE_REPLY_AGENT, USER_PROMPT
from prompts.prompts import PromptGenerator


class SSQAgent:
    def __init__(self, agent_name: str, platform: str, persona: str):
        self.agent_name = agent_name
        self.system_prompt = PromptGenerator(agent_name, platform, persona).get_prompt_for_agent()
        self.agent = Agent(
            model=GoogleModel(
                model_name="gemini-2.5-flash-lite",
                settings=GoogleModelSettings(
                    max_tokens=100,
                    temperature=0.9,
                    top_p=0.5,
                    timeout=15,
                ),
            ),
            system_prompt=self.system_prompt,
            output_type=str if agent_name == CREATE_REPLY_AGENT else bool,
        )

    async def generate_response(self, user_comment: str):
        result = await self.agent.run(f'{USER_PROMPT[self.agent_name]}: "{user_comment}"')
        if isinstance(result.output, str) and result.output.startswith('"') and result.output.endswith('"'):
            result.output = result.output[1:-1]

        return result.output
