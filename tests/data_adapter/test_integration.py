from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

from data_adapter.integration import Integration


class TestIntegrationGetAllForUser:
    @patch.object(Integration, "select_query")
    def test_get_all_for_user_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.where.return_value = []

        mock_user = Mock()
        Integration.get_all_for_user(mock_user)

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()


class TestIntegrationGetByUuidForUser:
    @patch.object(Integration, "select_query")
    def test_get_by_uuid_for_user_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        mock_user = Mock()
        test_uuid = "test-uuid"
        Integration.get_by_uuid_for_user(test_uuid, mock_user)

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)


class TestIntegrationDeleteByUuidForUser:
    @patch.object(Integration, "soft_delete")
    def test_delete_by_uuid_for_user_soft_deletes(self, mock_soft_delete):
        mock_query = MagicMock()
        mock_soft_delete.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.execute.return_value = 1

        mock_user = Mock()
        test_uuid = "test-uuid"
        Integration.delete_by_uuid_for_user(test_uuid, mock_user)

        mock_soft_delete.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.execute.assert_called_once()


class TestIntegrationGetByPlatformUserId:
    @patch.object(Integration, "select_query")
    def test_get_by_platform_user_id_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.first.return_value = None

        Integration.get_by_platform_user_id("platform_user_123", "instagram")

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.first.assert_called_once()


class TestIntegrationCreateOrUpdateIntegration:
    @patch.object(Integration, "select")
    @patch.object(Integration, "create")
    def test_create_integration_with_all_params(self, mock_create, mock_select):
        # Mock select to return nothing (new integration)
        mock_select_result = MagicMock()
        mock_select.return_value = mock_select_result
        mock_select_result.where.return_value.first.return_value = None

        mock_user = Mock()
        mock_integration = Mock()
        mock_create.return_value = mock_integration

        expires_at = datetime.now() + timedelta(hours=1)
        refresh_expires_at = datetime.now() + timedelta(days=60)

        result = Integration.create_or_update_integration(
            user=mock_user,
            platform_user_id="platform_123",
            platform="instagram",
            access_token="access_token_abc",
            expires_at=expires_at,
            token_type="Bearer",
            scopes=["read", "write"],
            refresh_token="refresh_token_xyz",
            refresh_token_expires_at=refresh_expires_at,
        )

        assert result == mock_integration
        mock_create.assert_called_once_with(
            user=mock_user,
            platform_user_id="platform_123",
            platform="instagram",
            access_token="access_token_abc",
            refresh_token="refresh_token_xyz",
            expires_at=expires_at,
            token_type="Bearer",
            scopes=["read", "write"],
            refresh_token_expires_at=refresh_expires_at,
            platform_username=None,
        )

    @patch.object(Integration, "select")
    @patch.object(Integration, "create")
    def test_create_integration_without_refresh_token(self, mock_create, mock_select):
        # Mock select to return nothing (new integration)
        mock_select_result = MagicMock()
        mock_select.return_value = mock_select_result
        mock_select_result.where.return_value.first.return_value = None

        mock_user = Mock()
        mock_integration = Mock()
        mock_create.return_value = mock_integration

        expires_at = datetime.now() + timedelta(hours=1)

        result = Integration.create_or_update_integration(
            user=mock_user,
            platform_user_id="youtube_123",
            platform="youtube",
            access_token="access_token_abc",
            expires_at=expires_at,
            token_type="Bearer",
            scopes=["read"],
        )

        assert result == mock_integration
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["refresh_token"] is None
        assert call_kwargs["refresh_token_expires_at"] is None
        assert call_kwargs["platform_username"] is None

    @patch.object(Integration, "select")
    def test_update_existing_integration(self, mock_select):
        # Mock select to return an existing integration
        mock_existing = MagicMock(spec=Integration)
        mock_select_result = MagicMock()
        mock_select.return_value = mock_select_result
        mock_select_result.where.return_value.first.return_value = mock_existing

        mock_user = Mock()
        expires_at = datetime.now() + timedelta(hours=1)

        result = Integration.create_or_update_integration(
            user=mock_user,
            platform_user_id="platform_123",
            platform="instagram",
            access_token="new_token",
            expires_at=expires_at,
            token_type="Bearer",
            scopes=["read"],
        )

        assert result == mock_existing
        assert mock_existing.access_token == "new_token"
        assert mock_existing.user == mock_user
        mock_existing.save.assert_called_once()


class TestIntegrationGetDetails:
    def test_get_details_with_active_token(self):
        integration = Integration()
        integration.uuid = "test-uuid-123"
        integration.platform = "instagram"
        integration.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Future date = active
        integration.token_type = "Bearer"
        integration.created_at = datetime(2024, 1, 1, 12, 0, 0)

        result = integration.get_details()

        assert result["uuid"] == "test-uuid-123"
        assert result["platform"] == "instagram"
        assert result["status"] == "active"
        assert result["token_type"] == "Bearer"
        assert result["created_at"] == "2024-01-01T12:00:00"
        assert result["platform_username"] is None

    def test_get_details_with_expired_token(self):
        integration = Integration()
        integration.uuid = "test-uuid-456"
        integration.platform = "youtube"
        integration.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)  # Past date = inactive
        integration.token_type = "Bearer"
        integration.created_at = datetime(2024, 1, 1, 12, 0, 0)

        result = integration.get_details()

        assert result["uuid"] == "test-uuid-456"
        assert result["platform"] == "youtube"
        assert result["status"] == "inactive"
        assert result["token_type"] == "Bearer"

    def test_get_details_returns_all_required_fields(self):
        integration = Integration()
        integration.uuid = "uuid-789"
        integration.platform = "instagram"
        integration.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        integration.token_type = "Bearer"
        integration.created_at = datetime(2024, 1, 1)

        result = integration.get_details()

        assert "uuid" in result
        assert "platform" in result
        assert "status" in result
        assert "token_type" in result
        assert "created_at" in result
