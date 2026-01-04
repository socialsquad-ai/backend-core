from config.env import APP_ENVIRONMENT
import uuid
import datetime


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


def parse_timestamp(value):
    """
    Parse a timestamp value (string or datetime) to datetime object.
    Handles ISO format strings and datetime objects.

    Args:
        value: String (ISO format) or datetime object

    Returns:
        datetime object or None if parsing fails or value is None

    Examples:
        >>> parse_timestamp('2025-11-09T11:19:46.759112+00:00')
        datetime.datetime(2025, 11, 9, 11, 19, 46, 759112, tzinfo=datetime.timezone.utc)
        >>> parse_timestamp('2025-11-09T11:19:46Z')
        datetime.datetime(2025, 11, 9, 11, 19, 46, tzinfo=datetime.timezone.utc)
        >>> parse_timestamp(datetime.datetime.now())
        datetime.datetime(...)
    """
    if value is None:
        return None

    if isinstance(value, datetime.datetime):
        return value

    if isinstance(value, str):
        try:
            # Handle ISO format strings (replace Z with +00:00 for fromisoformat)
            iso_string = value.replace("Z", "+00:00") if value.endswith("Z") else value
            return datetime.datetime.fromisoformat(iso_string)
        except (ValueError, AttributeError):
            return None

    return None
