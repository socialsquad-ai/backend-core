import traceback
import uuid
from contextlib import asynccontextmanager

import taskiq_fastapi
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from config.non_env import SERVER_INIT_LOG_MESSAGE
from controller.util import APIResponseFormat
from logger.logging import LoggerUtil
from server.router import init_routers
from utils.contextvar import (
    clear_request_metadata,
    set_context_json_post_payload,
    set_request_metadata,
)
from utils.exceptions import CustomBadRequest, CustomUnauthorized

from .pg_broker import broker  # Import broker from the new module

# OpenAPI Tags metadata for Swagger documentation
tags_metadata = [
    {
        "name": "Status",
        "description": "Health check and system status endpoints for monitoring service availability.",
    },
    {
        "name": "Users",
        "description": "User management operations including profile retrieval and user creation. Internal endpoints use API key authentication.",
    },
    {
        "name": "Onboarding",
        "description": "User onboarding flow to set up initial persona and preferences.",
    },
    {
        "name": "Integrations",
        "description": "Social media platform integrations management. Handles OAuth flows and connection status.",
    },
    {
        "name": "Personas",
        "description": "AI persona configuration for automated social media interactions. Manage tone, style, and behavior settings.",
    },
    {
        "name": "Webhooks",
        "description": "Webhook endpoints for receiving events from external platforms (e.g., Meta/Facebook). These endpoints use platform-specific verification.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    LoggerUtil.create_info_log("{}::Starting the app server...".format(SERVER_INIT_LOG_MESSAGE))
    LoggerUtil.create_info_log("{}::Setting environment specific variables...".format(SERVER_INIT_LOG_MESSAGE))
    LoggerUtil.create_info_log("{}::Registering REST API routes...".format(SERVER_INIT_LOG_MESSAGE))

    # Setting the config(DON'T remove the empty import!!)
    from config import env  # noqa: F401

    LoggerUtil.create_info_log("{}::Connecting to database(s)...".format(SERVER_INIT_LOG_MESSAGE))
    from data_adapter.db import ssq_db

    if not broker.is_worker_process:
        LoggerUtil.create_info_log("{}::Starting TaskIQ broker...".format(SERVER_INIT_LOG_MESSAGE))
        await broker.startup()

    yield  # Server is running and handling requests here

    # Shutdown
    LoggerUtil.create_info_log("{}::Shutting down the app server...".format(SERVER_INIT_LOG_MESSAGE))
    if not ssq_db.is_closed():
        ssq_db.close()
        LoggerUtil.create_info_log("{}::Database connections closed.".format(SERVER_INIT_LOG_MESSAGE))

    if not broker.is_worker_process:
        LoggerUtil.create_info_log("{}::Shutting down TaskIQ broker...".format(SERVER_INIT_LOG_MESSAGE))
        await broker.shutdown()


app = FastAPI(
    title="Social Squad API",
    description="Backend API for Social Squad - AI-powered social media management platform. Automate engagement, manage personas, and integrate with social media platforms.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_routers(app)

# Initialize TaskIQ with the broker and FastAPI app
taskiq_fastapi.init(broker, "server.app:app")


# Middleware to add a unique ID to each request
@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    api_id = str(uuid.uuid4())

    thread_id = str(uuid.uuid4())
    clear_request_metadata()
    set_request_metadata({"api_id": api_id, "thread_id": thread_id})
    await set_context_json_post_payload(request)
    response = await call_next(request)  # Process the request
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the error with traceback
    error_message = f"Error occurred: {str(exc)}\nTraceback:\n{traceback.format_exc()}"
    LoggerUtil.create_error_log(error_message)
    return APIResponseFormat(
        status_code=500,
        message="Internal Server Error",
        errors=[str(exc)],
    ).get_json()


@app.exception_handler(CustomUnauthorized)
async def custom_unauthorized_handler(request: Request, exc: CustomUnauthorized):
    LoggerUtil.create_error_log(f"Unauthorized: {exc.detail}")

    return APIResponseFormat(
        status_code=401,
        message=exc.detail,
        data=None,
        errors=[exc.detail],
    ).get_json()


@app.exception_handler(CustomBadRequest)
async def custom_bad_request_handler(request: Request, exc: CustomBadRequest):
    LoggerUtil.create_error_log(f"Bad Request: {exc.detail}, Errors: {exc.errors}")
    return APIResponseFormat(
        status_code=400,
        message=exc.detail,
        data=None,
        errors=exc.errors,
    ).get_json()


def custom_openapi():
    """Generate custom OpenAPI schema with security schemes."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=tags_metadata,
    )
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Auth0Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Auth0 JWT token. Obtain from Auth0 authentication flow.",
        },
        "InternalAPIKey": {
            "type": "http",
            "scheme": "bearer",
            "description": "Internal API key for service-to-service authentication.",
        },
        "MetaWebhookVerification": {
            "type": "apiKey",
            "in": "query",
            "name": "hub.verify_token",
            "description": "Meta webhook verification token passed as query parameter.",
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
