import os

from dotenv import load_dotenv

from config.non_env import SERVER_INIT_LOG_MESSAGE
from config.util import Environment
from logger.logging import LoggerUtil

TESTING = os.environ.get("APP_ENVIRONMENT") == "testing"
LOCAL = os.environ.get("APP_ENVIRONMENT") == "local"
# Load env variables from a file, if exists
LoggerUtil.create_info_log(
    "{}::Setting environment variables from .env file(if exists)...".format(
        SERVER_INIT_LOG_MESSAGE
    )
)
if TESTING:
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.env")
    LoggerUtil.create_info_log(
        "{}::Loading testing environment variables from '{}' file...".format(
            SERVER_INIT_LOG_MESSAGE, dotenv_path
        )
    )
    load_dotenv(verbose=True, dotenv_path=dotenv_path)
elif LOCAL:
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    LoggerUtil.create_info_log(
        "{}::Loading local environment variables from '{}' file...".format(
            SERVER_INIT_LOG_MESSAGE, dotenv_path
        )
    )
    load_dotenv(verbose=True, dotenv_path=dotenv_path)
else:
    LoggerUtil.create_info_log(
        "{}::Loading environment variables from '.env' file...".format(
            SERVER_INIT_LOG_MESSAGE
        )
    )
    load_dotenv(verbose=True)

DEBUG = Environment.get_bool("DEBUG", "False")
SSQ_SECRET_KEY = Environment.get_string("SSQ_SECRET_KEY")
SSQ_ALGORITHM = Environment.get_string("SSQ_ALGORITHM")
SSQ_ACCESS_TOKEN_EXPIRE_MINUTES = Environment.get_int("SSQ_ACCESS_TOKEN_EXPIRE_MINUTES")

SSQ_DB_NAME = Environment.get_string("SSQ_DB_NAME")
SSQ_DB_USER = Environment.get_string("SSQ_DB_USER")
SSQ_DB_HOST = Environment.get_string("SSQ_DB_HOST")
SSQ_DB_PASSWORD = Environment.get_string("SSQ_DB_PASSWORD")
SSQ_DB_PORT = Environment.get_int("SSQ_DB_PORT")
APP_ENVIRONMENT = Environment.get_string("APP_ENVIRONMENT")

# Auth0 Configuration (for token validation only)
AUTH0_DOMAIN = Environment.get_string("AUTH0_DOMAIN")
AUTH0_AUDIENCE = Environment.get_string("AUTH0_AUDIENCE")
AUTH0_ISSUER = Environment.get_string("AUTH0_ISSUER", f"https://{AUTH0_DOMAIN}/")

# Internal API Key (for webhooks, callbacks, internal services)
INTERNAL_AUTH_API_KEY = Environment.get_string("INTERNAL_AUTH_API_KEY")

# Social Media Integration Configuration
META_CLIENT_ID = Environment.get_string("META_CLIENT_ID")
META_CLIENT_SECRET = Environment.get_string("META_CLIENT_SECRET")
GOOGLE_CLIENT_ID = Environment.get_string("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = Environment.get_string("GOOGLE_CLIENT_SECRET")
