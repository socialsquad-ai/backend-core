from typing import Optional

from pydantic_ai.agent import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

from config.non_env import (
    CREATE_REPLY_AGENT,
    GEMINI_MAX_TOKENS,
    GEMINI_MODEL_NAME,
    GEMINI_TEMPERATURE,
    GEMINI_TIMEOUT,
    GEMINI_TOP_P,
    USER_PROMPT,
)
from prompts.prompts import PromptGenerator


class SSQAgent:
    # Class-level cache for the model to avoid re-instantiation overhead
    _model_instance: Optional[GoogleModel] = None

    @classmethod
    def _get_model(cls) -> GoogleModel:
        if cls._model_instance is None:
            cls._model_instance = GoogleModel(
                model_name=GEMINI_MODEL_NAME,
                settings=GoogleModelSettings(
                    max_tokens=GEMINI_MAX_TOKENS,
                    temperature=GEMINI_TEMPERATURE,
                    top_p=GEMINI_TOP_P,
                    timeout=GEMINI_TIMEOUT,
                ),
            )
        return cls._model_instance

    def __init__(self, agent_name: str, platform: str, persona: str):
        self.agent_name = agent_name
        self.system_prompt = PromptGenerator(agent_name, platform, persona).get_prompt_for_agent()
        self.agent = Agent(
            model=self._get_model(),
            system_prompt=self.system_prompt,
            output_type=str if agent_name == CREATE_REPLY_AGENT else bool,
        )

    async def generate_response(self, user_comment: str):
        result = await self.agent.run(f'{USER_PROMPT[self.agent_name]}: "{user_comment}"')

        # PydanticAI v0.7+ uses .data, older might use .output
        output = getattr(result, "data", getattr(result, "output", None))

        if isinstance(output, str):
            output = output.strip().strip('"').strip("'")

        return output
