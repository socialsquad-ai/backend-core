from data_adapter.user import User
from utils.contextvar import get_request_json_post_payload
from fastapi import Request
from utils.error_messages import RESOURCE_NOT_FOUND, INVALID_UUID
from utils.util import is_valid_uuid_v4


class UserManagement:
    @staticmethod
    def create_user(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        timezone = payload["timezone"]
        password = payload["password"]
        user = User.get_or_create_user(email, timezone, password)
        return "", user.get_details(), None

    @staticmethod
    def get_user_by_email(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        user = User.get_by_email(email)
        if not user:
            return RESOURCE_NOT_FOUND, None, None
        return "", user[0].get_details(), None

    @staticmethod
    def get_user_by_uuid(request: Request, user_uuid: str):
        user = User.get_by_uuid(user_uuid)
        if not is_valid_uuid_v4(user_uuid):
            return INVALID_UUID, None, None
        if not user:
            return RESOURCE_NOT_FOUND, None, None
        return "", {"user": user[0].get_details()}, None

    @staticmethod
    def get_users(request: Request):
        users = User.get_all_users()
        if not users:
            return "No users found", None, None
        return "", {"users": [user.get_details() for user in users]}, None
