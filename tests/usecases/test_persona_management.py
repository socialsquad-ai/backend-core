"""
Unit tests for usecases/persona_management.py

Tests cover all methods in the PersonaManagement class including:
- get_persona_templates
- get_user_personas
- create_persona
- update_persona
- delete_persona
"""

from unittest.mock import Mock, patch

from usecases.persona_management import PersonaManagement
from utils.error_messages import (
    INVALID_PAGINATION_PARAMETERS,
    PERSONA_ALREADY_EXISTS,
    RESOURCE_NOT_FOUND,
)


class TestGetPersonaTemplates:
    """Test cases for get_persona_templates method"""

    @patch("usecases.persona_management.PersonaTemplate")
    def test_get_persona_templates_success(self, mock_persona_template):
        """Test successful retrieval of persona templates"""
        # Arrange
        mock_template1 = Mock()
        mock_template1.get_details.return_value = {
            "uuid": "uuid1",
            "name": "Professional",
            "description": "Professional tone",
            "tone": "professional",
            "style": "formal",
            "instructions": "Be professional",
        }
        mock_template2 = Mock()
        mock_template2.get_details.return_value = {
            "uuid": "uuid2",
            "name": "Casual",
            "description": "Casual tone",
            "tone": "casual",
            "style": "informal",
            "instructions": "Be casual",
        }
        mock_persona_template.get_all_templates.return_value = [mock_template1, mock_template2]

        # Act
        error_message, data, errors = PersonaManagement.get_persona_templates()

        # Assert
        assert error_message == ""
        assert data == [
            {
                "uuid": "uuid1",
                "name": "Professional",
                "description": "Professional tone",
                "tone": "professional",
                "style": "formal",
                "instructions": "Be professional",
            },
            {
                "uuid": "uuid2",
                "name": "Casual",
                "description": "Casual tone",
                "tone": "casual",
                "style": "informal",
                "instructions": "Be casual",
            },
        ]
        assert errors is None
        mock_persona_template.get_all_templates.assert_called_once()

    @patch("usecases.persona_management.PersonaTemplate")
    def test_get_persona_templates_empty_list(self, mock_persona_template):
        """Test when no templates exist"""
        # Arrange
        mock_persona_template.get_all_templates.return_value = []

        # Act
        error_message, data, errors = PersonaManagement.get_persona_templates()

        # Assert
        assert error_message == ""
        assert data == []
        assert errors is None


class TestGetUserPersonas:
    """Test cases for get_user_personas method"""

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_success(self, mock_persona):
        """Test successful retrieval of user personas with pagination"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona1 = Mock()
        mock_persona1.get_details.return_value = {
            "uuid": "persona_uuid1",
            "name": "My Persona",
            "tone": "friendly",
            "style": "casual",
            "instructions": "Be friendly",
            "personal_details": "Details",
        }
        mock_persona2 = Mock()
        mock_persona2.get_details.return_value = {
            "uuid": "persona_uuid2",
            "name": "Work Persona",
            "tone": "professional",
            "style": "formal",
            "instructions": "Be professional",
            "personal_details": "",
        }

        mock_persona.get_all_for_user.return_value = [mock_persona1, mock_persona2]
        mock_persona.get_all_for_user_count.return_value = 15

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=10)

        # Assert
        assert error_message == ""
        assert data["items"] == [
            {
                "uuid": "persona_uuid1",
                "name": "My Persona",
                "tone": "friendly",
                "style": "casual",
                "instructions": "Be friendly",
                "personal_details": "Details",
            },
            {
                "uuid": "persona_uuid2",
                "name": "Work Persona",
                "tone": "professional",
                "style": "formal",
                "instructions": "Be professional",
                "personal_details": "",
            },
        ]
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 2
        assert errors is None
        mock_persona.get_all_for_user.assert_called_once_with(mock_user, 1, 10)
        mock_persona.get_all_for_user_count.assert_called_once_with(mock_user)

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_empty_result(self, mock_persona):
        """Test when user has no personas"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_all_for_user.return_value = []
        mock_persona.get_all_for_user_count.return_value = 0

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=10)

        # Assert
        assert error_message == ""
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0
        assert errors is None

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_with_custom_page_size(self, mock_persona):
        """Test with custom page size"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_all_for_user.return_value = []
        mock_persona.get_all_for_user_count.return_value = 50

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=2, page_size=20)

        # Assert
        assert error_message == ""
        assert data["page"] == 2
        assert data["page_size"] == 20
        assert data["total"] == 50
        assert data["total_pages"] == 3
        mock_persona.get_all_for_user.assert_called_once_with(mock_user, 2, 20)

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_invalid_page_less_than_one(self, mock_persona):
        """Test with page < 1"""
        # Arrange
        mock_user = Mock(id=1)

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=0, page_size=10)

        # Assert
        assert error_message == INVALID_PAGINATION_PARAMETERS
        assert data is None
        assert errors is None
        mock_persona.get_all_for_user.assert_not_called()

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_invalid_page_size_less_than_one(self, mock_persona):
        """Test with page_size < 1"""
        # Arrange
        mock_user = Mock(id=1)

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=0)

        # Assert
        assert error_message == INVALID_PAGINATION_PARAMETERS
        assert data is None
        assert errors is None

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_invalid_page_size_greater_than_100(self, mock_persona):
        """Test with page_size > 100"""
        # Arrange
        mock_user = Mock(id=1)

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=101)

        # Assert
        assert error_message == INVALID_PAGINATION_PARAMETERS
        assert data is None
        assert errors is None

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_page_size_exactly_100(self, mock_persona):
        """Test with page_size exactly 100 (boundary condition)"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_all_for_user.return_value = []
        mock_persona.get_all_for_user_count.return_value = 0

        # Act
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=100)

        # Assert
        assert error_message == ""
        assert data is not None
        mock_persona.get_all_for_user.assert_called_once_with(mock_user, 1, 100)

    @patch("usecases.persona_management.Persona")
    def test_get_user_personas_total_pages_calculation(self, mock_persona):
        """Test total pages calculation edge cases"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_all_for_user.return_value = []
        mock_persona.get_all_for_user_count.return_value = 25

        # Act - 25 items with page_size of 10 should be 3 pages
        error_message, data, errors = PersonaManagement.get_user_personas(mock_user, page=1, page_size=10)

        # Assert
        assert data["total_pages"] == 3  # (25 + 10 - 1) // 10 = 3


class TestCreatePersona:
    """Test cases for create_persona method"""

    @patch("usecases.persona_management.LoggerUtil")
    @patch("usecases.persona_management.Persona")
    def test_create_persona_success(self, mock_persona, mock_logger):
        """Test successful persona creation"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_name_and_user.return_value = None
        mock_created_persona = Mock()
        mock_created_persona.get_details.return_value = {
            "uuid": "new_uuid",
            "name": "Test Persona",
            "tone": "friendly",
            "style": "casual",
            "instructions": "Be friendly",
            "personal_details": "My details",
        }
        mock_persona.create_persona.return_value = mock_created_persona

        # Act
        error_message, data, errors = PersonaManagement.create_persona(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
            personal_details="My details",
        )

        # Assert
        assert error_message == ""
        assert data == {
            "uuid": "new_uuid",
            "name": "Test Persona",
            "tone": "friendly",
            "style": "casual",
            "instructions": "Be friendly",
            "personal_details": "My details",
        }
        assert errors is None
        mock_persona.get_by_name_and_user.assert_called_once_with("Test Persona", mock_user)
        mock_persona.create_persona.assert_called_once_with(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
            personal_details="My details",
        )

    @patch("usecases.persona_management.LoggerUtil")
    @patch("usecases.persona_management.Persona")
    def test_create_persona_success_without_personal_details(self, mock_persona, mock_logger):
        """Test successful persona creation with None personal_details"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_name_and_user.return_value = None
        mock_created_persona = Mock()
        mock_created_persona.get_details.return_value = {
            "uuid": "new_uuid",
            "name": "Test Persona",
            "tone": "friendly",
            "style": "casual",
            "instructions": "Be friendly",
            "personal_details": "",
        }
        mock_persona.create_persona.return_value = mock_created_persona

        # Act
        error_message, data, errors = PersonaManagement.create_persona(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data is not None
        mock_persona.create_persona.assert_called_once_with(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
            personal_details="",  # None should be converted to empty string
        )

    @patch("usecases.persona_management.LoggerUtil")
    @patch("usecases.persona_management.Persona")
    def test_create_persona_already_exists(self, mock_persona, mock_logger):
        """Test creating persona when name already exists for user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_existing_persona = Mock()
        mock_persona.get_by_name_and_user.return_value = mock_existing_persona

        # Act
        error_message, data, errors = PersonaManagement.create_persona(
            user=mock_user,
            name="Existing Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
            personal_details="Details",
        )

        # Assert
        assert error_message == PERSONA_ALREADY_EXISTS
        assert data is None
        assert errors is None
        mock_persona.get_by_name_and_user.assert_called_once_with("Existing Persona", mock_user)
        mock_persona.create_persona.assert_not_called()

    @patch("usecases.persona_management.LoggerUtil")
    @patch("usecases.persona_management.Persona")
    def test_create_persona_exception_handling(self, mock_persona, mock_logger):
        """Test exception handling during persona creation"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_name_and_user.return_value = None
        mock_persona.create_persona.side_effect = Exception("Database error")

        # Act
        error_message, data, errors = PersonaManagement.create_persona(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
        )

        # Assert
        assert "Failed to create persona" in error_message
        assert "Database error" in error_message
        assert data is None
        assert errors is None
        mock_logger.create_error_log.assert_called_once()

    @patch("usecases.persona_management.LoggerUtil")
    @patch("usecases.persona_management.Persona")
    def test_create_persona_exception_during_existence_check(self, mock_persona, mock_logger):
        """Test exception during name existence check"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_name_and_user.side_effect = Exception("Query error")

        # Act
        error_message, data, errors = PersonaManagement.create_persona(
            user=mock_user,
            name="Test Persona",
            tone="friendly",
            style="casual",
            instructions="Be friendly",
        )

        # Assert
        assert "Failed to create persona" in error_message
        assert data is None
        mock_logger.create_error_log.assert_called_once()


class TestUpdatePersona:
    """Test cases for update_persona method"""

    @patch("usecases.persona_management.Persona")
    def test_update_persona_success_all_fields(self, mock_persona):
        """Test successful update of all persona fields"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.uuid = "persona_uuid"
        mock_persona_instance.get_details.return_value = {
            "uuid": "persona_uuid",
            "name": "Updated Name",
            "tone": "updated_tone",
            "style": "updated_style",
            "instructions": "Updated instructions",
            "personal_details": "Updated details",
        }
        mock_persona.get_by_uuid.return_value = mock_persona_instance
        mock_persona.get_by_name_and_user.return_value = None

        # Act
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            name="Updated Name",
            tone="updated_tone",
            style="updated_style",
            instructions="Updated instructions",
            personal_details="Updated details",
        )

        # Assert
        assert error_message == ""
        assert data == {
            "uuid": "persona_uuid",
            "name": "Updated Name",
            "tone": "updated_tone",
            "style": "updated_style",
            "instructions": "Updated instructions",
            "personal_details": "Updated details",
        }
        assert errors is None
        assert mock_persona_instance.name == "Updated Name"
        assert mock_persona_instance.tone == "updated_tone"
        assert mock_persona_instance.style == "updated_style"
        assert mock_persona_instance.instructions == "Updated instructions"
        assert mock_persona_instance.personal_details == "Updated details"
        mock_persona_instance.save.assert_called_once()

    @patch("usecases.persona_management.Persona")
    def test_update_persona_partial_update(self, mock_persona):
        """Test updating only some fields"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.uuid = "persona_uuid"
        mock_persona_instance.get_details.return_value = {
            "uuid": "persona_uuid",
            "name": "Original Name",
            "tone": "updated_tone",
            "style": "original_style",
            "instructions": "Updated instructions",
            "personal_details": "original",
        }
        mock_persona.get_by_uuid.return_value = mock_persona_instance

        # Act - Only update tone and instructions
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            name=None,
            tone="updated_tone",
            style=None,
            instructions="Updated instructions",
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data is not None
        assert mock_persona_instance.tone == "updated_tone"
        assert mock_persona_instance.instructions == "Updated instructions"
        mock_persona_instance.save.assert_called_once()

    @patch("usecases.persona_management.Persona")
    def test_update_persona_no_fields_to_update(self, mock_persona):
        """Test when no fields are provided for update"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.get_details.return_value = {
            "uuid": "persona_uuid",
            "name": "Original Name",
            "tone": "original_tone",
            "style": "original_style",
            "instructions": "original",
            "personal_details": "original",
        }
        mock_persona.get_by_uuid.return_value = mock_persona_instance

        # Act - All fields are None
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            name=None,
            tone=None,
            style=None,
            instructions=None,
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data is not None
        mock_persona_instance.save.assert_not_called()  # No save if nothing to update

    @patch("usecases.persona_management.Persona")
    def test_update_persona_not_found(self, mock_persona):
        """Test updating non-existent persona"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_uuid.return_value = None

        # Act
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="nonexistent_uuid",
            name="Updated Name",
        )

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None

    @patch("usecases.persona_management.Persona")
    def test_update_persona_wrong_user(self, mock_persona):
        """Test updating persona that belongs to different user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 2  # Different user
        mock_persona.get_by_uuid.return_value = mock_persona_instance

        # Act
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            name="Updated Name",
        )

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_persona_instance.save.assert_not_called()

    @patch("usecases.persona_management.Persona")
    def test_update_persona_name_already_exists(self, mock_persona):
        """Test updating persona name to one that already exists"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.user = mock_user
        mock_persona_instance.uuid = "persona_uuid_1"

        mock_existing_persona = Mock()
        mock_existing_persona.uuid = "persona_uuid_2"  # Different persona

        mock_persona.get_by_uuid.return_value = mock_persona_instance
        mock_persona.get_by_name_and_user.return_value = mock_existing_persona

        # Act
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid_1",
            name="Existing Name",
        )

        # Assert
        assert error_message == PERSONA_ALREADY_EXISTS
        assert data is None
        assert errors is None
        mock_persona_instance.save.assert_not_called()

    @patch("usecases.persona_management.Persona")
    def test_update_persona_name_to_same_name(self, mock_persona):
        """Test updating persona name to its own current name (should succeed)"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.user = mock_user
        mock_persona_instance.uuid = "persona_uuid"
        mock_persona_instance.get_details.return_value = {
            "uuid": "persona_uuid",
            "name": "Same Name",
            "tone": "tone",
            "style": "style",
            "instructions": "instructions",
            "personal_details": "details",
        }

        # When checking for existing name, it finds itself
        mock_existing_persona = Mock()
        mock_existing_persona.uuid = "persona_uuid"  # Same UUID

        mock_persona.get_by_uuid.return_value = mock_persona_instance
        mock_persona.get_by_name_and_user.return_value = mock_existing_persona

        # Act
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            name="Same Name",
        )

        # Assert
        assert error_message == ""
        assert data is not None
        mock_persona_instance.save.assert_called_once()

    @patch("usecases.persona_management.Persona")
    def test_update_persona_empty_string_values(self, mock_persona):
        """Test updating fields with empty strings"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona_instance.uuid = "persona_uuid"
        mock_persona_instance.get_details.return_value = {
            "uuid": "persona_uuid",
            "name": "name",
            "tone": "",
            "style": "",
            "instructions": "",
            "personal_details": "",
        }
        mock_persona.get_by_uuid.return_value = mock_persona_instance

        # Act - Update with empty strings
        error_message, data, errors = PersonaManagement.update_persona(
            user=mock_user,
            persona_uuid="persona_uuid",
            tone="",
            style="",
            instructions="",
            personal_details="",
        )

        # Assert
        assert error_message == ""
        assert mock_persona_instance.tone == ""
        assert mock_persona_instance.style == ""
        assert mock_persona_instance.instructions == ""
        assert mock_persona_instance.personal_details == ""
        mock_persona_instance.save.assert_called_once()


class TestDeletePersona:
    """Test cases for delete_persona method"""

    @patch("usecases.persona_management.Persona")
    def test_delete_persona_success(self, mock_persona):
        """Test successful persona deletion"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona.get_by_uuid.return_value = mock_persona_instance
        mock_persona.delete_by_uuid.return_value = True

        # Act
        error_message, data, errors = PersonaManagement.delete_persona(
            persona_uuid="persona_uuid",
            user=mock_user,
        )

        # Assert
        assert error_message == ""
        assert data is None
        assert errors is None
        mock_persona.get_by_uuid.assert_called_once_with("persona_uuid")
        mock_persona.delete_by_uuid.assert_called_once_with("persona_uuid")

    @patch("usecases.persona_management.Persona")
    def test_delete_persona_not_found(self, mock_persona):
        """Test deleting non-existent persona"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona.get_by_uuid.return_value = None

        # Act
        error_message, data, errors = PersonaManagement.delete_persona(
            persona_uuid="nonexistent_uuid",
            user=mock_user,
        )

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_persona.delete_by_uuid.assert_not_called()

    @patch("usecases.persona_management.Persona")
    def test_delete_persona_wrong_user(self, mock_persona):
        """Test deleting persona that belongs to different user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 2  # Different user
        mock_persona.get_by_uuid.return_value = mock_persona_instance

        # Act
        error_message, data, errors = PersonaManagement.delete_persona(
            persona_uuid="persona_uuid",
            user=mock_user,
        )

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_persona.delete_by_uuid.assert_not_called()

    @patch("usecases.persona_management.Persona")
    def test_delete_persona_deletion_fails(self, mock_persona):
        """Test when soft delete operation fails"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona_instance = Mock()
        mock_persona_instance.user.id = 1
        mock_persona.get_by_uuid.return_value = mock_persona_instance
        mock_persona.delete_by_uuid.return_value = False  # Deletion failed

        # Act
        error_message, data, errors = PersonaManagement.delete_persona(
            persona_uuid="persona_uuid",
            user=mock_user,
        )

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_persona.delete_by_uuid.assert_called_once_with("persona_uuid")
