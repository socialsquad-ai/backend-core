from config.env import APP_ENVIRONMENT


def is_local_env():
    return APP_ENVIRONMENT == "local"


def sanitize_string_input(input_string):
    """Remove extra white characters(like spaces, newlines) everywhere from input string"""
    if not isinstance(input_string, str):
        return ""
    sanitized_string = " ".join(input_string.split())
    return sanitized_string
