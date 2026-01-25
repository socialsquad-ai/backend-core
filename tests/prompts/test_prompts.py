from unittest.mock import MagicMock, patch

from config.non_env import CREATE_REPLY_AGENT, DELETE_COMMENT_AGENT, IGNORE_COMMENT_AGENT
from prompts.prompts import AGENT_NAME_PROMPT_MAPPING, ALL_PLATFORMS, PromptGenerator


class TestAgentNamePromptMapping:
    def test_agent_name_prompt_mapping_exists(self):
        assert isinstance(AGENT_NAME_PROMPT_MAPPING, dict)

    def test_create_reply_agent_mapping(self):
        assert AGENT_NAME_PROMPT_MAPPING[CREATE_REPLY_AGENT] == "create_reply"

    def test_ignore_comment_agent_mapping(self):
        assert AGENT_NAME_PROMPT_MAPPING[IGNORE_COMMENT_AGENT] == "ignore_comment"

    def test_delete_comment_agent_mapping(self):
        assert AGENT_NAME_PROMPT_MAPPING[DELETE_COMMENT_AGENT] == "delete_comment"


class TestAllPlatforms:
    def test_all_platforms_is_list(self):
        assert isinstance(ALL_PLATFORMS, list)

    def test_all_platforms_contains_youtube(self):
        assert "youtube" in ALL_PLATFORMS

    def test_all_platforms_contains_instagram(self):
        assert "instagram" in ALL_PLATFORMS


class TestPromptGeneratorInit:
    def test_prompt_generator_initialization(self):
        generator = PromptGenerator("test_agent", "youtube", "test_persona")
        assert generator.agent_name == "test_agent"
        assert generator.platform == "youtube"
        assert generator.persona == "test_persona"

    def test_prompt_generator_stores_all_parameters(self):
        agent_name = CREATE_REPLY_AGENT
        platform = "instagram"
        persona = "friendly assistant"

        generator = PromptGenerator(agent_name, platform, persona)
        assert generator.agent_name == agent_name
        assert generator.platform == platform
        assert generator.persona == persona


class TestPromptGeneratorGetPromptForAgent:
    @patch("prompts.prompts._jinja_env")
    def test_get_prompt_for_agent_loads_correct_template(self, mock_env_instance):
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered prompt"
        mock_env_instance.get_template.return_value = mock_template

        generator = PromptGenerator(CREATE_REPLY_AGENT, "youtube", "test persona")
        result = generator.get_prompt_for_agent()

        mock_env_instance.get_template.assert_called_once_with("create_reply.j2")
        assert result == "rendered prompt"

    @patch("prompts.prompts._jinja_env")
    def test_get_prompt_for_agent_renders_with_correct_context(self, mock_env_instance):
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered prompt"
        mock_env_instance.get_template.return_value = mock_template

        persona = "friendly assistant"
        platform = "instagram"
        generator = PromptGenerator(IGNORE_COMMENT_AGENT, platform, persona)
        generator.get_prompt_for_agent()

        render_call_args = mock_template.render.call_args
        assert render_call_args is not None
        kwargs = render_call_args.kwargs

        assert kwargs["persona"] == persona
        assert kwargs["platform_name"] == platform
        assert "all_platforms" in kwargs
        assert "platform_description" in kwargs

    @patch("prompts.prompts._jinja_env")
    def test_get_prompt_for_agent_with_delete_comment_agent(self, mock_env_instance):
        mock_template = MagicMock()
        mock_template.render.return_value = "delete prompt"
        mock_env_instance.get_template.return_value = mock_template

        generator = PromptGenerator(DELETE_COMMENT_AGENT, "youtube", "test persona")
        result = generator.get_prompt_for_agent()

        mock_env_instance.get_template.assert_called_once_with("delete_comment.j2")
        assert result == "delete prompt"

    @patch("prompts.prompts._jinja_env")
    def test_get_prompt_for_agent_uses_file_system_loader(self, mock_env_instance):
        # This test verifies that we are using the mocked environment
        # In the original code, it checked strict jinja2 Environment instantiation,
        # but since we use a module-level instance, we verify interactions with that instance.

        mock_template = MagicMock()
        mock_template.render.return_value = "rendered"
        mock_env_instance.get_template.return_value = mock_template

        generator = PromptGenerator(CREATE_REPLY_AGENT, "youtube", "persona")
        generator.get_prompt_for_agent()

        # Verify get_template was called (which implies interaction with the env)
        assert mock_env_instance.get_template.called
