import asyncio
from functools import wraps
from typing import Any, Dict, Type

from fastapi import Request

from config import env
from controller.cerberus import CustomValidator
from logger.logging import LoggerUtil
from utils.contextvar import get_request_json_post_payload
from utils.exceptions import CustomBadRequest, CustomUnauthorized


def validate_json_payload(payload_validation_schema: dict):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # default values
            is_validated = False
            v = None
            try:
                post_payload = get_request_json_post_payload()
                v = CustomValidator(
                    schema=payload_validation_schema,
                    allow_unknown=True,
                    require_all=True,
                )
                is_validated = v.validate(post_payload)
            except Exception as e:
                LoggerUtil.create_error_log(
                    "BAD_REQUEST_EXCEPTION: {}".format(e),
                )
                raise CustomBadRequest(detail="Invalid json payload")
            if not is_validated:
                LoggerUtil.create_error_log(
                    "BAD_REQUEST:Payload:{},Error:{}".format(post_payload, v.errors),
                )
                raise CustomBadRequest(detail="Invalid payload", errors=v.errors if v else None)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_query_params(validation_schema: dict):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if request is None:
                request = next((arg for arg in args if isinstance(arg, Request)), None)

            if request:
                query_params = dict(request.query_params)
                v = None
                try:
                    v = CustomValidator(
                        schema=validation_schema,
                        allow_unknown=True,
                        require_all=False,
                    )
                    is_validated = v.validate(query_params)
                except Exception as e:
                    LoggerUtil.create_error_log(
                        "BAD_REQUEST_EXCEPTION: {}".format(e),
                    )
                    raise CustomBadRequest(detail="Invalid query parameters")

                if not is_validated:
                    LoggerUtil.create_error_log(
                        "BAD_REQUEST:QueryParams:{},Error:{}".format(query_params, v.errors if v else None),
                    )
                    raise CustomBadRequest(detail="Invalid query parameters", errors=v.errors if v else None)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def singleton_class(cls):
    """
    await the class to be initialized
    class_object = await SingletonClass()
    class_object.method()


    if not awaited it will return a coroutine object
    class_object = SingletonClass()
    class_object.method() (fails with coroutine not having the method)
    """
    instances: Dict[Type, Any] = {}
    lock = asyncio.Lock()

    async def wrapper(*args, **kwargs):
        if cls not in instances:
            async with lock:
                # Double-checked locking pattern
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


def require_internal_authentication(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if request is None:
            request = next((arg for arg in args if isinstance(arg, Request)), None)
        if request is None:
            LoggerUtil.create_error_log("No request object found in function arguments")
            raise CustomUnauthorized(detail="Authentication required")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            LoggerUtil.create_error_log("No Authorization header found for internal auth")
            raise CustomUnauthorized(detail="Authorization header required")

        # Check for Bearer token format
        if not auth_header.startswith("Bearer "):
            LoggerUtil.create_error_log("Invalid Authorization header format for internal auth")
            raise CustomUnauthorized(detail="Invalid authorization format")

        # Extract the token
        token = auth_header[7:]  # Remove "Bearer " prefix

        # Validate against internal API key
        if token != env.INTERNAL_AUTH_API_KEY:
            LoggerUtil.create_error_log("Invalid internal API key")
            raise CustomUnauthorized(detail="Invalid internal API key")

        LoggerUtil.create_info_log("Internal authentication successful")
        return await func(*args, **kwargs)

    return wrapper
