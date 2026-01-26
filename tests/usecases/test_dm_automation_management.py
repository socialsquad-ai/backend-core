import pytest
from unittest.mock import Mock, patch

from usecases.dm_automation_management import DmAutomationManagement
from utils.exceptions import CustomBadRequest, ResourceNotFound, CustomUnauthorized


@pytest.fixture
def mock_user():
    user = Mock()
    user.id = 1
    return user


@pytest.fixture
def mock_integration(mock_user):
    integration = Mock()
    integration.id = 1
    integration.user = mock_user
    return integration


@pytest.fixture
def mock_post(mock_integration):
    post = Mock()
    post.id = 1
    post.post_id = "post123"
    post.integration = mock_integration
    return post


class TestCreateDmAutomationRule:
    @patch("usecases.dm_automation_management.Integration.get_by_uuid_for_user")
    @patch("usecases.dm_automation_management.DmAutomationRule.create")
    def test_create_dm_rule_for_integration_success(
        self, mock_create_rule, mock_get_integration, mock_user, mock_integration
    ):
        mock_get_integration.return_value.first.return_value = mock_integration
        mock_rule = Mock()
        mock_rule.get_details.return_value = {"id": 1, "trigger_type": "dm"}
        mock_create_rule.return_value = mock_rule

        rule_data = {
            "trigger_type": "dm",
            "trigger_text": "hello",
            "dm_response": "hi there",
        }
        result = DmAutomationManagement.create_dm_automation_rule(
            mock_user, rule_data, integration_uuid="int-uuid"
        )

        assert result["trigger_type"] == "dm"
        mock_create_rule.assert_called_once()

    @patch("usecases.dm_automation_management.Post.get_by_post_id")
    @patch("usecases.dm_automation_management.DmAutomationRule.create")
    def test_create_comment_rule_for_post_success(
        self, mock_create_rule, mock_get_post, mock_user, mock_post
    ):
        mock_get_post.return_value.first.return_value = mock_post
        mock_rule = Mock()
        mock_rule.get_details.return_value = {"id": 1, "trigger_type": "comment"}
        mock_create_rule.return_value = mock_rule

        rule_data = {
            "post_id": "post123",
            "trigger_type": "comment",
            "match_type": "EXACT_TEXT",
            "trigger_text": "hello",
            "dm_response": "hi there",
        }
        result = DmAutomationManagement.create_dm_automation_rule(mock_user, rule_data)

        assert result["trigger_type"] == "comment"
        mock_create_rule.assert_called_once()

    @patch("usecases.dm_automation_management.Integration.get_by_uuid_for_user")
    def test_create_rule_integration_not_found(self, mock_get_integration, mock_user):
        mock_get_integration.return_value.first.return_value = None
        with pytest.raises(ResourceNotFound, match="Integration not found."):
            DmAutomationManagement.create_dm_automation_rule(
                mock_user, {"trigger_type": "dm"}, integration_uuid="int-uuid"
            )

    def test_create_comment_rule_no_post_id(self, mock_user):
        rule_data = {
            "trigger_type": "comment",
            "match_type": "EXACT_TEXT",
        }
        with pytest.raises(CustomBadRequest, match="`post_id` is required for 'comment' trigger type."):
            DmAutomationManagement.create_dm_automation_rule(mock_user, rule_data)

    @patch("usecases.dm_automation_management.Post.get_by_post_id")
    def test_create_comment_rule_post_not_found(self, mock_get_post, mock_user):
        mock_get_post.return_value.first.return_value = None
        rule_data = {
            "post_id": "post123",
            "trigger_type": "comment",
            "match_type": "EXACT_TEXT",
        }
        with pytest.raises(ResourceNotFound, match="Post not found."):
            DmAutomationManagement.create_dm_automation_rule(mock_user, rule_data)

    @patch("usecases.dm_automation_management.Post.get_by_post_id")
    def test_create_comment_rule_unauthorized(self, mock_get_post, mock_user, mock_post):
        unauthorized_user = Mock()
        unauthorized_user.id = 2
        mock_get_post.return_value.first.return_value = mock_post
        rule_data = {
            "post_id": "post123",
            "trigger_type": "comment",
            "match_type": "EXACT_TEXT",
        }
        with pytest.raises(CustomUnauthorized, match="User not authorized for this post."):
            DmAutomationManagement.create_dm_automation_rule(unauthorized_user, rule_data)

    @patch("usecases.dm_automation_management.Integration.get_by_uuid_for_user")
    def test_create_dm_rule_with_post_id(self, mock_get_integration, mock_user):
        mock_get_integration.return_value.first.return_value = Mock()
        rule_data = {
            "post_id": "post123",
            "trigger_type": "dm",
        }
        with pytest.raises(CustomBadRequest, match="`post_id` is not allowed for 'dm' trigger type."):
            DmAutomationManagement.create_dm_automation_rule(
                mock_user, rule_data, integration_uuid="int-uuid"
            )
