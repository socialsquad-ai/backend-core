import datetime

from fastapi import Request
from peewee import IntegrityError

from data_adapter.db import ssq_db
from data_adapter.user import User
from utils.contextvar import get_context_user, get_request_json_post_payload
from utils.error_messages import INVALID_RESOURCE_ID, RESOURCE_NOT_FOUND
from utils.util import is_valid_uuid_v4


class UserManagement:
    @staticmethod
    def get_profile(request: Request):
        user = get_context_user()
        if not user:
            return RESOURCE_NOT_FOUND, None, None
        return "", user.get_details(), None

    @staticmethod
    @ssq_db.atomic()
    def create_user(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        auth0_user_id = payload["auth0_user_id"]
        name = payload.get("name", email.split("@")[0])
        signup_method = payload["signup_method"]
        email_verified = payload["email_verified"]
        auth0_created_at = payload.get("auth0_created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
        try:
            user = User.get_or_create_user_from_auth0(
                auth0_user_id,
                name,
                email,
                signup_method,
                email_verified,
                auth0_created_at,
            )
            return "", user.get_details(), None
        except IntegrityError:
            return "", None, "User already exists"
        except Exception as e:
            # Convert exception to string to make it JSON serializable
            error_message = str(e)
            return "", None, error_message

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
            return INVALID_RESOURCE_ID, None, None
        if not user:
            return RESOURCE_NOT_FOUND, None, None
        return "", {"user": user[0].get_details()}, None

    @staticmethod
    def get_users(request: Request):
        users = User.get_all_users()
        if not users:
            return "No users found", None, None
        return "", {"users": [user.get_details() for user in users]}, None
