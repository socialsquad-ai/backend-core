# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL REQUIREMENTS

### Swagger Documentation (MANDATORY)

**Every time you add or modify an API endpoint, you MUST update Swagger documentation:**

1. Add `summary` and `description` to the route decorator
2. Add `responses` dict with all possible status codes
3. Add `openapi_extra={"security": [...]}` if authentication is required
4. If creating a new domain, add tag to `tags_metadata` in `server/app.py`

Example:
```python
@router.post(
    "/",
    summary="Create Resource",  # REQUIRED
    description="Detailed description of the endpoint.",  # REQUIRED
    responses={  # REQUIRED
        200: {"description": "Success"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},  # If auth required
)
```

**Verification**: After adding an API, check http://localhost:8000/docs to ensure it appears correctly.

## Development Commands (Docker)

### Start All Services
```bash
docker compose up
```

### Start Individual Services
```bash
docker compose up postgres   # Database only
docker compose up api        # API server only
docker compose up worker     # TaskIQ worker only
```

### Stop Services
```bash
docker compose down          # Stop all
docker compose down -v       # Stop and remove volumes (resets database)
```

### Running Tests
```bash
# In Docker (recommended)
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Locally
python -m pytest tests/ -v
```

### Code Quality
```bash
ruff check .   # Lint
ruff format .  # Format
```

## Architecture Overview

### Core Design Pattern
This is a **FastAPI-based backend** following a layered architecture:

**Controller → Usecase → Data Adapter → Database**

- **Controllers** (`controller/`): FastAPI routers that handle HTTP requests and responses
- **Usecases** (`usecases/`): Business logic layer that orchestrates operations
- **Data Adapters** (`data_adapter/`): Database models and queries using Peewee ORM
- **Decorators** (`decorators/`): Custom decorators for authentication and validation

### Database Architecture
- **ORM**: Peewee with connection pooling (`PooledPostgresqlExtDatabase`)
- **Base Model**: All models inherit from `BaseModel` (in `data_adapter/db.py`)
  - Provides: `id`, `uuid`, `created_at`, `updated_at`, `is_deleted`
  - Implements soft deletes via `is_deleted` flag
  - Custom query methods: `select_query()`, `update_query()`, `soft_delete()`
- **Database Setup**: Run SQL scripts in `data_adapter/sql-postgres/` in numerical order

### Authentication System
- **Auth0 Integration**: Token-based authentication (no user management in backend)
- **Two Decorator Types**:
  - `@require_authentication`: Validates Auth0 JWT tokens, extracts user from token
  - `@require_internal_authentication`: Validates internal API key for service-to-service calls
- **User Context**: Authenticated user stored via `set_context_user()` and accessible via `get_context_user()`
- See `AUTH0_SETUP.md` for Auth0 configuration details

### Request Processing Flow
1. **Middleware** (`server/app.py`): Each request gets unique `api_id` and `thread_id`
2. **Context Variables** (`utils/contextvar.py`): Request metadata stored in context vars
3. **Decorators Execute Top-to-Bottom**:
   ```python
   @require_authentication  # Runs first
   @validate_json_payload({ ... })  # Runs second
   async def endpoint(request: Request):
       pass
   ```
4. **Payload Validation**: Uses Cerberus validator (`controller/cerberus.py`)
5. **Response Format**: Standardized via `APIResponseFormat` in `controller/util.py`

### Asynchronous Task Processing
- **TaskIQ**: Async task queue backed by PostgreSQL (`server/pg_broker.py`)
- **Task Definition**: Use `@broker.task` decorator (see `usecases/task.py`)
- **Webhook Processing**: Webhooks are enqueued for async processing
  - Controller receives webhook → Validates → Enqueues task → Returns immediately
  - Worker processes task asynchronously
  - Webhook logs stored in `webhook_logs` table for idempotency and retry tracking

### AI Agent System
- **SSQAgent** (`usecases/ssq_agent.py`): Pydantic AI agents using Google's Gemini models
- **Prompts**: Jinja2 templates in `prompts/` directory
- **Use Cases**: Comment analysis, reply generation, content moderation
- **Integration**: Used in webhook processing for automated social media interactions

### Logging
- **Logger**: Custom `LoggerUtil` class in `logger/logging.py`
- **Methods**: `create_info_log()`, `create_error_log()`, `create_warning_log()`
- **Context**: Automatically includes `api_id` and `thread_id` from request metadata

### Environment Configuration
- **Config Files**: Environment variables loaded from `config/.env`
- **Env Helper**: `config/env.py` uses `Environment` utility class
- **Non-Env Constants**: Hardcoded constants in `config/non_env.py`
- **Testing**: Use `config/test.env` when `APP_ENVIRONMENT=testing`

## Key Implementation Patterns

### Adding a New API Endpoint
1. Create controller in `controller/` with FastAPI router
2. Add business logic in `usecases/`
3. Add data access methods in `data_adapter/`
4. Register router in `server/router.py` via `init_routers()`
5. Apply decorators for auth and validation

### Database Model Pattern
```python
class MyModel(BaseModel):
    # Define fields
    # Use select_query() instead of select() for soft-delete awareness
    # Always call save() to auto-update updated_at timestamp
```

### Async Task Pattern
```python
@broker.task
async def my_background_task(data: dict):
    # Task logic here
    pass

# Enqueue task
await my_background_task.kiq(data)
```

### Custom Exception Handling
- Use `CustomUnauthorized` for 401 errors
- Use `CustomBadRequest` for 400 errors
- Global exception handlers defined in `server/app.py`

## Project Structure Notes

### Controllers
Each controller corresponds to a domain:
- `user_controller.py`: User profile and management
- `integration_controller.py`: Social media platform integrations
- `persona_controller.py`: AI persona configuration
- `webhook_controller.py`: Incoming webhook handling
- `onboarding_controller.py`: User onboarding flow
- `status_controller.py`: Health check endpoints

### Data Models
Key models in `data_adapter/`:
- `user.py`: User accounts
- `integration.py`: OAuth integrations with social platforms
- `personas.py`: AI persona configurations
- `posts.py`: Social media posts
- `webhook_logs.py`: Webhook event tracking

### Testing
- Test framework: pytest
- Test files located in `tests/` directory
- Database setup required before running tests

## API Documentation (Swagger/OpenAPI)

### Accessing API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Security Schemes
The API uses three authentication methods documented in Swagger:

1. **Auth0Bearer**: JWT tokens from Auth0 for user authentication
2. **InternalAPIKey**: Bearer token for service-to-service calls
3. **MetaWebhookVerification**: Query parameter verification for Meta webhooks

### Adding Swagger Documentation to New Endpoints

When creating new API endpoints, follow this pattern to ensure they appear correctly in Swagger:

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/resource",
    tags=["ResourceName"],  # Must match a tag in server/app.py tags_metadata
)

@router.get(
    "/",
    summary="Short Action Description",  # Shows in endpoint list
    description="Detailed description of what this endpoint does.",
    responses={
        200: {"description": "Success response description"},
        400: {"description": "Bad request description"},
        401: {"description": "Authentication required"},
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},  # Or InternalAPIKey, or omit for public
)
@require_authentication  # Decorator must come after route decorator
async def get_resource(request: Request):
    """Docstring becomes the endpoint description if no description param."""
    pass
```

### Authentication Documentation Patterns

**User-authenticated endpoints** (Auth0 JWT):
```python
@router.get(
    "/",
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def endpoint():
    pass
```

**Internal service endpoints** (API Key):
```python
@router.post(
    "/",
    openapi_extra={"security": [{"InternalAPIKey": []}]},
)
@require_internal_authentication
async def endpoint():
    pass
```

**Public endpoints** (no auth, like OAuth callbacks):
```python
@router.get("/callback")  # No openapi_extra security
async def callback():
    pass
```

**Webhook endpoints** (platform-specific verification):
```python
@router.get(
    "/webhook",
    openapi_extra={"security": [{"MetaWebhookVerification": []}]},
)
async def verify_webhook():
    pass
```

### Adding New Tags

If creating a new controller domain, add a tag to `tags_metadata` in `server/app.py`:

```python
tags_metadata = [
    # ... existing tags
    {
        "name": "NewDomain",
        "description": "Description of what this API group handles.",
    },
]
```

Then use `tags=["NewDomain"]` in your `APIRouter`.
