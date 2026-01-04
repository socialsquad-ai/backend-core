"""
Unit tests for controller/onboarding_controller.py

Tests cover all endpoint handlers including:
- onboard_user
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock the decorators before importing the controller
sys.modules["decorators.user"] = MagicMock()
sys.modules["decorators.user"].require_authentication = lambda f: f

sys.modules["decorators.common"] = MagicMock()
sys.modules["decorators.common"].validate_json_payload = lambda schema: lambda f: f

# Mock usecases modules to avoid import errors with Python 3.9 (union type syntax issues)
sys.modules["usecases.onboarding_management"] = MagicMock()
sys.modules["usecases.persona_management"] = MagicMock()

from controller.onboarding_controller import onboard_user  # noqa: E402


class TestOnboardUser:
    """Test cases for onboard_user endpoint"""

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_success(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test successful user onboarding"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_get_user.return_value = mock_user

        payload = {
            "persona_name": "Professional Bot",
            "tone": "professional",
            "style": "formal",
            "instructions": "Be helpful and professional",
            "role": "content_creator",
            "content_categories": ["tech", "business"],
            "personal_details": "Software engineer",
        }
        mock_get_payload.return_value = payload

        persona_data = {"id": 1, "uuid": "persona-uuid-123", "name": "Professional Bot", "tone": "professional"}
        mock_onboard_user.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "User onboarded successfully", "data": persona_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await onboard_user(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "User onboarded successfully", "data": persona_data}
        mock_onboard_user.assert_called_once_with(
            user=mock_user,
            persona_name="Professional Bot",
            tone="professional",
            style="formal",
            instructions="Be helpful and professional",
            content_categories=["tech", "business"],
            role="content_creator",
            personal_details="Software engineer",
        )

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_without_personal_details(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding without optional personal_details field"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Casual Bot", "tone": "casual", "style": "informal", "instructions": "Be friendly", "role": "influencer", "content_categories": ["lifestyle"]}
        mock_get_payload.return_value = payload

        persona_data = {"id": 2, "name": "Casual Bot"}
        mock_onboard_user.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        mock_onboard_user.assert_called_once_with(
            user=mock_user, persona_name="Casual Bot", tone="casual", style="informal", instructions="Be friendly", content_categories=["lifestyle"], role="influencer", personal_details=None
        )

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_returns_200_on_success(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that successful onboarding returns 200 status code"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Test Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200
        assert call_kwargs["message"] == "User onboarded successfully"

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_error_message(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding with error from OnboardingManagement"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Error Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        error_msg = "Failed to create persona"
        mock_onboard_user.return_value = (error_msg, None, "Database error")

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == error_msg
        assert call_kwargs["errors"] == "Database error"

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_returns_500_on_error(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that onboarding error returns 500 status code"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Test", "tone": "test", "style": "test", "instructions": "test", "role": "test", "content_categories": []}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("Error occurred", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_passes_user_from_context(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that authenticated user from context is passed to OnboardingManagement"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_user.id = 42
        mock_user.email = "test@example.com"
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_args = mock_onboard_user.call_args
        assert call_args[1]["user"] == mock_user
        assert call_args[1]["user"].id == 42

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_passes_all_payload_fields(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that all payload fields are correctly passed to OnboardingManagement"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {
            "persona_name": "Detailed Bot",
            "tone": "enthusiastic",
            "style": "creative",
            "instructions": "Be creative and engaging",
            "role": "brand_ambassador",
            "content_categories": ["fashion", "lifestyle", "beauty"],
            "personal_details": "Fashion blogger with 5 years experience",
        }
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_onboard_user.call_args[1]
        assert call_kwargs["persona_name"] == "Detailed Bot"
        assert call_kwargs["tone"] == "enthusiastic"
        assert call_kwargs["style"] == "creative"
        assert call_kwargs["instructions"] == "Be creative and engaging"
        assert call_kwargs["role"] == "brand_ambassador"
        assert call_kwargs["content_categories"] == ["fashion", "lifestyle", "beauty"]
        assert call_kwargs["personal_details"] == "Fashion blogger with 5 years experience"

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_returns_persona_data_on_success(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that persona data is returned in response on success"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Data Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        persona_data = {"id": 123, "uuid": "persona-uuid-456", "name": "Data Bot", "tone": "neutral", "style": "balanced"}
        mock_onboard_user.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == persona_data

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_returns_none_data_on_error(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that data is None when onboarding fails"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Fail Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("Failed to create persona", None, "DB error")

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] is None

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_empty_content_categories(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding with empty content_categories list"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Empty Categories Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": []}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_onboard_user.call_args[1]
        assert call_kwargs["content_categories"] == []

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_multiple_content_categories(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding with multiple content categories"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        categories = ["tech", "business", "finance", "startups", "ai"]
        payload = {"persona_name": "Multi Category Bot", "tone": "professional", "style": "informative", "instructions": "Cover multiple topics", "role": "journalist", "content_categories": categories}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_onboard_user.call_args[1]
        assert call_kwargs["content_categories"] == categories
        assert len(call_kwargs["content_categories"]) == 5

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_errors_list(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that errors are included in response when provided"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Error Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        error_details = "Persona name already exists for this user"
        mock_onboard_user.return_value = ("Persona creation failed", None, error_details)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["errors"] == error_details
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == "Persona creation failed"

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_response_format_structure(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test that APIResponseFormat is called with correct structure"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"persona_name": "Format Test Bot", "tone": "neutral", "style": "balanced", "instructions": "Test", "role": "creator", "content_categories": ["test"]}
        mock_get_payload.return_value = payload

        persona_data = {"id": 999}
        mock_onboard_user.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"test": "response"}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await onboard_user(mock_request)

        # Assert
        # Verify APIResponseFormat was called with all required parameters
        assert mock_response_format.called
        call_kwargs = mock_response_format.call_args[1]
        assert "status_code" in call_kwargs
        assert "message" in call_kwargs
        assert "data" in call_kwargs
        assert "errors" in call_kwargs
        # Verify get_json was called
        mock_response_instance.get_json.assert_called_once()
        assert result == {"test": "response"}

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_long_instructions(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding with lengthy instructions"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        long_instructions = "A" * 1000  # Very long instructions string
        payload = {"persona_name": "Long Instructions Bot", "tone": "detailed", "style": "comprehensive", "instructions": long_instructions, "role": "educator", "content_categories": ["education"]}
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_onboard_user.call_args[1]
        assert call_kwargs["instructions"] == long_instructions
        assert len(call_kwargs["instructions"]) == 1000

    @pytest.mark.asyncio
    @patch("controller.onboarding_controller.get_context_user")
    @patch("controller.onboarding_controller.get_request_json_post_payload")
    @patch("controller.onboarding_controller.OnboardingManagement.onboard_user")
    @patch("controller.onboarding_controller.APIResponseFormat")
    async def test_onboard_user_with_special_characters_in_fields(self, mock_response_format, mock_onboard_user, mock_get_payload, mock_get_user):
        """Test onboarding with special characters in string fields"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {
            "persona_name": "Bot with emoji 🤖",
            "tone": "casual & friendly",
            "style": "modern/contemporary",
            "instructions": "Use emojis 😊, hashtags #awesome, and @mentions",
            "role": "social_media_manager",
            "content_categories": ["social", "marketing"],
            "personal_details": "Expert in social media (5+ years) & content creation",
        }
        mock_get_payload.return_value = payload

        mock_onboard_user.return_value = ("", {"id": 1}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await onboard_user(mock_request)

        # Assert
        call_kwargs = mock_onboard_user.call_args[1]
        assert "🤖" in call_kwargs["persona_name"]
        assert "&" in call_kwargs["tone"]
        assert "/" in call_kwargs["style"]
        assert "😊" in call_kwargs["instructions"]
        assert "5+" in call_kwargs["personal_details"]
