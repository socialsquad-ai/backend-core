from functools import wraps
from controller.cerebrus import CustomValidator
from logger.logging import LoggerUtil
from utils.exceptions import CustomBadRequest
from utils.contextvar import get_request_json_post_payload


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
                raise CustomBadRequest(
                    detail="Invalid payload", errors=v.errors if v else None
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_query_params(func):
    # TODO :: Add the logic to validate the query params
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
