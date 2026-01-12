# SocialSquadAI Backend Core

## Project Overview
SocialSquadAI is a backend service designed to automate social media engagement using AI. It provides functionality for managing user personas, integrating with social media platforms (Instagram, YouTube), and handling real-time webhook events (specifically from Meta/Instagram) to auto-generate replies, delete offensive content, or ignore irrelevancy.

## Key Technologies
*   **Language**: Python 3.12+
*   **Web Framework**: FastAPI
*   **Database**: PostgreSQL (v16.6+)
*   **ORM**: Peewee
*   **Task Queue**: TaskIQ with PostgreSQL broker
*   **AI/LLM**: Google Gemini (via `pydantic-ai`)
*   **Authentication**: Auth0 (JWT) & Internal API Keys
*   **HTTP Client**: HTTPX (Async)

## Architecture
The project follows a **Clean Architecture** / Layered pattern:
1.  **Controllers (`controller/`)**: Handle HTTP requests, input validation, and route definitions.
2.  **Use Cases (`usecases/`)**: Encapsulate business logic and orchestrate data flow (e.g., `webhook_management.py`, `ssq_agent.py`).
3.  **Data Adapters (`data_adapter/`)**: Handle database interactions and define Peewee models.
4.  **Decorators (`decorators/`)**: Cross-cutting concerns like Authentication (`@require_authentication`) and Validation (`@validate_json_payload`).
5.  **Utils (`utils/`)**: Helper services for external APIs (Auth0, Platform interactions).

## Setup & Installation

### Prerequisites
*   Python 3.12+
*   PostgreSQL 16.6+

### Database Setup
1.  Ensure PostgreSQL is running.
2.  Execute the initial setup script:
    ```bash
    psql -U postgres -f data_adapter/sql-postgres/1.initial_setup.sql
    ```

### Environment Setup
1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
2.  Activate the environment:
    *   Windows: `.venv\Scripts\activate`
    *   Unix: `source .venv/bin/activate`
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

## Development Conventions

### Code Style
*   **Formatting/Linting**: The project uses `ruff`. Run `ruff check .` to verify.
*   **Async First**: All I/O bound operations (DB, External APIs) should be asynchronous (`async/await`).
*   **Type Hinting**: Extensive use of Python type hints is expected.

### API Decorator Order
Decorators execute top-to-bottom:
1.  `@require_authentication` (Auth Check)
2.  `@validate_json_payload` / `@validate_query_params` (Input Validation)

Example:
```python
@require_authentication
@validate_json_payload(schema)
async def endpoint(request: Request):
    ...
```

### Key Components

*   **Webhook Handling**:
    *   Entry point: `controller/webhook_controller.py`
    *   Logic: `usecases/webhook_management.py`
    *   Task Queue: Events are pushed to TaskIQ (`usecases/task.py`) for background processing.
*   **AI Agents**:
    *   Located in `usecases/ssq_agent.py`.
    *   Uses a cached `GoogleModel` instance for performance.
    *   Prompts are managed via Jinja2 templates in `prompts/`.

## Common Tasks
*   **Adding a new dependency**: Add to `requirements.txt`.
*   **Database Migration**: Manually manage SQL scripts in `data_adapter/sql-postgres/`.
*   **New Platform Integration**:
    1.  Add platform constant in `config/non_env.py`.
    2.  Implement methods in `utils/platform_service.py`.
    3.  Update `usecases/webhook_management.py` to handle platform-specific logic.
