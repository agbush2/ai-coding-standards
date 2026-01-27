# Python Testing Standards
Implementation of: /testing_standards.md

## Relationship to Standards
This file provides the Python-specific implementation ("How") for the testing strategies and quality gates defined in `/testing_standards.md` ("What").

## Frameworks
- **Runner**: `pytest`
- **Mocking**: `pytest-mock` (use `mocker` fixture).
- **Async**: `pytest-asyncio`.
- **Network Blocking**: `pytest-socket` (ensure `socket.socket` is disabled in unit tests).

## Patterns
- **Fixtures**: Use `conftest.py` for shared fixtures.
- **Factories**: Use `factory_boy` or custom Pydantic factories.
- **Markers**: Use `@pytest.mark.integration` for slow tests.

## Coverage Reporting
- **Threshold**: Minimum 80% code coverage required for PR approval.
- **Reporting Tools**: Use `pytest-cov` and integrate with Coveralls or Codecov for CI reporting.

## Example: Unit Test
```python
import pytest
from src.core.service import calculate_total

def test_calculate_total_success():
    # Arrange
    items = [10, 20]
    # Act
    result = calculate_total(items)
    # Assert
    assert result == 30
```

## Example: Mocking
```python
def test_external_call(mocker):
    mock_get = mocker.patch("src.services.client.httpx.AsyncClient.get")
    mock_get.return_value.status_code = 200
    # ...
```
