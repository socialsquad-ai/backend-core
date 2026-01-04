from datetime import time
from unittest.mock import MagicMock, Mock, patch

from data_adapter.posts import Post


class TestPostGetByPostId:
    @patch.object(Post, "select_query")
    def test_get_by_post_id_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        Post.get_by_post_id("post_123")

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)


class TestPostGetByIntegration:
    @patch.object(Post, "select_query")
    def test_get_by_integration_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.where.return_value = []

        mock_integration = Mock()
        Post.get_by_integration(mock_integration)

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()


class TestPostGetDetails:
    @patch.object(Post, "integration", create=True)
    def test_get_details_returns_all_fields(self, mock_integration_field):
        mock_integration = Mock()
        mock_integration.get_details.return_value = {
            "uuid": "integration-uuid",
            "platform": "instagram",
        }

        post = Post()
        post._data = {"integration": mock_integration}
        post.post_id = "post_123"
        post.ignore_instructions = "Don't reply to spam"
        post.engagement_enabled = True
        post.engagement_start_hours = time(12, 0)
        post.engagement_end_hours = time(14, 0)

        with patch.object(type(post), "integration", mock_integration, create=True):
            result = post.get_details()

        assert result["post_id"] == "post_123"
        assert result["integration"] == {"uuid": "integration-uuid", "platform": "instagram"}
        assert result["ignore_instructions"] == "Don't reply to spam"
        assert result["engagement_enabled"] is True
        assert result["engagement_start_hours"] == time(12, 0)
        assert result["engagement_end_hours"] == time(14, 0)

    @patch.object(Post, "integration", create=True)
    def test_get_details_with_empty_ignore_instructions(self, mock_integration_field):
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"platform": "youtube"}

        post = Post()
        post.post_id = "post_456"
        post.ignore_instructions = ""
        post.engagement_enabled = False
        post.engagement_start_hours = time(9, 0)
        post.engagement_end_hours = time(17, 0)

        with patch.object(type(post), "integration", mock_integration, create=True):
            result = post.get_details()

        assert result["post_id"] == "post_456"
        assert result["ignore_instructions"] == ""
        assert result["engagement_enabled"] is False

    @patch.object(Post, "integration", create=True)
    def test_get_details_calls_integration_get_details(self, mock_integration_field):
        mock_integration = Mock()
        mock_integration.get_details.return_value = {"test": "data"}

        post = Post()
        post.post_id = "post_789"
        post.ignore_instructions = ""
        post.engagement_enabled = True
        post.engagement_start_hours = time(10, 0)
        post.engagement_end_hours = time(12, 0)

        with patch.object(type(post), "integration", mock_integration, create=True):
            result = post.get_details()

        mock_integration.get_details.assert_called_once()
        assert result["integration"] == {"test": "data"}

    @patch.object(Post, "integration", create=True)
    def test_get_details_includes_all_required_keys(self, mock_integration_field):
        mock_integration = Mock()
        mock_integration.get_details.return_value = {}

        post = Post()
        post.post_id = "post_000"
        post.ignore_instructions = "test"
        post.engagement_enabled = False
        post.engagement_start_hours = time(0, 0)
        post.engagement_end_hours = time(23, 59)

        with patch.object(type(post), "integration", mock_integration, create=True):
            result = post.get_details()

        assert "post_id" in result
        assert "integration" in result
        assert "ignore_instructions" in result
        assert "engagement_enabled" in result
        assert "engagement_start_hours" in result
        assert "engagement_end_hours" in result
