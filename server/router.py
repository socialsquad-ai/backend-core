from fastapi import FastAPI
from controller.status_controller import status_router
from controller.sample_user_controller import sample_user_router, sample_user_router_v2


def init_routers(app: FastAPI):
    """Initialize all routers and attach them to the main app."""

    app.include_router(status_router)
    app.include_router(sample_user_router)
    app.include_router(sample_user_router_v2)
