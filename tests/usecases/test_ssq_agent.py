from unittest.mock import AsyncMock, Mock, patch

import pytest

from config.non_env import CREATE_REPLY_AGENT, DELETE_COMMENT_AGENT, IGNORE_COMMENT_AGENT
from usecases.ssq_agent import SSQAgent


class TestSSQAgentInit:
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_ssq_agent_initialization(self, mock_prompt_gen, mock_agent, mock_google_model):
        mock_prompt = "Test system prompt"
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = mock_prompt
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        agent = SSQAgent(CREATE_REPLY_AGENT, "instagram", "friendly assistant")

        assert agent.agent_name == CREATE_REPLY_AGENT
        assert agent.system_prompt == mock_prompt
        mock_prompt_gen.assert_called_once_with(CREATE_REPLY_AGENT, "instagram", "friendly assistant")

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_ssq_agent_creates_agent_with_string_output_for_create_reply(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt = "Test prompt"
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = mock_prompt
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        SSQAgent(CREATE_REPLY_AGENT, "youtube", "persona")

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs["output_type"] is str
        assert call_kwargs["system_prompt"] == mock_prompt

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_ssq_agent_creates_agent_with_bool_output_for_ignore_comment(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt = "Test prompt"
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = mock_prompt
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        SSQAgent(IGNORE_COMMENT_AGENT, "instagram", "persona")

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs["output_type"] is bool

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    def test_ssq_agent_creates_agent_with_bool_output_for_delete_comment(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt = "Test prompt"
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = mock_prompt
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        SSQAgent(DELETE_COMMENT_AGENT, "instagram", "persona")

        call_kwargs = mock_agent_class.call_args.kwargs
        assert call_kwargs["output_type"] is bool


class TestSSQAgentGenerateResponse:
    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    @pytest.mark.asyncio
    async def test_generate_response_returns_agent_output(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = "prompt"
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.data = "This is a response"
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(CREATE_REPLY_AGENT, "instagram", "persona")
        result = await agent.generate_response("Great post!")

        assert result == "This is a response"

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    @pytest.mark.asyncio
    async def test_generate_response_strips_surrounding_quotes(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = "prompt"
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.data = '"This is quoted"'
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(CREATE_REPLY_AGENT, "instagram", "persona")
        result = await agent.generate_response("Comment")

        assert result == "This is quoted"

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    @pytest.mark.asyncio
    async def test_generate_response_does_not_strip_non_matching_quotes(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = "prompt"
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.data = '"Only start quote'
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(CREATE_REPLY_AGENT, "instagram", "persona")
        result = await agent.generate_response("Comment")

        assert result == 'Only start quote'

    @patch("usecases.ssq_agent.GoogleModel")
    @patch("usecases.ssq_agent.Agent")
    @patch("usecases.ssq_agent.PromptGenerator")
    @pytest.mark.asyncio
    async def test_generate_response_handles_bool_output(self, mock_prompt_gen, mock_agent_class, mock_google_model):
        mock_prompt_gen_instance = Mock()
        mock_prompt_gen_instance.get_prompt_for_agent.return_value = "prompt"
        mock_prompt_gen.return_value = mock_prompt_gen_instance

        mock_agent_instance = Mock()
        mock_result = Mock()
        mock_result.data = True
        mock_agent_instance.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent_instance

        agent = SSQAgent(IGNORE_COMMENT_AGENT, "instagram", "persona")
        result = await agent.generate_response("spam comment")

        assert result is True
