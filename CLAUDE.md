# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the server
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
python -m pytest tests/ -v
```

### Code Quality
```bash
# Lint code with ruff
ruff check .

# Format code with ruff
ruff format .
```

### TaskIQ Worker
```bash
# Start TaskIQ worker for async task processing
taskiq worker server.pg_broker:broker
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
