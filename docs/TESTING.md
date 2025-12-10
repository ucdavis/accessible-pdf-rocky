# Testing Guide

This document describes the testing infrastructure and best practices for the project.

## Overview

The project uses a comprehensive testing strategy with:

- **Python**: pytest with coverage tracking
- **JavaScript/TypeScript**: Jest (frontend) and Vitest (workers)
- **CI/CD**: GitHub Actions for automated testing
- **Coverage**: Codecov integration for coverage reports

## Running Tests

### All Tests

```bash
# Run all tests
just test

# Run with coverage
just test-coverage
```

### Python Tests

```bash
# Run Python tests only
just test-python

# With coverage
just test-python-coverage

# Or manually
cd controller && uv run pytest
cd hpc_runner && uv run pytest
```

### JavaScript/TypeScript Tests

```bash
# Run JS/TS tests only
just test-js

# With coverage
just test-js-coverage

# Or manually
cd frontend && npm test
cd workers && npm test
```

## Test Structure

### Python (controller & hpc_runner)

```
controller/
├── tests/
│   ├── test_main.py           # FastAPI endpoint tests
│   └── hpc/
│       └── test_submit.py     # SLURM submission tests
└── pyproject.toml             # pytest configuration

hpc_runner/
├── tests/
│   └── test_runner.py         # PDF analysis tests
└── pyproject.toml             # pytest configuration
```

**Conventions:**

- Test files: `test_*.py`
- Test functions: `test_*`
- Use fixtures for setup/teardown
- Use `pytest.mark` for categorization

### Frontend (Next.js + Jest)

```
frontend/
├── src/app/__tests__/
│   └── page.test.tsx          # Component tests
├── jest.config.js             # Jest configuration
└── jest.setup.js              # Test setup
```

**Conventions:**

- Test files: `*.test.tsx` or `*.spec.tsx`
- Use React Testing Library
- Test user interactions, not implementation

### Workers (Vitest)

```
workers/
├── tests/
│   └── upload.test.ts         # Worker tests
└── vitest.config.ts           # Vitest configuration
```

**Conventions:**

- Test files: `*.test.ts` or `*.spec.ts`
- Use Vitest's built-in mocking
- Test worker behavior in isolation

## Writing Tests

### Python Example

```python
"""Tests for module."""

import pytest

def test_function():
    """Test description."""
    result = my_function()
    assert result == expected
    
@pytest.fixture
def mock_data():
    """Fixture description."""
    return {"key": "value"}
```

### TypeScript Example

```typescript
import { describe, it, expect } from 'vitest'

describe('Module', () => {
  it('should work', () => {
    const result = myFunction()
    expect(result).toBe(expected)
  })
})
```

## Coverage Requirements

- **Target**: >80% coverage for all components
- **Enforcement**: CI fails if tests fail (coverage is advisory)
- **Reports**: Available in `htmlcov/` (Python) and `coverage/` (JS)

### View Coverage Locally

```bash
# Python
cd controller && uv run pytest --cov=. --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend && npm run test:coverage
open coverage/lcov-report/index.html

# Workers  
cd workers && npm run test:coverage
open coverage/index.html
```

## CI/CD Integration

Tests run automatically on:

- Every push to `main`
- Every pull request
- Schedule (weekly)

### GitHub Actions Workflows

- `.github/workflows/ci.yml` - Main CI workflow (tests + linting)
- `.github/workflows/security.yml` - Security audits
- `.github/workflows/codeql.yml` - Code security scanning

### Workflow Status

View test results: <https://github.com/ucdavis/accessible-pdf-rocky/actions>

## Best Practices

### Do's

✅ Write tests for new features
✅ Test edge cases and error conditions
✅ Use descriptive test names
✅ Keep tests isolated and independent
✅ Use fixtures/mocks for external dependencies
✅ Run tests locally before pushing

### Don'ts

❌ Don't test implementation details
❌ Don't skip tests without good reason
❌ Don't commit failing tests
❌ Don't write flaky tests
❌ Don't test third-party code

## Debugging Tests

### Python

```bash
# Run specific test
uv run pytest tests/test_main.py::test_function

# Verbose output
uv run pytest -v

# Show print statements
uv run pytest -s

# Stop on first failure
uv run pytest -x

# Interactive debugging
uv run pytest --pdb
```

### JavaScript/TypeScript

```bash
# Run specific test
npm test -- page.test.tsx

# Watch mode
npm run test:watch

# Update snapshots
npm test -- -u
```

## Test Dependencies

### Python Dependencies

- `pytest` - Test framework
- `pytest-cov` - Coverage plugin
- `pytest-asyncio` - Async test support (controller only)
- `httpx` - HTTP client for FastAPI tests

### JavaScript/TypeScript Dependencies

#### Frontend

- `jest` - Test framework
- `@testing-library/react` - React testing utilities
- `@testing-library/jest-dom` - DOM matchers

#### Workers

- `vitest` - Fast test framework
- `@vitest/coverage-v8` - Coverage reporter

## Continuous Improvement

- Review coverage reports regularly
- Add tests for bug fixes
- Refactor tests as code evolves
- Update this guide as practices change

## Troubleshooting

### Tests fail locally but pass in CI

- Check Python/Node versions match
- Ensure dependencies are synced (`uv sync`, `npm ci`)
- Check for environment-specific issues

### Import errors in Python tests

- Verify `sys.path` setup in test files
- Check module structure and `__init__.py` files
- Ensure dependencies are installed

### Jest configuration issues

- Clear cache: `npm test -- --clearCache`
- Check `jest.config.js` and `jest.setup.js`
- Verify Next.js compatibility

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Jest documentation](https://jestjs.io/)
- [Vitest documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
