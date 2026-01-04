"""
Unit tests for data_adapter/integration.py

Tests cover all methods in the Integration model including:
- get_all_for_user
- get_by_uuid_for_user
- delete_by_uuid_for_user
- get_by_platform_user_id
- create_integration
- get_details
"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from data_adapter.integration import Integration


class TestGetAllForUser:
    """Test cases for get_all_for_user method"""

    @patch.object(Integration, "select_query")
    def test_get_all_for_user_success(self, mock_select_query):
        """Test getting all integrations for a user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        result = Integration.get_all_for_user(mock_user)

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        assert result == mock_query.where.return_value

    @patch.object(Integration, "select_query")
    def test_get_all_for_user_empty_result(self, mock_select_query):
        """Test getting integrations when none exist"""
        # Arrange
        mock_user = Mock(id=999)
        mock_query = Mock()
        mock_query.where.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = Integration.get_all_for_user(mock_user)

        # Assert
        assert result == []


class TestGetByUuidForUser:
    """Test cases for get_by_uuid_for_user method"""

    @patch.object(Integration, "select_query")
    def test_get_by_uuid_for_user_success(self, mock_select_query):
        """Test getting integration by UUID for a user"""
        # Arrange
        mock_user = Mock(id=1)
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Integration.get_by_uuid_for_user(test_uuid, mock_user)

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)

    @patch.object(Integration, "select_query")
    def test_get_by_uuid_for_user_not_found(self, mock_select_query):
        """Test getting integration with invalid UUID"""
        # Arrange
        mock_user = Mock(id=1)
        test_uuid = "invalid-uuid"
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = Integration.get_by_uuid_for_user(test_uuid, mock_user)

        # Assert
        assert result == []


class TestDeleteByUuidForUser:
    """Test cases for delete_by_uuid_for_user method"""

    @patch.object(Integration, "soft_delete")
    def test_delete_by_uuid_for_user_success(self, mock_soft_delete):
        """Test soft deleting integration by UUID for a user"""
        # Arrange
        mock_user = Mock(id=1)
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_query = Mock()
        mock_soft_delete.return_value = mock_query
        mock_query.where.return_value.execute.return_value = 1

        # Act
        result = Integration.delete_by_uuid_for_user(test_uuid, mock_user)

        # Assert
        mock_soft_delete.assert_called_once()
        mock_query.where.assert_called_once()
        assert result == 1

    @patch.object(Integration, "soft_delete")
    def test_delete_by_uuid_for_user_not_found(self, mock_soft_delete):
        """Test deleting non-existent integration"""
        # Arrange
        mock_user = Mock(id=1)
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_query = Mock()
        mock_soft_delete.return_value = mock_query
        mock_query.where.return_value.execute.return_value = 0

        # Act
        result = Integration.delete_by_uuid_for_user(test_uuid, mock_user)

        # Assert
        assert result == 0


class TestGetByPlatformUserId:
    """Test cases for get_by_platform_user_id method"""

    @patch.object(Integration, "select_query")
    def test_get_by_platform_user_id_success(self, mock_select_query):
        """Test getting integration by platform user ID"""
        # Arrange
        mock_integration = Mock(platform_user_id="instagram_123", platform="instagram")
        mock_query = Mock()
        mock_query.where.return_value.first.return_value = mock_integration
        mock_select_query.return_value = mock_query

        # Act
        result = Integration.get_by_platform_user_id("instagram_123", "instagram")

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        assert result == mock_integration

    @patch.object(Integration, "select_query")
    def test_get_by_platform_user_id_not_found(self, mock_select_query):
        """Test getting integration with invalid platform user ID"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.first.return_value = None
        mock_select_query.return_value = mock_query

        # Act
        result = Integration.get_by_platform_user_id("invalid_id", "instagram")

        # Assert
        assert result is None

    @patch.object(Integration, "select_query")
    def test_get_by_platform_user_id_different_platforms(self, mock_select_query):
        """Test querying different platforms"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        Integration.get_by_platform_user_id("user_123", "youtube")

        # Assert
        # Verify the where clause is called with both platform_user_id and platform
        mock_query.where.assert_called_once()


class TestCreateIntegration:
    """Test cases for create_integration method"""

    @patch.object(Integration, "create")
    def test_create_integration_with_all_fields(self, mock_create):
        """Test creating integration with all fields"""
        # Arrange
        mock_user = Mock(id=1)
        mock_integration = Mock(id=1)
        mock_create.return_value = mock_integration

        expires_at = datetime.now() + timedelta(days=30)
        refresh_token_expires_at = datetime.now() + timedelta(days=60)

        # Act
        result = Integration.create_integration(
            user=mock_user,
            platform_user_id="instagram_123",
            platform="instagram",
            access_token="access_token_123",
            expires_at=expires_at,
            token_type="bearer",
            scopes=["instagram_basic", "instagram_manage_comments"],
            refresh_token="refresh_token_123",
            refresh_token_expires_at=refresh_token_expires_at,
        )

        # Assert
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["user"] == mock_user
        assert call_kwargs["platform_user_id"] == "instagram_123"
        assert call_kwargs["platform"] == "instagram"
        assert call_kwargs["access_token"] == "access_token_123"
        assert call_kwargs["refresh_token"] == "refresh_token_123"
        assert result == mock_integration

    @patch.object(Integration, "create")
    def test_create_integration_without_refresh_token(self, mock_create):
        """Test creating integration without refresh token"""
        # Arrange
        mock_user = Mock(id=1)
        mock_integration = Mock(id=1)
        mock_create.return_value = mock_integration

        expires_at = datetime.now() + timedelta(days=30)

        # Act
        _result = Integration.create_integration(
            user=mock_user,
            platform_user_id="youtube_123",
            platform="youtube",
            access_token="access_token_123",
            expires_at=expires_at,
            token_type="bearer",
            scopes=["youtube.readonly"],
        )

        # Assert
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["refresh_token"] is None
        assert call_kwargs["refresh_token_expires_at"] is None

    @patch.object(Integration, "create")
    def test_create_integration_different_platforms(self, mock_create):
        """Test creating integrations for different platforms"""
        # Arrange
        mock_user = Mock(id=1)
        mock_create.return_value = Mock()
        expires_at = datetime.now() + timedelta(days=30)

        # Act - Instagram
        Integration.create_integration(
            user=mock_user,
            platform_user_id="instagram_123",
            platform="instagram",
            access_token="token1",
            expires_at=expires_at,
            token_type="bearer",
            scopes=["instagram_basic"],
        )

        # Act - YouTube
        Integration.create_integration(
            user=mock_user,
            platform_user_id="youtube_123",
            platform="youtube",
            access_token="token2",
            expires_at=expires_at,
            token_type="bearer",
            scopes=["youtube.readonly"],
        )

        # Assert
        assert mock_create.call_count == 2


class TestGetDetails:
    """Test cases for get_details method"""

    def test_get_details_active_token(self):
        """Test get_details with active token"""
        # Arrange
        future_time = datetime.now() + timedelta(days=30)
        mock_integration = Mock(spec=Integration)
        mock_integration.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_integration.platform = "instagram"
        mock_integration.expires_at = future_time
        mock_integration.token_type = "bearer"
        mock_integration.created_at = datetime.now()

        # Bind the method to the instance
        mock_integration.get_details = Integration.get_details.__get__(mock_integration, Integration)

        # Act
        result = mock_integration.get_details()

        # Assert
        assert result["uuid"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["platform"] == "instagram"
        assert result["status"] == "active"
        assert result["token_type"] == "bearer"
        assert "created_at" in result

    def test_get_details_inactive_token(self):
        """Test get_details with expired token"""
        # Arrange
        past_time = datetime.now() - timedelta(days=1)
        mock_integration = Mock(spec=Integration)
        mock_integration.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_integration.platform = "youtube"
        mock_integration.expires_at = past_time
        mock_integration.token_type = "bearer"
        mock_integration.created_at = datetime.now()

        # Bind the method to the instance
        mock_integration.get_details = Integration.get_details.__get__(mock_integration, Integration)

        # Act
        result = mock_integration.get_details()

        # Assert
        assert result["status"] == "inactive"

    def test_get_details_returns_all_fields(self):
        """Test that get_details returns all required fields"""
        # Arrange
        mock_integration = Mock(spec=Integration)
        mock_integration.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_integration.platform = "instagram"
        mock_integration.expires_at = datetime.now() + timedelta(days=30)
        mock_integration.token_type = "bearer"
        mock_integration.created_at = datetime(2024, 1, 1, 12, 0, 0)

        # Bind the method to the instance
        mock_integration.get_details = Integration.get_details.__get__(mock_integration, Integration)

        # Act
        result = mock_integration.get_details()

        # Assert
        assert "uuid" in result
        assert "platform" in result
        assert "status" in result
        assert "token_type" in result
        assert "created_at" in result
        assert len(result) == 5
