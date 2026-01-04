"""
Unit tests for usecases/onboarding_management.py

Tests cover all methods in the OnboardingManagement class including:
- onboard_user
"""

from unittest.mock import MagicMock, Mock, patch

from usecases.onboarding_management import OnboardingManagement


class TestOnboardUser:
    """Test cases for onboard_user method"""

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_success_with_all_fields(self, mock_create_persona, mock_db, mock_logger):
        """Test successful user onboarding with all fields including personal_details"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {
            "uuid": "persona_uuid_123",
            "name": "Business Persona",
            "tone": "Professional",
            "style": "Formal",
        }
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator context manager
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Business Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional and courteous",
            role="brand",
            content_categories=["tech", "business"],
            personal_details="CEO of TechCorp",
        )

        # Assert
        assert error_message == ""
        assert data == persona_data
        assert errors is None

        # Verify PersonaManagement.create_persona was called correctly
        mock_create_persona.assert_called_once_with(
            user=mock_user,
            name="Business Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional and courteous",
            personal_details="CEO of TechCorp",
        )

        # Verify user was updated with correct values
        mock_user.update_values.assert_called_once_with(role="brand", content_categories=["tech", "business"], status="active")

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_success_without_personal_details(self, mock_create_persona, mock_db, mock_logger):
        """Test successful user onboarding without personal_details (optional field)"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {
            "uuid": "persona_uuid_123",
            "name": "Casual Persona",
            "tone": "Friendly",
            "style": "Casual",
        }
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator context manager
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Casual Persona",
            tone="Friendly",
            style="Casual",
            instructions="Be friendly and approachable",
            role="influencer",
            content_categories=["lifestyle", "travel"],
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data == persona_data
        assert errors is None

        # Verify PersonaManagement.create_persona was called with None for personal_details
        mock_create_persona.assert_called_once_with(
            user=mock_user,
            name="Casual Persona",
            tone="Friendly",
            style="Casual",
            instructions="Be friendly and approachable",
            personal_details=None,
        )

        # Verify user was updated
        mock_user.update_values.assert_called_once_with(role="influencer", content_categories=["lifestyle", "travel"], status="active")

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_persona_creation_fails(self, mock_create_persona, mock_db, mock_logger):
        """Test when persona creation fails during onboarding"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        error_msg = "Persona with this name already exists"
        mock_create_persona.return_value = (error_msg, None, "duplicate_error")

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Existing Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert
        assert error_message == error_msg
        assert data is None
        assert errors == "duplicate_error"

        # Verify error was logged
        mock_logger.create_error_log.assert_called_once()
        assert "Persona creation failed during onboarding" in mock_logger.create_error_log.call_args[0][0]

        # Verify transaction was rolled back
        mock_db.rollback.assert_called_once()

        # Verify user update was never called since persona creation failed
        mock_user.update_values.assert_not_called()

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_update_values_fails(self, mock_create_persona, mock_db, mock_logger):
        """Test when user.update_values fails during onboarding"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock(side_effect=Exception("Database error"))

        persona_data = {"uuid": "persona_uuid_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert
        assert "Failed to update user fields" in error_message
        assert data is None
        assert errors == "Database error"

        # Verify error was logged
        mock_logger.create_error_log.assert_called_once()
        assert "Failed to update user fields" in mock_logger.create_error_log.call_args[0][0]

        # Verify transaction was rolled back
        mock_db.rollback.assert_called_once()

        # Verify persona creation succeeded before user update failed
        mock_create_persona.assert_called_once()
        mock_user.update_values.assert_called_once()

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_unexpected_exception(self, mock_create_persona, mock_db, mock_logger):
        """Test handling of unexpected exceptions during onboarding"""
        # Arrange
        mock_user = Mock()

        # Make create_persona raise an unexpected exception
        mock_create_persona.side_effect = Exception("Unexpected error")

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert
        assert "Unexpected error during onboarding" in error_message
        assert data is None
        assert errors == "Unexpected error"

        # Verify error was logged
        mock_logger.create_error_log.assert_called_once()
        assert "Unexpected error during onboarding" in mock_logger.create_error_log.call_args[0][0]

        # Verify transaction was rolled back
        mock_db.rollback.assert_called_once()

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_with_empty_content_categories(self, mock_create_persona, mock_db, mock_logger):
        """Test user onboarding with empty content_categories list"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_uuid_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=[],  # Empty list
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data == persona_data
        assert errors is None

        # Verify user was updated with empty content_categories
        mock_user.update_values.assert_called_once_with(role="brand", content_categories=[], status="active")

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_with_multiple_content_categories(self, mock_create_persona, mock_db, mock_logger):
        """Test user onboarding with multiple content categories"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_uuid_123", "name": "Multi Category Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        content_categories = ["tech", "business", "finance", "startup", "ai"]

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Multi Category Persona",
            tone="Professional",
            style="Formal",
            instructions="Cover multiple topics",
            role="creator",
            content_categories=content_categories,
            personal_details="Multi-niche content creator",
        )

        # Assert
        assert error_message == ""
        assert data == persona_data
        assert errors is None

        # Verify user was updated with all content categories
        mock_user.update_values.assert_called_once_with(role="creator", content_categories=content_categories, status="active")

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_different_roles(self, mock_create_persona, mock_db, mock_logger):
        """Test user onboarding with different role values"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_uuid_123", "name": "Influencer Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Test with influencer role
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Influencer Persona",
            tone="Friendly",
            style="Casual",
            instructions="Be engaging",
            role="influencer",
            content_categories=["lifestyle"],
            personal_details=None,
        )

        # Assert
        assert error_message == ""
        assert data == persona_data

        # Verify correct role was set
        mock_user.update_values.assert_called_with(role="influencer", content_categories=["lifestyle"], status="active")

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_sets_status_to_active(self, mock_create_persona, mock_db, mock_logger):
        """Test that onboarding always sets user status to 'active'"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_uuid_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert
        assert error_message == ""

        # Verify status was set to "active"
        call_kwargs = mock_user.update_values.call_args[1]
        assert call_kwargs["status"] == "active"

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_transaction_rollback_on_persona_failure(self, mock_create_persona, mock_db, mock_logger):
        """Test that transaction is properly rolled back when persona creation fails"""
        # Arrange
        mock_user = Mock()
        mock_create_persona.return_value = ("Persona creation error", None, "error_details")

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert - verify rollback was called
        mock_db.rollback.assert_called_once()
        assert error_message == "Persona creation error"
        assert data is None

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_transaction_rollback_on_update_failure(self, mock_create_persona, mock_db, mock_logger):
        """Test that transaction is properly rolled back when user update fails"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock(side_effect=ValueError("Invalid role"))

        persona_data = {"uuid": "persona_uuid_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="invalid_role",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert - verify rollback was called
        mock_db.rollback.assert_called_once()
        assert "Failed to update user fields" in error_message
        assert data is None

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_preserves_persona_data_structure(self, mock_create_persona, mock_db, mock_logger):
        """Test that persona data structure is preserved in the response"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock()

        # Create a detailed persona data structure
        persona_data = {
            "uuid": "persona_uuid_123",
            "name": "Business Persona",
            "tone": "Professional",
            "style": "Formal",
            "instructions": "Be professional and courteous",
            "personal_details": "CEO of TechCorp",
            "created_at": "2024-01-01T00:00:00",
        }
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Business Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional and courteous",
            role="brand",
            content_categories=["tech"],
            personal_details="CEO of TechCorp",
        )

        # Assert - verify the exact persona data is returned
        assert error_message == ""
        assert data == persona_data
        assert data["uuid"] == "persona_uuid_123"
        assert data["name"] == "Business Persona"
        assert data["tone"] == "Professional"
        assert errors is None

    @patch("usecases.onboarding_management.LoggerUtil")
    @patch("usecases.onboarding_management.ssq_db")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_logs_specific_error_messages(self, mock_create_persona, mock_db, mock_logger):
        """Test that specific error types are logged appropriately"""
        # Arrange
        mock_user = Mock()
        mock_user.update_values = Mock(side_effect=Exception("Connection timeout"))

        persona_data = {"uuid": "persona_uuid_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        # Mock the atomic decorator and rollback
        mock_atomic = MagicMock()
        mock_db.atomic.return_value = mock_atomic
        mock_db.rollback = Mock()

        # Act
        error_message, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        # Assert - verify the specific error was logged
        mock_logger.create_error_log.assert_called_once()
        logged_message = mock_logger.create_error_log.call_args[0][0]
        assert "Failed to update user fields" in logged_message
        assert "Connection timeout" in logged_message
