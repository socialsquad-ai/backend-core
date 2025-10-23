# Version prefix constants
API_VERSION_V1 = "/v1"
API_VERSION_V2 = "/v2"
API_VERSION_V3 = "/v3"


SERVER_INIT_LOG_MESSAGE = "SERVER_INIT"
CONFIG_ERROR_LOG_MESSAGE = "CONFIG_ERROR"
ALERT_MESSAGE_PREPEND = "ALERT"
GLOBAL_ERROR_KEY = "global_error"
SERVICE_NAME = "api-service"


URL_REGEX = r"(([a-z]{3,6}://)|(^|\s))([a-zA-Z0-9\-]+\.)+[a-z]{2,13}[\.\?\=\&\%\/\w\-]*\b([^@]|$)"
FILTER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Agent types
CREATE_REPLY_AGENT = "create_reply_agent"
IGNORE_COMMENT_AGENT = "ignore_comment_agent"
DELETE_COMMENT_AGENT = "delete_comment_agent"

# Webhook Configuration
META_VERIFY_TOKEN = "ssq_meta"  # Token for Meta webhook verification

# Agent User Prompts
USER_PROMPT = {
    CREATE_REPLY_AGENT: "Reply to the user comment",
    IGNORE_COMMENT_AGENT: "Check if the user comment should be ignored",
    DELETE_COMMENT_AGENT: "Check if the user comment should be deleted",
}

# Platform Info
PLATFORM_INSTAGRAM = "instagram"
PLATFORM_YOUTUBE = "youtube"
PLATFORM_NAME_DESCRIPTION = {
    "youtube": "Comments on YouTube videos can be up to 2000 characters long and can contain emojis.",
    "instagram": "Comments on Instagram photos and videos can be up to 1024 characters long and can contain emojis.",
}
