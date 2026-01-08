# Testing Quick Start Guide

Get started with testing in 5 minutes or less.

## Prerequisites

```bash
# Ensure you're in the project directory
cd /Users/sathwik/Documents/GitHub/ssq/backend-core

# Install dependencies
pip install -r requirements-dev.txt
```

## Run Tests Now

### Option 1: Local (Fastest)

```bash
python -m pytest tests/ -v
```

### Option 2: Docker (Most Reliable)

```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit && \
docker-compose -f docker-compose.test.yml down
```

### Option 3: VS Code (Best DX)

1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Tasks: Run Task"
3. Select "Run Unit Tests (Docker)"

## Check Coverage

```bash
# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows
```

## Write Your First Test

1. **Copy template**:
```bash
cp tests/TEST_TEMPLATE.py tests/your_module/test_your_function.py
```

2. **Edit the file**:
```python
import pytest
from unittest.mock import patch, Mock
from your_module.function import your_function


class TestYourFunction:
    """Test cases for your_function"""

    def test_your_function_happy_path(self):
        # Arrange
        input_data = "test"

        # Act
        result = your_function(input_data)

        # Assert
        assert result == "expected_output"
```

3. **Run your test**:
```bash
python -m pytest tests/your_module/test_your_function.py -v
```

## Common Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific file
python -m pytest tests/utils/test_util.py -v

# Run specific test
python -m pytest tests/utils/test_util.py::TestSanitizeStringInput::test_sanitize_string_input_removes_extra_spaces -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# Run tests that match a pattern
python -m pytest tests/ -k "test_sanitize" -v
```

## Troubleshooting

### Tests fail with import errors
```bash
# Ensure you're in the project root
cd /Users/sathwik/Documents/GitHub/ssq/backend-core

# Reinstall dependencies
pip install -r requirements-dev.txt
```

### Docker won't stop
```bash
docker-compose -f docker-compose.test.yml down -v
```

### Coverage is below 100%
```bash
# See which lines are missing
python -m pytest tests/ --cov=. --cov-report=term-missing

# Then add tests for the missing lines
```

## Next Steps

1. Read **TESTING.md** for comprehensive guide
2. Check **TEST_IMPLEMENTATION_SUMMARY.md** for project status
3. Use **TEST_TEMPLATE.py** for test examples
4. Run tests before every commit
5. Aim for 100% coverage on all new code

## VS Code Tips

- **Run tests**: Click test icon in sidebar
- **Debug tests**: Click debug icon next to test
- **Coverage gutters**: Install "Coverage Gutters" extension to see coverage inline

## GitHub Actions

Every push to master/develop/fix-agent-flow runs:
1. All unit tests
2. Coverage check (must be 100%)
3. Linting and formatting checks

**PR won't merge if tests fail or coverage < 100%**

## Need Help?

- Refer to **TESTING.md** for detailed documentation
- Check existing tests in `tests/` for examples
- Look at **TEST_TEMPLATE.py** for common patterns
