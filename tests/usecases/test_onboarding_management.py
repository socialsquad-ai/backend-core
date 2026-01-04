from unittest.mock import Mock, patch

from usecases.onboarding_management import OnboardingManagement


class TestOnboardingManagementOnboardUser:
    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_success(self, mock_create_persona, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_123", "name": "Test Persona"}
        mock_create_persona.return_value = ("", persona_data, None)

        error, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test Persona",
            tone="Professional",
            style="Formal",
            instructions="Be professional",
            role="brand",
            content_categories=["tech", "gaming"],
            personal_details="About me",
        )

        assert error == ""
        assert data == persona_data
        assert errors is None
        mock_user.update_values.assert_called_once_with(role="brand", content_categories=["tech", "gaming"], status="active")

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("data_adapter.db.ssq_db.rollback")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    @patch("usecases.onboarding_management.LoggerUtil.create_error_log")
    def test_onboard_user_persona_creation_fails(self, mock_log, mock_create_persona, mock_rollback, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_user = Mock()

        mock_create_persona.return_value = ("Persona already exists", None, {"name": ["already exists"]})

        error, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Duplicate",
            tone="Casual",
            style="Friendly",
            instructions="Be friendly",
            role="creator",
            content_categories=["music"],
        )

        assert error == "Persona already exists"
        assert data is None
        assert errors == {"name": ["already exists"]}
        mock_rollback.assert_called_once()

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("data_adapter.db.ssq_db.rollback")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    @patch("usecases.onboarding_management.LoggerUtil.create_error_log")
    def test_onboard_user_update_values_fails(self, mock_log, mock_create_persona, mock_rollback, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_user = Mock()
        mock_user.update_values.side_effect = Exception("Database error")

        persona_data = {"uuid": "persona_123"}
        mock_create_persona.return_value = ("", persona_data, None)

        error, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test",
            tone="Casual",
            style="Friendly",
            instructions="Test",
            role="brand",
            content_categories=["tech"],
        )

        assert "Failed to update user fields" in error
        assert data is None
        assert errors == "Database error"
        mock_rollback.assert_called_once()

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("data_adapter.db.ssq_db.rollback")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    @patch("usecases.onboarding_management.LoggerUtil.create_error_log")
    def test_onboard_user_unexpected_exception(self, mock_log, mock_create_persona, mock_rollback, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_user = Mock()

        mock_create_persona.side_effect = Exception("Unexpected error")

        error, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test",
            tone="Casual",
            style="Friendly",
            instructions="Test",
            role="brand",
            content_categories=["tech"],
        )

        assert "Unexpected error during onboarding" in error
        assert data is None
        assert errors == "Unexpected error"
        mock_rollback.assert_called_once()

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.onboarding_management.PersonaManagement.create_persona")
    def test_onboard_user_with_optional_personal_details(self, mock_create_persona, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_user = Mock()
        mock_user.update_values = Mock()

        persona_data = {"uuid": "persona_123"}
        mock_create_persona.return_value = ("", persona_data, None)

        error, data, errors = OnboardingManagement.onboard_user(
            user=mock_user,
            persona_name="Test",
            tone="Casual",
            style="Friendly",
            instructions="Test",
            role="brand",
            content_categories=["tech"],
            personal_details=None,
        )

        assert error == ""
        call_kwargs = mock_create_persona.call_args.kwargs
        assert call_kwargs["personal_details"] is None
