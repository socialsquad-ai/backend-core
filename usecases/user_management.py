from data_adapter.user import User
from utils.contextvar import get_request_json_post_payload
from fastapi import Request


class UserManagement:
    @staticmethod
    def create_user(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        timezone = payload["timezone"]
        user = User.get_or_create_user(email, timezone)
        return "", user.get_details(), None

    @staticmethod
    def get_user_by_email(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        user = User.get_by_email(email)
        if not user:
            return "User not found", None, None
        return "", user.get_details(), None
