import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from server.app import app
from config.non_env import API_VERSION_V1
from data_adapter.user import User


@pytest.fixture(autouse=True)
def mock_auth_and_user():
    with patch("decorators.user.Auth0Service.validate_token") as mock_validate, \
         patch("data_adapter.user.User.get_by_auth0_user_id") as mock_get_user:
        mock_validate.return_value = {"sub": "auth0|123"}
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_get_user.return_value = mock_user
        yield


client = TestClient(app)


class TestDmAutomationController:
    @patch("usecases.dm_automation_management.DmAutomationManagement.get_dm_automation_rules_for_integration")
    def test_get_integration_dm_rules_success(
        self, mock_get_rules
    ):
        mock_get_rules.return_value = [{"id": 1, "trigger_type": "dm"}]
        response = client.get(
            f"{API_VERSION_V1}/integrations/some-uuid/dm-automations",
            headers={"Authorization": "Bearer dummy-token"},
        )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["data"][0]["trigger_type"] == "dm"
        mock_get_rules.assert_called_once()

    @patch("usecases.dm_automation_management.DmAutomationManagement.create_dm_automation_rule")
    def test_create_integration_dm_rule_success(
        self, mock_create_rule
    ):
        mock_create_rule.return_value = {"id": 1, "trigger_type": "dm"}
        payload = {
            "trigger_type": "dm",
            "trigger_text": "hello",
            "dm_response": "hi there",
        }
        response = client.post(
            f"{API_VERSION_V1}/integrations/some-uuid/dm-automations",
            json=payload,
            headers={"Authorization": "Bearer dummy-token"},
        )
        assert response.status_code == 201
        json_response = response.json()
        assert json_response["data"]["trigger_type"] == "dm"
        mock_create_rule.assert_called_once()

    @patch("usecases.dm_automation_management.DmAutomationManagement.create_dm_automation_rule")
    def test_create_post_dm_rule_success(self, mock_create_rule):
        mock_create_rule.return_value = {"id": 1, "trigger_type": "comment"}
        payload = {
            "trigger_type": "comment",
            "match_type": "EXACT_TEXT",
            "trigger_text": "hello",
            "dm_response": "hi there",
        }
        response = client.post(
            f"{API_VERSION_V1}/posts/post123/dm-automations",
            json=payload,
            headers={"Authorization": "Bearer dummy-token"},
        )
        assert response.status_code == 201
        json_response = response.json()
        assert json_response["data"]["trigger_type"] == "comment"
        mock_create_rule.assert_called_once()

    @patch("usecases.dm_automation_management.DmAutomationManagement.update_dm_automation_rule")
    def test_update_dm_rule_success(self, mock_update_rule):
        mock_update_rule.return_value = {"id": 1, "is_active": False}
        payload = {"is_active": False}
        response = client.put(
            f"{API_VERSION_V1}/dm-automations/some-rule-uuid",
            json=payload,
            headers={"Authorization": "Bearer dummy-token"},
        )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["data"]["is_active"] is False
        mock_update_rule.assert_called_once()

    @patch("usecases.dm_automation_management.DmAutomationManagement.delete_dm_automation_rule")
    def test_delete_dm_rule_success(self, mock_delete_rule):
        mock_delete_rule.return_value = None
        response = client.delete(
            f"{API_VERSION_V1}/dm-automations/some-rule-uuid",
            headers={"Authorization": "Bearer dummy-token"},
        )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["message"] == "Rule deleted successfully."
        mock_delete_rule.assert_called_once()
