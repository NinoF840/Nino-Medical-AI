# Italian Medical NER - Test Suite

This directory contains the comprehensive test suite for the Italian Medical NER project.

## Test Structure

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── test_final_optimized_ner.py    # Tests for FinalOptimizedItalianMedicalNER
├── test_enhanced_inference.py     # Tests for EnhancedItalianMedicalNER
├── test_api_service.py            # Tests for FastAPI service
├── test_utils.py                  # Tests for utility functions
└── README.md                      # This file
```

## Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests requiring model files
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.mock` - Tests using extensive mocking
- `@pytest.mark.slow` - Performance tests that take longer to run

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest -m unit tests/
pytest -m integration tests/
pytest -m api tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_enhanced_inference.py
```

### Using the Test Runner

The project includes a convenient test runner script:

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type api

# Run with verbose output
python run_tests.py --verbose

# Check dependencies
python run_tests.py --check-deps

# Run with coverage report
python run_tests.py --coverage
```

## Test Configuration

### pytest.ini

The `pytest.ini` file in the project root configures:
- Test discovery patterns
- Excluded directories (avoids testing PyTorch internals)
- Test markers
- Output formatting

### conftest.py

Contains shared fixtures and test configuration:
- Sample Italian medical texts
- Mock objects for models and tokenizers
- Test data generators
- API test clients

## Test Files Description

### test_final_optimized_ner.py
Tests for the main NER model class including:
- Model initialization
- Pipeline creation
- Pattern loading
- Entity detection

### test_enhanced_inference.py
Comprehensive tests for the enhanced inference pipeline:
- Confidence score calculation
- Pattern enhancement
- BIOES tag processing
- Complete prediction workflow

### test_api_service.py
API service tests covering:
- Endpoint functionality
- Authentication
- Request/response validation
- Error handling
- Performance testing

### test_utils.py
Utility function tests for:
- Text processing
- Pattern matching
- Confidence calculations
- Entity validation

## Requirements

### Required Packages
- pytest
- torch
- transformers
- fastapi (for API tests)
- httpx (for API testing)

### Optional Packages
- coverage (for coverage reports)
- pytest-cov (alternative coverage tool)

Install test dependencies:
```bash
pip install pytest torch transformers fastapi httpx
```

## Test Data

Tests use sample Italian medical texts and expected entities defined in `conftest.py`:

- Sample medical reports
- Expected entity annotations
- Performance test data
- Mock model responses

## Mocking Strategy

Tests use extensive mocking for:
- Model loading (when actual models aren't available)
- Tokenizer behavior
- API dependencies
- External services

This ensures tests can run in any environment without requiring:
- Large model files
- GPU access
- External API keys

## Integration Tests

Integration tests require actual model files and will be skipped if:
- Model files are not found
- Dependencies are missing
- Environment is not properly configured

## Performance Tests

Marked with `@pytest.mark.slow`, these tests:
- Measure processing time
- Test with large texts
- Validate memory usage
- Check API response times

Skip slow tests during development:
```bash
pytest -m "not slow" tests/
```

## Continuous Integration

The test suite is designed to work in CI environments:
- Uses mocking to avoid external dependencies
- Provides clear pass/fail indicators
- Generates coverage reports
- Supports parallel execution

## Contributing

When adding new tests:

1. Use appropriate markers (`@pytest.mark.unit`, etc.)
2. Add fixtures to `conftest.py` for reusable test data
3. Mock external dependencies appropriately
4. Include both positive and negative test cases
5. Test edge cases and error conditions

## Troubleshooting

### Common Issues

**Tests fail with import errors:**
- Check that all dependencies are installed
- Ensure you're running from the project root directory

**Model loading errors in integration tests:**
- Integration tests will skip if model files aren't available
- Use unit tests with mocking for development

**API tests fail:**
- Ensure FastAPI and httpx are installed
- Check that API service imports are available

**Permission errors:**
- Ensure pytest.ini excludes problematic directories
- Run tests from project root directory

### Debug Mode

Run tests with maximum verbosity and no capture:
```bash
pytest -vvv -s tests/
```

### Test Selection

Run specific tests:
```bash
# Run single test method
pytest tests/test_enhanced_inference.py::TestEnhancedItalianMedicalNER::test_initialization

# Run single test class
pytest tests/test_api_service.py::TestAPIService
```
