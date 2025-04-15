from config.env import APP_ENVIRONMENT
import uuid


def is_local_env():
    return APP_ENVIRONMENT == "local"


def sanitize_string_input(input_string):
    """Remove extra white characters(like spaces, newlines) everywhere from input string"""
    if not isinstance(input_string, str):
        return ""
    sanitized_string = " ".join(input_string.split())
    return sanitized_string


def is_valid_uuid_v4(uuid_string):
    try:
        uuid.UUID(uuid_string, version=4)
        return True
    except ValueError:
        return False
