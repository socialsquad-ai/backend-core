from functools import wraps
from fastapi import Request
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
            raise CustomUnauthorized()
        auth_header = request.headers.get("Authorization")
        # TODO :: Add the logic to check the token
        if not auth_header or auth_header != "Bearer valid_token":
            raise CustomUnauthorized()

        return await func(*args, **kwargs)

    return wrapper
