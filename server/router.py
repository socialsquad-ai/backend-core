from fastapi import FastAPI

from controller.instagram_controller import instagram_router
from controller.integration_controller import integrations_router
from controller.onboarding_controller import onboarding_router
from controller.persona_controller import persona_router
from controller.status_controller import status_router
from controller.user_controller import user_router
from controller.webhook_controller import webhook_router


def init_routers(app: FastAPI):
    """Initialize all routers and attach them to the main app."""

    app.include_router(status_router)
    app.include_router(user_router)
    app.include_router(onboarding_router)
    app.include_router(integrations_router)
    app.include_router(persona_router)
    app.include_router(webhook_router)
    app.include_router(instagram_router)
