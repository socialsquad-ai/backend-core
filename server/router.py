from fastapi import FastAPI
from controller.status_controller import status_router
from controller.user_controller import user_router


def init_routers(app: FastAPI):
    """Initialize all routers and attach them to the main app."""

    app.include_router(status_router)
    app.include_router(user_router)
