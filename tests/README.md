# Testing and Quality Assurance

This directory contains tests for the Data Compliance Audit system, focusing on the PII tagging engine and dbt macros.

## Test Structure

### Unit Tests
- `test_tagging_engine.py`: Tests for the PII tagging functionality
  - Column name pattern matching
  - Value-based PII detection
  - DataFrame scanning
  - Edge cases and error handling

### dbt Tests
- `dbt_project/tests/test_pii_check.sql`: Tests for the dbt PII check macro
  - Macro compilation
  - Basic functionality
  - Data validation

### Test Helpers
- `dbt_project/macros/test_helpers.sql`: Helper macros for dbt tests
  - Test data setup
  - Test cleanup
  - Reusable test components

## Running Tests

### Python Unit Tests

1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests with coverage:
   ```bash
   pytest -v --cov=src --cov-report=term-missing
   ```

3. Generate an HTML coverage report:
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html  # On macOS/Linux
   start htmlcov/index.html  # On Windows
   ```

### dbt Tests

1. Navigate to the dbt project directory:
   ```bash
   cd dbt_project
   ```

2. Run dbt tests:
   ```bash
   dbt test --models test_pii_check
   ```

## Test Coverage

The test suite aims to cover:
- All PII detection patterns
- Edge cases and error conditions
- Data type handling
- Performance with various input sizes
- Integration with dbt

## Adding New Tests

1. For Python code:
   - Create a new file `test_*.py` in the `tests` directory
   - Follow pytest conventions
   - Use fixtures for common test data

2. For dbt macros:
   - Add SQL test files in `dbt_project/tests/`
   - Use the `test_` prefix for test models
   - Leverage test helpers for common patterns

## Continuous Integration

The test suite can be integrated into your CI/CD pipeline using the provided pytest and dbt test commands.
