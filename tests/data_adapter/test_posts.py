"""
Unit tests for data_adapter/posts.py

Tests cover all methods in the Post model including:
- get_by_post_id
- get_by_integration
- get_details
"""

from datetime import time
from unittest.mock import Mock, patch

from data_adapter.posts import Post


class TestGetByPostId:
    """Test cases for get_by_post_id method"""

    @patch.object(Post, "select_query")
    def test_get_by_post_id_success(self, mock_select_query):
        """Test getting post by post_id"""
        # Arrange
        mock_post = Mock(post_id="post_123")
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_post]
        mock_select_query.return_value = mock_query

        # Act
        result = Post.get_by_post_id("post_123")

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)
        assert result == [mock_post]

    @patch.object(Post, "select_query")
    def test_get_by_post_id_not_found(self, mock_select_query):
        """Test getting post with invalid post_id"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = Post.get_by_post_id("invalid_post_id")

        # Assert
        assert result == []

    @patch.object(Post, "select_query")
    def test_get_by_post_id_different_ids(self, mock_select_query):
        """Test querying different post IDs"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        Post.get_by_post_id("post_1")
        Post.get_by_post_id("post_2")
        Post.get_by_post_id("post_3")

        # Assert
        assert mock_select_query.call_count == 3


class TestGetByIntegration:
    """Test cases for get_by_integration method"""

    @patch.object(Post, "select_query")
    def test_get_by_integration_success(self, mock_select_query):
        """Test getting posts by integration"""
        # Arrange
        mock_integration = Mock(id=1)
        mock_post1 = Mock(post_id="post_1", integration=mock_integration)
        mock_post2 = Mock(post_id="post_2", integration=mock_integration)
        mock_query = Mock()
        mock_query.where.return_value = [mock_post1, mock_post2]
        mock_select_query.return_value = mock_query

        # Act
        result = Post.get_by_integration(mock_integration)

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        assert len(result) == 2

    @patch.object(Post, "select_query")
    def test_get_by_integration_no_posts(self, mock_select_query):
        """Test getting posts when integration has no posts"""
        # Arrange
        mock_integration = Mock(id=999)
        mock_query = Mock()
        mock_query.where.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = Post.get_by_integration(mock_integration)

        # Assert
        assert result == []

    @patch.object(Post, "select_query")
    def test_get_by_integration_different_integrations(self, mock_select_query):
        """Test querying posts for different integrations"""
        # Arrange
        mock_integration1 = Mock(id=1)
        mock_integration2 = Mock(id=2)
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        Post.get_by_integration(mock_integration1)
        Post.get_by_integration(mock_integration2)

        # Assert
        assert mock_select_query.call_count == 2


class TestGetDetails:
    """Test cases for get_details method"""

    def test_get_details_complete_data(self):
        """Test get_details with complete data"""
        # Arrange
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"uuid": "integration_uuid", "platform": "instagram"}

        mock_post = Mock(spec=Post)
        mock_post.post_id = "post_123"
        mock_post.integration = mock_integration
        mock_post.ignore_instructions = "ignore spam and promotional comments"
        mock_post.engagement_enabled = True
        mock_post.engagement_start_hours = time(12, 0)
        mock_post.engagement_end_hours = time(14, 0)

        # Bind the method to the instance
        mock_post.get_details = Post.get_details.__get__(mock_post, Post)

        # Act
        result = mock_post.get_details()

        # Assert
        assert result["post_id"] == "post_123"
        assert result["integration"]["uuid"] == "integration_uuid"
        assert result["ignore_instructions"] == "ignore spam and promotional comments"
        assert result["engagement_enabled"] is True
        assert result["engagement_start_hours"] == time(12, 0)
        assert result["engagement_end_hours"] == time(14, 0)

    def test_get_details_engagement_disabled(self):
        """Test get_details when engagement is disabled"""
        # Arrange
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"uuid": "integration_uuid"}

        mock_post = Mock(spec=Post)
        mock_post.post_id = "post_456"
        mock_post.integration = mock_integration
        mock_post.ignore_instructions = ""
        mock_post.engagement_enabled = False
        mock_post.engagement_start_hours = time(12, 0)
        mock_post.engagement_end_hours = time(14, 0)

        # Bind the method to the instance
        mock_post.get_details = Post.get_details.__get__(mock_post, Post)

        # Act
        result = mock_post.get_details()

        # Assert
        assert result["engagement_enabled"] is False

    def test_get_details_empty_ignore_instructions(self):
        """Test get_details with empty ignore instructions"""
        # Arrange
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"uuid": "integration_uuid"}

        mock_post = Mock(spec=Post)
        mock_post.post_id = "post_789"
        mock_post.integration = mock_integration
        mock_post.ignore_instructions = ""
        mock_post.engagement_enabled = True
        mock_post.engagement_start_hours = time(9, 0)
        mock_post.engagement_end_hours = time(17, 0)

        # Bind the method to the instance
        mock_post.get_details = Post.get_details.__get__(mock_post, Post)

        # Act
        result = mock_post.get_details()

        # Assert
        assert result["ignore_instructions"] == ""

    def test_get_details_all_fields_present(self):
        """Test that get_details returns all required fields"""
        # Arrange
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"uuid": "uuid"}

        mock_post = Mock(spec=Post)
        mock_post.post_id = "post_123"
        mock_post.integration = mock_integration
        mock_post.ignore_instructions = "test"
        mock_post.engagement_enabled = True
        mock_post.engagement_start_hours = time(12, 0)
        mock_post.engagement_end_hours = time(14, 0)

        # Bind the method to the instance
        mock_post.get_details = Post.get_details.__get__(mock_post, Post)

        # Act
        result = mock_post.get_details()

        # Assert
        required_fields = ["post_id", "integration", "ignore_instructions", "engagement_enabled", "engagement_start_hours", "engagement_end_hours"]
        for field in required_fields:
            assert field in result

    def test_get_details_custom_time_window(self):
        """Test get_details with custom engagement time window"""
        # Arrange
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"uuid": "uuid"}

        mock_post = Mock(spec=Post)
        mock_post.post_id = "post_custom"
        mock_post.integration = mock_integration
        mock_post.ignore_instructions = "custom instructions"
        mock_post.engagement_enabled = True
        mock_post.engagement_start_hours = time(8, 30)
        mock_post.engagement_end_hours = time(20, 45)

        # Bind the method to the instance
        mock_post.get_details = Post.get_details.__get__(mock_post, Post)

        # Act
        result = mock_post.get_details()

        # Assert
        assert result["engagement_start_hours"] == time(8, 30)
        assert result["engagement_end_hours"] == time(20, 45)
