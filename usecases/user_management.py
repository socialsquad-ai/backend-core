from data_adapter.user import User
from data_adapter.account import Account
from utils.contextvar import get_request_json_post_payload, get_request_metadata
from fastapi import Request
from utils.error_messages import RESOURCE_NOT_FOUND, INVALID_RESOURCE_ID
from utils.util import is_valid_uuid_v4
from decorators.common import run_in_background
from peewee import IntegrityError
import datetime
from data_adapter.db import ssq_db


class UserManagement:
    @staticmethod
    @ssq_db.atomic()
    def create_user(request: Request):
        payload = get_request_json_post_payload()
        email = payload["email"]
        auth0_user_id = payload["auth0_user_id"]
        name = payload.get("name", email.split("@")[0])
        signup_method = payload["signup_method"]
        email_verified = payload["email_verified"]
        auth0_created_at = payload.get(
            "auth0_created_at", datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        account_uuid = payload.get("account_uuid")
        try:
            # If we're adding a user to an existing account, use the existing account
            if account_uuid:
                account = Account.get_by_uuid(account_uuid)
            else:
                account = Account.get_or_create_account(name, email)
            if not account:
                return "", None, "Account not found"

            user = User.get_or_create_user_from_auth0(
                auth0_user_id,
                name,
                email,
                signup_method,
                email_verified,
                auth0_created_at,
                account,
            )
            return "", user.get_details(), None
        except IntegrityError:
            return "", None, "User already exists"
        except Exception as e:
            return "", None, e

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
