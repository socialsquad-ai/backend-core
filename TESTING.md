# Testing Infrastructure Guide

This document provides comprehensive guidance on the testing infrastructure for the SSQ Backend Core project.

## Table of Contents

- [Overview](#overview)
- [Test Coverage Requirements](#test-coverage-requirements)
- [Running Tests](#running-tests)
- [Test Infrastructure Components](#test-infrastructure-components)
- [VS Code Integration](#vs-code-integration)
- [GitHub Actions](#github-actions)
- [Writing Unit Tests](#writing-unit-tests)
- [Troubleshooting](#troubleshooting)

## Overview

This project uses **pytest** as the testing framework with the following goals:

- **100% code coverage** requirement enforced in CI/CD
- **Unit tests only** - no integration or end-to-end tests
- **Comprehensive mocking** of all external dependencies
- **Docker-based test execution** for consistency across environments

## Test Coverage Requirements

### Coverage Target: 100%

All code must have 100% test coverage. This is enforced by:

1. **pytest.ini** configuration with `--cov-fail-under=100`
2. **GitHub Actions** workflow that fails if coverage < 100%
3. **.coveragerc** configuration to exclude non-code files

### Excluded from Coverage

The following are excluded from coverage requirements (see `.coveragerc`):

- Test files (`*/tests/*`, `**/test_*.py`)
- Virtual environments (`*/.venv/*`, `*/venv/*`)
- Cache directories (`**/__pycache__/*`, `**/.pytest_cache/*`)
- Initialization files (`*/__init__.py`)
- Entry points (`*/server/app.py`, `*/server/router.py`, `*/server/pg_broker.py`)
- Database migration scripts (`*/data_adapter/sql-postgres/*`)

## Running Tests

### Local Execution (Without Docker)

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
python -m pytest tests/utils/test_util.py -v

# Run specific test class
python -m pytest tests/utils/test_util.py::TestSanitizeStringInput -v

# Run specific test function
python -m pytest tests/utils/test_util.py::TestSanitizeStringInput::test_sanitize_string_input_removes_extra_spaces -v
```

### Docker Execution

```bash
# Run tests in Docker with automatic cleanup
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit && \\
docker-compose -f docker-compose.test.yml down

# Run tests and view coverage report
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit && \\
open htmlcov/index.html && \\
docker-compose -f docker-compose.test.yml down
```

### Cleanup

```bash
# Stop and remove all test containers
docker-compose -f docker-compose.test.yml down -v

# Clean test artifacts
rm -rf .pytest_cache htmlcov coverage.xml .coverage
```

## Test Infrastructure Components

### Configuration Files

#### 1. pytest.ini

Main pytest configuration file with:

- Test discovery patterns
- Coverage settings (100% requirement)
- Async test support
- Test markers (unit, integration, slow, etc.)
- Log configuration

#### 2. .coveragerc

Coverage configuration with:

- Source paths and omit patterns
- Branch coverage enabled
- Exclusion patterns for non-testable code
- Report formats (HTML, XML, terminal)

#### 3. requirements-dev.txt

Development dependencies including:

- `pytest==8.3.4` - Testing framework
- `pytest-asyncio==0.24.0` - Async test support
- `pytest-cov==6.0.0` - Coverage plugin
- `pytest-mock==3.14.0` - Mocking utilities
- `pre-commit==4.0.1` - Pre-commit hooks

### Docker Files

#### 1. Dockerfile.test

Isolated test environment with:

- Python 3.9-slim base image
- PostgreSQL client for database tests
- All project dependencies
- Test-specific environment variables

#### 2. docker-compose.test.yml

Complete test stack with:

- PostgreSQL test database (port 5433)
- Test runner service with dependencies
- Health checks for database
- Volume mounts for code and reports

## VS Code Integration

### Tasks (`.vscode/tasks.json`)

Available VS Code tasks (run via `Cmd+Shift+P` > "Tasks: Run Task"):

1. **Run Unit Tests (Docker)** - Full test suite in Docker with cleanup
2. **Run Unit Tests (Local)** - Quick local test execution
3. **Run Tests with Coverage (Local)** - Local tests with coverage report
4. **Run Tests with Coverage Report (Docker)** - Docker tests with HTML report
5. **Check Test Coverage Percentage** - Validate 100% coverage
6. **Generate Coverage Report (HTML)** - Create and open HTML report
7. **Stop and Remove Test Containers** - Cleanup Docker resources
8. **Clean Test Artifacts** - Remove all cache and coverage files
9. **Run Specific Test File** - Run currently open test file
10. **Ruff Format Code** - Format codebase
11. **Ruff Check Code** - Lint codebase

### Settings (`.vscode/settings.json`)

- pytest test discovery enabled
- Coverage gutters for inline coverage display
- Auto-format on save with Ruff
- Python interpreter path configured
- Test explorer integration

### Running Tests from VS Code

1. **Test Explorer**: Click the test icon in the sidebar to see all tests
2. **Individual Test**: Click the play button next to any test
3. **Debug Test**: Click the debug icon next to a test to debug
4. **Run Task**: `Cmd+Shift+P` > "Tasks: Run Task" > Select task

## GitHub Actions

### Workflow 1: Unit Tests (`.github/workflows/unit-tests.yml`)

Runs on every push and pull request:

1. Sets up Python 3.9 and PostgreSQL
2. Installs dependencies
3. Runs Ruff linter and formatter checks
4. Executes all unit tests
5. Uploads test results as artifacts

**Triggers**: Push to master/develop/fix-agent-flow, PRs to master/develop

### Workflow 2: Coverage Enforcement (`.github/workflows/coverage-enforcement.yml`)

Enforces 100% coverage requirement:

1. Runs all tests with coverage
2. Generates coverage reports
3. **Fails build if coverage < 100%**
4. Comments coverage percentage on PRs
5. Uploads coverage reports as artifacts

**Triggers**: Push to master/develop/fix-agent-flow, PRs to master/develop

## Writing Unit Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_function_name_scenario(self):
    # Arrange: Set up test data and mocks
    mock_dependency = Mock(return_value=expected_value)

    # Act: Call the function under test
    result = function_under_test(test_input)

    # Assert: Verify results and mock interactions
    assert result == expected_output
    mock_dependency.assert_called_once_with(expected_args)
```

### Test Organization

```
tests/
├── __init__.py
├── utils/
│   ├── test_util.py
│   ├── test_contextvar.py
│   ├── test_exceptions.py
│   └── test_auth0_service.py
├── logger/
│   └── test_logging.py
├── decorators/
│   ├── test_common.py
│   └── test_user.py
├── controller/
│   ├── test_util.py
│   └── test_cerberus.py
├── usecases/
│   └── (to be implemented)
└── data_adapter/
    └── (to be implemented)
```

### Naming Conventions

- **Test files**: `test_<module_name>.py`
- **Test classes**: `Test<FunctionName>` or `Test<ClassName>`
- **Test methods**: `test_<function>_<scenario>`

Examples:
- `test_sanitize_string_input_removes_extra_spaces`
- `test_validate_token_handles_expired_signature_error`
- `test_get_context_api_id_returns_empty_when_not_set`

### Mocking Strategy

#### 1. Mock External Dependencies

Always mock:
- Database calls (`peewee` models)
- HTTP requests (`requests`, Auth0 API)
- File I/O operations
- External services (TaskIQ, webhooks)

```python
@patch("module.path.DatabaseModel.select")
def test_function(self, mock_select):
    mock_select.return_value.where.return_value = mock_data
```

#### 2. Mock Layer Dependencies

When testing controllers, mock usecases:
```python
@patch("controller.user_controller.UserManagement.get_user")
def test_get_user_endpoint(self, mock_get_user):
    mock_get_user.return_value = {"id": 1, "name": "Test"}
```

When testing usecases, mock data adapters:
```python
@patch("usecases.user_management.User.select_query")
def test_get_user_by_id(self, mock_select):
    mock_select.return_value.where.return_value = [user_data]
```

#### 3. Mock Context Variables

```python
@patch("module.path.get_context_user")
def test_requires_user_context(self, mock_get_user):
    mock_get_user.return_value = {"id": 123}
```

#### 4. Mock Loggers

```python
@patch("module.path.LoggerUtil.create_info_log")
def test_logs_info(self, mock_logger):
    function_that_logs()
    mock_logger.assert_called_once()
```

### Testing Async Functions

Use `pytest.mark.asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function(self):
    # Arrange
    mock_service = AsyncMock(return_value="result")

    # Act
    result = await async_function(mock_service)

    # Assert
    assert result == "result"
```

### Test Coverage Best Practices

1. **Happy Path**: Test normal, expected behavior
2. **Edge Cases**: Empty inputs, None values, boundary conditions
3. **Error Conditions**: Invalid inputs, exceptions, error handling
4. **All Branches**: Test every if/else, try/except path
5. **Mock Assertions**: Verify mock interactions with `assert_called_once_with()`

### Example Test File

```python
import pytest
from unittest.mock import Mock, patch
from module.function import function_to_test


class TestFunctionToTest:
    """Test cases for function_to_test"""

    def test_function_to_test_happy_path(self):
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result == expected_output

    def test_function_to_test_with_none_input(self):
        # Arrange
        input_data = None

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result is None

    @patch("module.function.external_dependency")
    def test_function_to_test_with_mocked_dependency(self, mock_dep):
        # Arrange
        mock_dep.return_value = "mocked_value"

        # Act
        result = function_to_test({"key": "value"})

        # Assert
        assert result == "expected_with_mocked_value"
        mock_dep.assert_called_once()
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError` when running tests

**Solution**: Ensure you're running from the project root:
```bash
cd /path/to/backend-core
python -m pytest tests/
```

#### 2. Coverage Not 100%

**Problem**: Tests pass but coverage < 100%

**Solution**:
1. Run coverage with missing lines report:
   ```bash
   python -m pytest tests/ --cov=. --cov-report=term-missing
   ```
2. Check which lines are missing
3. Add tests for uncovered code paths

#### 3. Docker Container Won't Stop

**Problem**: Test containers remain running

**Solution**:
```bash
docker-compose -f docker-compose.test.yml down -v
docker ps  # Verify containers stopped
```

#### 4. Database Connection Errors

**Problem**: Tests fail with database connection errors

**Solution**:
1. Ensure `APP_ENVIRONMENT=testing` is set
2. Check PostgreSQL is running (for Docker tests)
3. Verify database credentials in environment variables

#### 5. Async Test Warnings

**Problem**: `DeprecationWarning` for async tests

**Solution**: Ensure `pytest-asyncio` is installed and `asyncio_mode = auto` is in `pytest.ini`

### Debugging Tests

#### 1. Print Debug Output

```python
def test_with_debug():
    result = function()
    print(f"Debug: result = {result}")  # Will show in test output with -v
    assert result == expected
```

#### 2. Use pytest's Built-in Debugger

```bash
python -m pytest tests/test_file.py::test_function -v --pdb
```

This drops into a debugger when a test fails.

#### 3. Run Single Test

```bash
python -m pytest tests/utils/test_util.py::TestSanitizeStringInput::test_sanitize_string_input_removes_extra_spaces -v -s
```

The `-s` flag shows print statements.

### Getting Help

1. Check test output with `-v` (verbose) flag
2. Review coverage report: `open htmlcov/index.html`
3. Check GitHub Actions logs for CI failures
4. Ensure all dependencies are installed: `pip install -r requirements-dev.txt`

## Coverage Commands Cheat Sheet

```bash
# Generate HTML coverage report
python -m pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html

# Show coverage in terminal with missing lines
python -m pytest tests/ --cov=. --cov-report=term-missing

# Generate XML coverage report (for CI)
python -m pytest tests/ --cov=. --cov-report=xml

# Fail if coverage < 100%
python -m pytest tests/ --cov=. --cov-fail-under=100

# Combined: All reports + fail under 100%
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-fail-under=100
```

## Best Practices Summary

1. **Write tests first** (TDD approach) or alongside code
2. **Mock all external dependencies** (DB, APIs, file I/O)
3. **Test one behavior per test** - keep tests focused
4. **Use descriptive test names** - they serve as documentation
5. **Aim for 100% coverage** - it's required, not optional
6. **Run tests before committing** - pre-commit hooks will enforce this
7. **Keep tests fast** - unit tests should run in seconds, not minutes
8. **Make tests independent** - tests should not depend on each other
9. **Use fixtures for common setup** - DRY principle
10. **Document complex test scenarios** - add comments when needed

## Next Steps

1. Review existing test files in `tests/` directory
2. Run tests locally to ensure setup works
3. Check coverage report to identify gaps
4. Write tests for new features before implementation
5. Monitor GitHub Actions for CI test results

---

For questions or issues with the testing infrastructure, please refer to this guide or check the existing test files for examples.
