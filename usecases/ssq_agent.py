from pydantic_ai.models.google import GoogleModelSettings, GoogleModel
from pydantic_ai.agent import Agent
from config.non_env import CREATE_REPLY_AGENT
from prompts.prompts import PromptGenerator
from config.non_env import USER_PROMPT


class SSQAgent:
    def __init__(self, agent_name: str, platform: str, persona: str):
        self.agent_name = agent_name
        self.agent = Agent(
            model=GoogleModel(
                model="gemini-2.5-flash-lite",
                settings=GoogleModelSettings(
                    max_tokens=100,
                    temperature=0.9,
                    top_p=0.5,
                    timeout=15,
                ),
            ),
            system_prompt=PromptGenerator(
                agent_name, platform, persona
            ).get_prompt_for_agent(),
            output_type=str if agent_name == CREATE_REPLY_AGENT else bool,
        )

    async def generate_response(self, user_comment: str):
        return await self.agent.run_sync(
            f'{USER_PROMPT[self.agent_name]}: "{user_comment}"'
        ).output
