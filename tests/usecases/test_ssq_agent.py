"""
Unit tests for usecases/ssq_agent.py

Tests cover all methods in the SSQAgent class including:
- __init__
- generate_response
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from usecases.ssq_agent import SSQAgent


class TestSSQAgentInit:
    """Test cases for SSQAgent.__init__ method"""

    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_init_creates_agent_with_correct_parameters(self, mock_prompt_gen, mock_google_model, mock_agent):
        """Test initialization creates agent with correct parameters"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test system prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        # Act
        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Assert
        assert agent.agent_name == "create_reply_agent"
        assert agent.system_prompt == "Test system prompt"
        mock_prompt_gen.assert_called_once_with("create_reply_agent", "instagram", "Be friendly")
        mock_agent.assert_called_once()

    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_init_configures_google_model_correctly(self, mock_prompt_gen, mock_google_model_class, mock_agent):
        """Test initialization configures Google model with correct settings"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        # Act
        _agent = SSQAgent(agent_name="delete_comment_agent", platform="youtube", persona="Strict moderation")

        # Assert
        mock_google_model_class.assert_called_once()
        call_kwargs = mock_google_model_class.call_args[1]
        assert call_kwargs["model_name"] == "gemini-2.5-flash-lite"

    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.GoogleModelSettings")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_init_sets_google_model_settings(self, mock_prompt_gen, mock_settings_class, mock_google_model, mock_agent):
        """Test initialization sets Google model settings correctly"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        # Act
        _agent = SSQAgent(agent_name="ignore_comment_agent", platform="instagram", persona="Ignore spam")

        # Assert
        mock_settings_class.assert_called_once()
        call_kwargs = mock_settings_class.call_args[1]
        assert call_kwargs["max_tokens"] == 100
        assert call_kwargs["temperature"] == 0.9
        assert call_kwargs["top_p"] == 0.5
        assert call_kwargs["timeout"] == 15

    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.CREATE_REPLY_AGENT", "create_reply_agent")
    def test_init_output_type_string_for_create_reply(self, mock_prompt_gen, mock_google_model, mock_agent):
        """Test initialization sets output_type to str for create_reply agent"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        # Act
        _agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Assert
        call_kwargs = mock_agent.call_args[1]
        assert call_kwargs["output_type"] is str

    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.CREATE_REPLY_AGENT", "create_reply_agent")
    def test_init_output_type_bool_for_other_agents(self, mock_prompt_gen, mock_google_model, mock_agent):
        """Test initialization sets output_type to bool for non-reply agents"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        # Act
        _agent = SSQAgent(agent_name="delete_comment_agent", platform="instagram", persona="Be strict")

        # Assert
        call_kwargs = mock_agent.call_args[1]
        assert call_kwargs["output_type"] is bool


class TestSSQAgentGenerateResponse:
    """Test cases for SSQAgent.generate_response method"""

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"create_reply_agent": "Reply to this comment"})
    async def test_generate_response_string_output(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response returns string for create_reply agent"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = "This is a great comment!"

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        result = await agent.generate_response("Nice post!")

        # Assert
        assert result == "This is a great comment!"
        mock_agent_instance.run.assert_called_once()

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"create_reply_agent": "Reply"})
    async def test_generate_response_strips_quotes(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response strips surrounding quotes from string output"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = '"This is a quoted response"'

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        result = await agent.generate_response("Test comment")

        # Assert
        assert result == "This is a quoted response"

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"delete_comment_agent": "Should delete"})
    async def test_generate_response_bool_output(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response returns bool for non-reply agents"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = True

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="delete_comment_agent", platform="instagram", persona="Be strict")

        # Act
        result = await agent.generate_response("Offensive comment")

        # Assert
        assert result is True

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"ignore_comment_agent": "Should ignore"})
    async def test_generate_response_bool_false(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response returns False"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = False

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="ignore_comment_agent", platform="youtube", persona="Ignore spam")

        # Act
        result = await agent.generate_response("Good comment")

        # Assert
        assert result is False

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"create_reply_agent": "Reply to this comment"})
    async def test_generate_response_constructs_user_prompt(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response constructs user prompt correctly"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = "Response"

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        await agent.generate_response("Nice photo!")

        # Assert
        mock_agent_instance.run.assert_called_once_with('Reply to this comment: "Nice photo!"')

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"create_reply_agent": "Reply"})
    async def test_generate_response_no_quotes_to_strip(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response when output has no quotes"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = "No quotes here"

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        result = await agent.generate_response("Test")

        # Assert
        assert result == "No quotes here"

    @pytest.mark.asyncio
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.PromptGenerator")
    @patch("usecases.ssq_agent.USER_PROMPT", {"create_reply_agent": "Reply"})
    async def test_generate_response_only_start_quote(self, mock_prompt_gen, mock_google_model, mock_agent_class):
        """Test generate_response when output has only start quote"""
        # Arrange
        mock_prompt_instance = Mock()
        mock_prompt_instance.get_prompt_for_agent.return_value = "Test prompt"
        mock_prompt_gen.return_value = mock_prompt_instance

        mock_result = Mock()
        mock_result.output = '"Only start quote'

        mock_agent_instance = AsyncMock()
        mock_agent_instance.run.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(agent_name="create_reply_agent", platform="instagram", persona="Be friendly")

        # Act
        result = await agent.generate_response("Test")

        # Assert
        # Should not strip when only one quote present
        assert result == '"Only start quote'
