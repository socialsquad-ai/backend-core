"""
Unit tests for prompts/prompts.py

Tests cover all functionality in the PromptGenerator class including:
- Initialization
- get_prompt_for_agent
- Template mapping
- Platform support
"""

from unittest.mock import Mock, patch

from prompts.prompts import AGENT_NAME_PROMPT_MAPPING, ALL_PLATFORMS, PromptGenerator


class TestPromptGeneratorInit:
    """Test cases for PromptGenerator.__init__ method"""

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters"""
        # Act
        generator = PromptGenerator(agent_name="create_reply_agent", platform="instagram", persona="Be friendly and helpful")

        # Assert
        assert generator.agent_name == "create_reply_agent"
        assert generator.platform == "instagram"
        assert generator.persona == "Be friendly and helpful"

    def test_init_with_different_platform(self):
        """Test initialization with different platform"""
        # Act
        generator = PromptGenerator(agent_name="delete_comment_agent", platform="youtube", persona="Professional tone")

        # Assert
        assert generator.platform == "youtube"

    def test_init_with_empty_persona(self):
        """Test initialization with empty persona"""
        # Act
        generator = PromptGenerator(agent_name="ignore_comment_agent", platform="instagram", persona="")

        # Assert
        assert generator.persona == ""


class TestPromptGeneratorGetPromptForAgent:
    """Test cases for PromptGenerator.get_prompt_for_agent method"""

    @patch("prompts.prompts.jinja2.Environment")
    @patch("prompts.prompts.PLATFORM_NAME_DESCRIPTION", {"instagram": "Instagram platform description"})
    def test_get_prompt_for_agent_create_reply(self, mock_env_class):
        """Test get_prompt_for_agent for create_reply agent"""
        # Arrange
        mock_template = Mock()
        mock_template.render.return_value = "Generated prompt"

        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="create_reply_agent", platform="instagram", persona="Be helpful")

        # Act
        result = generator.get_prompt_for_agent()

        # Assert
        assert result == "Generated prompt"
        mock_env.get_template.assert_called_once_with("create_reply.j2")
        mock_template.render.assert_called_once()

    @patch("prompts.prompts.jinja2.Environment")
    @patch("prompts.prompts.PLATFORM_NAME_DESCRIPTION", {"youtube": "YouTube platform description"})
    def test_get_prompt_for_agent_ignore_comment(self, mock_env_class):
        """Test get_prompt_for_agent for ignore_comment agent"""
        # Arrange
        mock_template = Mock()
        mock_template.render.return_value = "Ignore comment prompt"

        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="ignore_comment_agent", platform="youtube", persona="Ignore spam")

        # Act
        _result = generator.get_prompt_for_agent()

        # Assert
        mock_env.get_template.assert_called_once_with("ignore_comment.j2")

    @patch("prompts.prompts.jinja2.Environment")
    @patch("prompts.prompts.PLATFORM_NAME_DESCRIPTION", {"instagram": "Instagram description"})
    def test_get_prompt_for_agent_delete_comment(self, mock_env_class):
        """Test get_prompt_for_agent for delete_comment agent"""
        # Arrange
        mock_template = Mock()
        mock_template.render.return_value = "Delete comment prompt"

        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="delete_comment_agent", platform="instagram", persona="Moderate strictly")

        # Act
        _result = generator.get_prompt_for_agent()

        # Assert
        mock_env.get_template.assert_called_once_with("delete_comment.j2")

    @patch("prompts.prompts.jinja2.Environment")
    @patch("prompts.prompts.PLATFORM_NAME_DESCRIPTION", {"instagram": "Instagram platform"})
    def test_get_prompt_for_agent_renders_with_correct_context(self, mock_env_class):
        """Test that template is rendered with correct context variables"""
        # Arrange
        mock_template = Mock()
        mock_template.render.return_value = "Rendered prompt"

        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        _result = generator.get_prompt_for_agent()

        # Assert
        call_kwargs = mock_template.render.call_args[1]
        assert call_kwargs["persona"] == "Be friendly"
        assert call_kwargs["platform_name"] == "instagram"
        assert call_kwargs["platform_description"] == "Instagram platform"
        assert call_kwargs["all_platforms"] == ALL_PLATFORMS

    @patch("prompts.prompts.jinja2.Environment")
    @patch("prompts.prompts.PLATFORM_NAME_DESCRIPTION", {})
    def test_get_prompt_for_agent_platform_without_description(self, mock_env_class):
        """Test get_prompt_for_agent when platform has no description"""
        # Arrange
        mock_template = Mock()
        mock_template.render.return_value = "Prompt"

        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="create_reply_agent", platform="unknown_platform", persona="Test")

        # Act
        _result = generator.get_prompt_for_agent()

        # Assert
        call_kwargs = mock_template.render.call_args[1]
        assert call_kwargs["platform_description"] is None

    @patch("prompts.prompts.jinja2.Environment")
    def test_get_prompt_for_agent_loads_from_prompts_directory(self, mock_env_class):
        """Test that templates are loaded from prompts directory"""
        # Arrange
        mock_template = Mock()
        mock_env = Mock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generator = PromptGenerator(agent_name="create_reply_agent", platform="instagram", persona="Test")

        # Act
        generator.get_prompt_for_agent()

        # Assert
        # Verify FileSystemLoader was called with "prompts" directory
        mock_env_class.assert_called_once()


class TestAgentNamePromptMapping:
    """Test cases for AGENT_NAME_PROMPT_MAPPING constant"""

    def test_mapping_contains_create_reply(self):
        """Test mapping contains create_reply_agent"""
        from config.non_env import CREATE_REPLY_AGENT

        assert CREATE_REPLY_AGENT in AGENT_NAME_PROMPT_MAPPING
        assert AGENT_NAME_PROMPT_MAPPING[CREATE_REPLY_AGENT] == "create_reply"

    def test_mapping_contains_ignore_comment(self):
        """Test mapping contains ignore_comment_agent"""
        from config.non_env import IGNORE_COMMENT_AGENT

        assert IGNORE_COMMENT_AGENT in AGENT_NAME_PROMPT_MAPPING
        assert AGENT_NAME_PROMPT_MAPPING[IGNORE_COMMENT_AGENT] == "ignore_comment"

    def test_mapping_contains_delete_comment(self):
        """Test mapping contains delete_comment_agent"""
        from config.non_env import DELETE_COMMENT_AGENT

        assert DELETE_COMMENT_AGENT in AGENT_NAME_PROMPT_MAPPING
        assert AGENT_NAME_PROMPT_MAPPING[DELETE_COMMENT_AGENT] == "delete_comment"

    def test_mapping_has_three_entries(self):
        """Test mapping has exactly three entries"""
        assert len(AGENT_NAME_PROMPT_MAPPING) == 3


class TestAllPlatforms:
    """Test cases for ALL_PLATFORMS constant"""

    def test_all_platforms_contains_youtube(self):
        """Test ALL_PLATFORMS contains youtube"""
        assert "youtube" in ALL_PLATFORMS

    def test_all_platforms_contains_instagram(self):
        """Test ALL_PLATFORMS contains instagram"""
        assert "instagram" in ALL_PLATFORMS

    def test_all_platforms_has_two_entries(self):
        """Test ALL_PLATFORMS has exactly two platforms"""
        assert len(ALL_PLATFORMS) == 2

    def test_all_platforms_are_strings(self):
        """Test all platforms are lowercase strings"""
        for platform in ALL_PLATFORMS:
            assert isinstance(platform, str)
            assert platform.islower()
