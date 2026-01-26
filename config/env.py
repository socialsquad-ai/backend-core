import os
from urllib.parse import urlparse

from dotenv import load_dotenv

from config.non_env import SERVER_INIT_LOG_MESSAGE
from config.util import Environment
from logger.logging import LoggerUtil

TESTING = os.environ.get("APP_ENVIRONMENT") == "testing"
LOCAL = os.environ.get("APP_ENVIRONMENT", "local") == "local"
# Load env variables from a file, if exists
LoggerUtil.create_info_log("{}::Setting environment variables from .env file(if exists)...".format(SERVER_INIT_LOG_MESSAGE))
if TESTING:
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.env")
    LoggerUtil.create_info_log("{}::Loading testing environment variables from '{}' file...".format(SERVER_INIT_LOG_MESSAGE, dotenv_path))
    load_dotenv(verbose=True, dotenv_path=dotenv_path)
elif LOCAL:
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    LoggerUtil.create_info_log("{}::Loading local environment variables from '{}' file...".format(SERVER_INIT_LOG_MESSAGE, dotenv_path))
    load_dotenv(verbose=True, dotenv_path=dotenv_path)
else:
    LoggerUtil.create_info_log("{}::Loading environment variables from '.env' file...".format(SERVER_INIT_LOG_MESSAGE))
    load_dotenv(verbose=True)

DEBUG = Environment.get_bool("DEBUG", "False")

# Database configuration
# Heroku provides DATABASE_URL, local dev uses individual vars
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Heroku provides postgres:// but psycopg2/peewee needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    parsed = urlparse(DATABASE_URL)
    SSQ_DB_HOST = parsed.hostname
    SSQ_DB_PORT = parsed.port or 5432
    SSQ_DB_USER = parsed.username
    SSQ_DB_PASSWORD = parsed.password
    SSQ_DB_NAME = parsed.path[1:]  # Remove leading slash
    LoggerUtil.create_info_log(f"{SERVER_INIT_LOG_MESSAGE}::Using DATABASE_URL for database connection")
else:
    # Local development - use individual environment variables
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

# Auth0 Management API (for resending verification emails, user management)
# Create a Machine-to-Machine application in Auth0 Dashboard
AUTH0_MGMT_CLIENT_ID = Environment.get_string("AUTH0_MGMT_CLIENT_ID", "")
AUTH0_MGMT_CLIENT_SECRET = Environment.get_string("AUTH0_MGMT_CLIENT_SECRET", "")
# This is typically your SPA client ID (for verification email redirects)
AUTH0_SPA_CLIENT_ID = Environment.get_string("AUTH0_SPA_CLIENT_ID", "")

# Internal API Key (for webhooks, callbacks, internal services)
INTERNAL_AUTH_API_KEY = Environment.get_string("INTERNAL_AUTH_API_KEY")

SSQ_BASE_URL = Environment.get_string("SSQ_BASE_URL")
SSQ_CLIENT_URL = Environment.get_string("SSQ_CLIENT_URL")

# Social Media Integration Configuration
META_CLIENT_ID = Environment.get_string("META_CLIENT_ID")
META_CLIENT_SECRET = Environment.get_string("META_CLIENT_SECRET")
GOOGLE_CLIENT_ID = Environment.get_string("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = Environment.get_string("GOOGLE_CLIENT_SECRET")
