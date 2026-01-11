import jinja2

from config.non_env import (
    CREATE_REPLY_AGENT,
    DELETE_COMMENT_AGENT,
    IGNORE_COMMENT_AGENT,
    PLATFORM_NAME_DESCRIPTION,
)

AGENT_NAME_PROMPT_MAPPING = {
    CREATE_REPLY_AGENT: "create_reply",
    IGNORE_COMMENT_AGENT: "ignore_comment",
    DELETE_COMMENT_AGENT: "delete_comment",
}

# Current supported platforms
ALL_PLATFORMS = ["youtube", "instagram"]

_jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("prompts"))


class PromptGenerator:
    def __init__(self, agent_name: str, platform: str, persona: str):
        self.agent_name = agent_name
        self.platform = platform
        self.persona = persona

    def get_prompt_for_agent(self):
        template = _jinja_env.get_template(f"{AGENT_NAME_PROMPT_MAPPING[self.agent_name]}.j2")

        return template.render(
            all_platforms=ALL_PLATFORMS,
            persona=self.persona,
            platform_name=self.platform,
            platform_description=PLATFORM_NAME_DESCRIPTION.get(self.platform),
        )
