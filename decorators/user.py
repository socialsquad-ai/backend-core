from functools import wraps

from fastapi import Request

from data_adapter.user import User
from logger.logging import LoggerUtil
from utils.auth0_service import Auth0Service
from utils.contextvar import set_context_user
from utils.exceptions import CustomUnauthorized


def require_authentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Locate the Request object in the function's arguments.
        request = kwargs.get("request")

        # If not in kwargs, check in args
        if request is None:
            request = next((arg for arg in args if isinstance(arg, Request)), None)
        if request is None:
            LoggerUtil.create_error_log("No request object found in function arguments")
            raise CustomUnauthorized(detail="Authentication required")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            LoggerUtil.create_error_log("No Authorization header found")
            raise CustomUnauthorized(detail="Authorization header required")

        try:
            # Create Auth0Service instance and validate the token
            auth0_service = Auth0Service()
            token_payload = auth0_service.validate_token(auth_header)

            # Store user information in request state for potential use in the endpoint
            request.state.user = token_payload
            set_context_user(User.get_by_auth0_user_id(token_payload.get("sub")))
            # set_context_user(User.get_by_email("milind@socialsquad.ai").get())

            LoggerUtil.create_info_log(f"Authentication successful for user: {token_payload.get('sub', 'unknown')}")

        except CustomUnauthorized:
            # Re-raise the exception as it's already properly formatted
            raise
        except Exception as e:
            LoggerUtil.create_error_log(f"Unexpected authentication error: {e}")
            raise CustomUnauthorized(detail="Authentication failed")

        return await func(*args, **kwargs)

    return wrapper
