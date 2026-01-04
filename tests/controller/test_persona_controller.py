"""
Unit tests for controller/persona_controller.py

Tests cover all endpoint handlers including:
- get_persona_templates
- get_personas
- create_persona
- update_persona
- delete_persona
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock the decorators before importing the controller
sys.modules["decorators.user"] = MagicMock()
sys.modules["decorators.user"].require_authentication = lambda f: f

sys.modules["decorators.common"] = MagicMock()
sys.modules["decorators.common"].validate_json_payload = lambda schema: lambda f: f

# Mock the PersonaManagement module to avoid import errors
sys.modules["usecases.persona_management"] = MagicMock()

from controller.persona_controller import (  # noqa: E402
    create_persona,
    delete_persona,
    get_persona_templates,
    get_personas,
    update_persona,
)


class TestGetPersonaTemplates:
    """Test cases for get_persona_templates endpoint"""

    @pytest.mark.asyncio
    @patch("controller.persona_controller.PersonaManagement.get_persona_templates")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_persona_templates_success(self, mock_response_format, mock_get_templates):
        """Test successful retrieval of persona templates"""
        # Arrange
        mock_request = Mock()
        templates_data = [{"id": 1, "name": "Professional", "tone": "formal"}, {"id": 2, "name": "Casual", "tone": "friendly"}]
        mock_get_templates.return_value = ("", templates_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": templates_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_persona_templates(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": templates_data}
        mock_get_templates.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.persona_controller.PersonaManagement.get_persona_templates")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_persona_templates_returns_200_on_success(self, mock_response_format, mock_get_templates):
        """Test that successful template retrieval returns 200"""
        # Arrange
        mock_request = Mock()
        mock_get_templates.return_value = ("", [], None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_persona_templates(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.persona_controller.PersonaManagement.get_persona_templates")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_persona_templates_returns_500_on_error(self, mock_response_format, mock_get_templates):
        """Test that error returns 500"""
        # Arrange
        mock_request = Mock()
        mock_get_templates.return_value = ("Database error", None, ["error1"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_persona_templates(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.persona_controller.PersonaManagement.get_persona_templates")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_persona_templates_with_errors(self, mock_response_format, mock_get_templates):
        """Test template retrieval with errors"""
        # Arrange
        mock_request = Mock()
        error_message = "Failed to fetch templates"
        errors = ["DB connection error"]
        mock_get_templates.return_value = (error_message, None, errors)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_persona_templates(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == error_message
        assert call_kwargs["errors"] == errors

    @pytest.mark.asyncio
    @patch("controller.persona_controller.PersonaManagement.get_persona_templates")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_persona_templates_empty_list(self, mock_response_format, mock_get_templates):
        """Test retrieval when no templates exist"""
        # Arrange
        mock_request = Mock()
        mock_get_templates.return_value = ("", [], None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": []}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_persona_templates(mock_request)

        # Assert
        assert result["data"] == []


class TestGetPersonas:
    """Test cases for get_personas endpoint"""

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.get_user_personas")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_personas_success(self, mock_response_format, mock_get_user_personas, mock_get_user):
        """Test successful retrieval of user personas"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        personas_data = {"items": [{"id": 1, "name": "Persona 1"}], "total": 1, "page": 1, "page_size": 10, "total_pages": 1}
        mock_get_user_personas.return_value = ("", personas_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": personas_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_personas(mock_request, page=1, page_size=10)

        # Assert
        assert result["status_code"] == 200
        mock_get_user_personas.assert_called_once_with(mock_user, 1, 10)

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.get_user_personas")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_personas_with_custom_pagination(self, mock_response_format, mock_get_user_personas, mock_get_user):
        """Test persona retrieval with custom pagination parameters"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        personas_data = {"items": [], "total": 50, "page": 3, "page_size": 20, "total_pages": 3}
        mock_get_user_personas.return_value = ("", personas_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_personas(mock_request, page=3, page_size=20)

        # Assert
        mock_get_user_personas.assert_called_once_with(mock_user, 3, 20)

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.get_user_personas")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_personas_invalid_pagination_returns_400(self, mock_response_format, mock_get_user_personas, mock_get_user):
        """Test that invalid pagination parameters return 400"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user
        mock_get_user_personas.return_value = ("Invalid pagination parameters. Page must be >= 1 and page size between 1-100", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_personas(mock_request, page=0, page_size=10)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 400

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.get_user_personas")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_personas_database_error_returns_500(self, mock_response_format, mock_get_user_personas, mock_get_user):
        """Test that database error returns 500"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user
        mock_get_user_personas.return_value = ("Database error", None, ["error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_personas(mock_request, page=1, page_size=10)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.get_user_personas")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_get_personas_empty_list(self, mock_response_format, mock_get_user_personas, mock_get_user):
        """Test retrieval when user has no personas"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        personas_data = {"items": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0}
        mock_get_user_personas.return_value = ("", personas_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"data": personas_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_personas(mock_request, page=1, page_size=10)

        # Assert
        assert result["data"]["items"] == []
        assert result["data"]["total"] == 0


class TestCreatePersona:
    """Test cases for create_persona endpoint"""

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.create_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_create_persona_success(self, mock_response_format, mock_create_persona, mock_get_payload, mock_get_user):
        """Test successful persona creation"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {
            "name": "Professional Bot",
            "tone": "formal",
            "style": "concise",
            "instructions": "Be professional",
            "role": "assistant",
            "content_categories": ["tech", "business"],
            "personal_details": "Expert in tech",
        }
        mock_get_payload.return_value = payload

        persona_data = {"id": 1, "name": "Professional Bot", "uuid": "abc-123"}
        mock_create_persona.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 201, "message": "Persona created successfully", "data": persona_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await create_persona(mock_request)

        # Assert
        assert result["status_code"] == 201
        assert result["message"] == "Persona created successfully"
        mock_create_persona.assert_called_once_with(
            user=mock_user,
            name=payload["name"],
            tone=payload["tone"],
            style=payload["style"],
            instructions=payload["instructions"],
            content_categories=payload["content_categories"],
            role=payload["role"],
            personal_details=payload["personal_details"],
        )

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.create_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_create_persona_without_optional_fields(self, mock_response_format, mock_create_persona, mock_get_payload, mock_get_user):
        """Test persona creation without optional personal_details field"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"name": "Simple Bot", "tone": "casual", "style": "brief", "instructions": "Be friendly", "role": "helper", "content_categories": ["general"]}
        mock_get_payload.return_value = payload

        persona_data = {"id": 2, "name": "Simple Bot"}
        mock_create_persona.return_value = ("", persona_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_persona(mock_request)

        # Assert
        call_args = mock_create_persona.call_args[1]
        assert call_args["personal_details"] is None

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.create_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_create_persona_returns_201_on_success(self, mock_response_format, mock_create_persona, mock_get_payload, mock_get_user):
        """Test that successful creation returns 201 status code"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test", "role": "test", "content_categories": []}
        mock_get_payload.return_value = payload
        mock_create_persona.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_persona(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 201

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.create_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_create_persona_returns_500_on_error(self, mock_response_format, mock_create_persona, mock_get_payload, mock_get_user):
        """Test that error returns 500 status code"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test", "role": "test", "content_categories": []}
        mock_get_payload.return_value = payload
        mock_create_persona.return_value = ("Database error", None, ["error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_persona(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.create_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_create_persona_with_error_message(self, mock_response_format, mock_create_persona, mock_get_payload, mock_get_user):
        """Test persona creation with error message"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test", "role": "test", "content_categories": []}
        mock_get_payload.return_value = payload

        error_message = "Failed to create persona"
        mock_create_persona.return_value = (error_message, None, ["DB error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_persona(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == error_message


class TestUpdatePersona:
    """Test cases for update_persona endpoint"""

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_success(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test successful persona update"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "test-uuid-123"
        payload = {"name": "Updated Name", "tone": "casual", "style": "brief", "instructions": "New instructions", "personal_details": "Updated details"}
        mock_get_payload.return_value = payload

        updated_data = {"id": 1, "name": "Updated Name", "uuid": persona_uuid}
        mock_update_persona.return_value = ("", updated_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "Persona updated successfully", "data": updated_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await update_persona(mock_request, persona_uuid)

        # Assert
        assert result["status_code"] == 200
        assert result["message"] == "Persona updated successfully"
        mock_update_persona.assert_called_once_with(user=mock_user, persona_uuid=persona_uuid, **payload)

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_not_found_returns_404(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test that persona not found returns 404"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "non-existent-uuid"
        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test"}
        mock_get_payload.return_value = payload
        mock_update_persona.return_value = ("Not found", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await update_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 404
        assert call_kwargs["message"] == "Not found"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_already_exists_returns_400(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test that duplicate persona name returns 400"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        payload = {"name": "Existing Name", "tone": "test", "style": "test", "instructions": "test"}
        mock_get_payload.return_value = payload
        mock_update_persona.return_value = ("Persona already exists", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await update_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 400
        assert call_kwargs["message"] == "Persona already exists"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_database_error_returns_500(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test that database error returns 500"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test"}
        mock_get_payload.return_value = payload
        mock_update_persona.return_value = ("Database connection error", None, ["error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await update_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == "Database connection error"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_without_optional_fields(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test persona update without optional personal_details field"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        payload = {"name": "Updated", "tone": "formal", "style": "detailed", "instructions": "Instructions"}
        mock_get_payload.return_value = payload
        mock_update_persona.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await update_persona(mock_request, persona_uuid)

        # Assert
        mock_update_persona.assert_called_once()
        call_kwargs = mock_update_persona.call_args[1]
        assert "personal_details" not in payload or call_kwargs.get("personal_details") is None

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.get_request_json_post_payload")
    @patch("controller.persona_controller.PersonaManagement.update_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_update_persona_returns_correct_status_code(self, mock_response_format, mock_update_persona, mock_get_payload, mock_get_user):
        """Test that successful update returns 200 status code"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        payload = {"name": "Test", "tone": "test", "style": "test", "instructions": "test"}
        mock_get_payload.return_value = payload
        mock_update_persona.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await update_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200


class TestDeletePersona:
    """Test cases for delete_persona endpoint"""

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_success(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test successful persona deletion"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-to-delete"
        mock_delete_persona.return_value = ("", {"deleted": True}, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "Persona deleted successfully", "data": {"deleted": True}}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await delete_persona(mock_request, persona_uuid)

        # Assert
        assert result["status_code"] == 200
        assert result["message"] == "Persona deleted successfully"
        mock_delete_persona.assert_called_once_with(persona_uuid, mock_user)

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_not_found_returns_404(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test that deleting non-existent persona returns 404"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "non-existent-uuid"
        mock_delete_persona.return_value = ("Not found", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 404
        assert call_kwargs["message"] == "Not found"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_database_error_returns_500(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test that database error returns 500"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        mock_delete_persona.return_value = ("Database error", None, ["error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == "Database error"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_returns_correct_message_on_success(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test that successful deletion returns correct message"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        mock_delete_persona.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == "Persona deleted successfully"

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_passes_correct_arguments(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test that delete_persona is called with correct arguments"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_user.id = 123
        mock_get_user.return_value = mock_user

        persona_uuid = "specific-uuid-456"
        mock_delete_persona.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_persona(mock_request, persona_uuid)

        # Assert
        mock_delete_persona.assert_called_once_with(persona_uuid, mock_user)

    @pytest.mark.asyncio
    @patch("controller.persona_controller.get_context_user")
    @patch("controller.persona_controller.PersonaManagement.delete_persona")
    @patch("controller.persona_controller.APIResponseFormat")
    async def test_delete_persona_with_errors_array(self, mock_response_format, mock_delete_persona, mock_get_user):
        """Test deletion with errors array"""
        # Arrange
        mock_request = Mock()
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        persona_uuid = "uuid-123"
        errors = ["Permission denied", "Resource locked"]
        mock_delete_persona.return_value = ("Failed to delete", None, errors)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_persona(mock_request, persona_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["errors"] == errors
