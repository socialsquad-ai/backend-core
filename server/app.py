from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.non_env import SERVER_INIT_LOG_MESSAGE
from logger.logging import LoggerUtil
from server.router import init_routers
import traceback
from controller.util import APIResponseFormat
import uuid
from utils.exceptions import CustomUnauthorized, CustomBadRequest
from utils.contextvar import (
    set_request_metadata,
    clear_request_metadata,
    set_context_json_post_payload,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    LoggerUtil.create_info_log(
        "{}::Starting the app server...".format(SERVER_INIT_LOG_MESSAGE)
    )
    LoggerUtil.create_info_log(
        "{}::Setting environment specific variables...".format(SERVER_INIT_LOG_MESSAGE)
    )

    # Setting the config(DON'T remove the empty import!!) #
    from config import env  # noqa: F401

    LoggerUtil.create_info_log(
        "{}::Connecting to database(s)...".format(SERVER_INIT_LOG_MESSAGE)
    )
    from data_adapter.db import ssq_db

    yield  # Server is running and handling requests here

    # Shutdown
    LoggerUtil.create_info_log(
        "{}::Shutting down the app server...".format(SERVER_INIT_LOG_MESSAGE)
    )
    if not ssq_db.is_closed():
        ssq_db.close()
        LoggerUtil.create_info_log(
            "{}::Database connections closed.".format(SERVER_INIT_LOG_MESSAGE)
        )


app = FastAPI(title="API Service", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_routers(app)

LoggerUtil.create_info_log(
    "{}::Registering REST API routes...".format(SERVER_INIT_LOG_MESSAGE)
)


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
