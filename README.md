# Social Squad Backend

FastAPI-based backend for Social Squad - AI-powered social media management platform.

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.12 | Required for both Docker and local development |
| **Docker** | 20.10+ | Required for Docker-based development |
| **Docker Compose** | 2.0+ | Required for Docker-based development |
| **PostgreSQL** | 16.6+ | Only if running locally without Docker |

> **Important**: Python 3.12 is used consistently across Docker containers and local development to ensure compatibility.

---

## Quick Start (Docker) — Recommended

This is the recommended way to run the backend. Docker handles all dependencies and database setup automatically.

### Prerequisites

- **Docker Desktop** installed and running
- **VS Code** with Python and Docker extensions (optional, for debugging)

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd backend-core

# Copy environment template
cp config/.env.example config/.env

# Edit config/.env with your actual values (API keys, secrets, etc.)
```

### Step 2: Start Services

**Option A: Using VS Code (Recommended)**

1. Open the project in VS Code
2. Press `F5` or go to Run → Start Debugging
3. Select **"Start All Services"** from the dropdown
4. Wait for services to start (debugger will attach automatically)

**Option B: Using Terminal**

```bash
docker compose up
```

### Step 3: Verify

Once running, you can access:

| Endpoint | URL | Description |
|----------|-----|-------------|
| **API** | http://localhost:8000 | Main API endpoint |
| **Swagger UI** | http://localhost:8000/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| **Health Check** | http://localhost:8000/v1/status/ | Service health status |

Test the health check:
```bash
curl http://localhost:8000/v1/status/
```

---

## Local Development (Without Docker)

Use this approach if you prefer running Python directly on your machine.

### Prerequisites

- **Python 3.12** installed ([Download](https://www.python.org/downloads/))
- **PostgreSQL 16.6+** installed and running

### Step 1: Set Up Python Virtual Environment

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Verify Python version
python --version  # Should show Python 3.12.x
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing, linting)
pip install -r requirements-dev.txt
```

### Step 3: Set Up PostgreSQL Database

```bash
# Run SQL setup scripts in order
psql postgres -f data_adapter/sql-postgres/0.extensions.sql
psql postgres -f data_adapter/sql-postgres/1.initial_setup.sql
psql postgres -f data_adapter/sql-postgres/2.create_user.sql
psql postgres -f data_adapter/sql-postgres/3.create_integration.sql
psql postgres -f data_adapter/sql-postgres/4.personas_setup.sql
# Continue with any additional SQL files in numerical order
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp config/.env.example config/.env

# Edit config/.env with your database connection and other settings
```

### Step 5: Run the Application

```bash
# Start the API server
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# In a separate terminal (activate venv first), start the TaskIQ worker
source .venv/bin/activate
taskiq worker server.pg_broker:broker
```

---

## VS Code Integration

### Launch Configurations

Available in the Run and Debug panel (`F5`):

| Configuration | Description |
|---------------|-------------|
| **Start All Services** | Starts Postgres, API, and Worker with debugger attached to API |
| **Start API Server** | Starts only API server with debugger attached |
| **Start Worker** | Starts only TaskIQ worker with debugger attached |
| **Start Postgres** | Starts only the database container |

### Tasks

Run via `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux) → "Tasks: Run Task":

| Task | Description |
|------|-------------|
| `docker-stop` | Stop all Docker containers |
| `docker-clean` | Stop containers, remove volumes, prune system |
| `Run Unit Tests (Docker)` | Run pytest in isolated Docker environment |
| `Ruff Format` | Format code with Ruff |
| `Ruff Check` | Lint code with Ruff |

### Debugging

- **Breakpoints work** in both API and Worker when using VS Code launch configurations
- The debugger attaches via `debugpy` on ports 5678 (API) and 5679 (Worker)
- Path mappings are configured automatically

---

## Services Architecture

| Service | Port | Description | Data Persistence |
|---------|------|-------------|------------------|
| **postgres** | 5432 | PostgreSQL database | `ssq-postgres-data` Docker volume |
| **api** | 8000 | FastAPI server | Stateless |
| **worker** | - | TaskIQ background worker | Stateless |

### Debug Ports (Development Only)

| Service | Debug Port | Purpose |
|---------|------------|---------|
| **api** | 5678 | VS Code debugpy attachment |
| **worker** | 5679 | VS Code debugpy attachment |

---

## Hot Reload

**Code changes are automatically detected in development!**

- The API server runs with `--reload` flag
- Source code is mounted into containers via Docker volumes
- Save a file → uvicorn automatically restarts

**Rebuild required only when changing:**
- `requirements.txt` or `requirements-dev.txt`
- `Dockerfile`
- `docker-compose.yml` or `docker-compose.override.yml`

To rebuild:
```bash
docker compose up --build
```

---

## Running Tests

### Using Docker (Recommended)

```bash
# Run tests in isolated environment
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
docker compose -f docker-compose.test.yml down
```

Or use the VS Code task: `Run Unit Tests (Docker)`

### Using Local Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_example.py -v

# Run with coverage
python -m pytest tests/ -v --cov=.
```

---

## Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Auto-fix linting issues
ruff check . --fix
```

---

## Project Structure

```
backend-core/
├── config/           # Environment configuration
│   ├── .env          # Local environment variables (git-ignored)
│   ├── .env.example  # Environment template
│   ├── env.py        # Environment loader
│   └── non_env.py    # Hardcoded constants
├── controller/       # FastAPI route handlers
├── data_adapter/     # Database models (Peewee ORM)
│   └── sql-postgres/ # Database migration scripts
├── decorators/       # Auth & validation decorators
├── logger/           # Logging utilities
├── prompts/          # AI agent prompts (Jinja2 templates)
├── server/           # FastAPI app & router setup
├── usecases/         # Business logic layer
├── utils/            # Shared utilities
├── tests/            # Unit tests
├── Dockerfile        # Multi-stage Docker build
├── docker-compose.yml        # Base Docker configuration
└── docker-compose.override.yml  # Development overrides
```

---

## Common Commands Reference

| Task | Command |
|------|---------|
| Start all services | `docker compose up` |
| Start in background | `docker compose up -d` |
| Stop services | `docker compose down` |
| View logs | `docker compose logs -f` |
| View specific service logs | `docker compose logs -f api` |
| Rebuild and start | `docker compose up --build` |
| Reset database | `docker compose down -v && docker compose up` |
| Enter container shell | `docker compose exec api bash` |

---

## Troubleshooting

### Port already in use

```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database connection issues

```bash
# Restart just postgres
docker compose restart postgres

# Check postgres logs
docker compose logs postgres
```

### Debugger not attaching

1. Ensure containers are fully started (wait for "API ready!" message)
2. Check that ports 5678/5679 are not blocked
3. Try stopping all containers and starting fresh:
   ```bash
   docker compose down
   docker compose up
   ```

### Python version mismatch

Ensure you're using Python 3.12:
```bash
python --version  # Should show 3.12.x

# If not, specify the version explicitly
python3.12 -m venv .venv
```
