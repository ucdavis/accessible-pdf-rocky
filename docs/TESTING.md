# Testing Guide

This document describes the testing infrastructure and best practices for the project.

## Overview

The project uses a comprehensive testing strategy with:

- **.NET**: xUnit with coverage tracking
- **Python**: pytest for HPC runner tests
- **JavaScript/TypeScript**: Vitest for client and worker tests
- **CI/CD**: Azure Pipelines for automated testing
- **Coverage**: Codecov integration for coverage reports

## Running Tests

### All Tests

```bash
# Run all tests
just test

# Run with coverage
just test-coverage
```

### .NET Tests

```bash
# Run .NET tests only
just test-dotnet

# With coverage
just test-dotnet-coverage

# Or manually
cd tests && dotnet test
```

### Python Tests

```bash
# Run Python tests only (hpc_runner)
just test-python

# With coverage
just test-python-coverage

# Or manually
cd hpc_runner && uv run pytest
```

### JavaScript/TypeScript Tests

```bash
# Run JS/TS tests only
just test-js

# With coverage
just test-js-coverage

# Or manually
cd client && npm test
cd workers && npm test
```

## Test Structure

### .NET (server & tests)

```
tests/
├── tests.csproj               # xUnit project file
├── JobControllerTests.cs      # Controller tests
├── DatabaseApiClientTests.cs  # Database client tests
└── MetricsClientTests.cs      # Metrics client tests
```

**Conventions:**

- Test files: `*Tests.cs`
- Test methods: `[Fact]` or `[Theory]` attributes
- Use `xUnit` assertions
- Use mocking libraries (Moq, NSubstitute)

### Python (hpc_runner)

```
hpc_runner/
├── pyproject.toml             # pytest configuration
└── tests/
    ├── test_ai_processors.py  # AI processor tests
    └── test_runner.py         # Main runner tests
```

**Conventions:**

- Test files: `test_*.py`
- Test functions: `test_*`
- Use fixtures for setup/teardown
- Use `pytest.mark` for categorization

### Client (React + Vite + Vitest)

```
client/
├── src/
│   ├── routes/
│   │   ├── __tests__/
│   │   │   ├── index.test.tsx      # Home page tests
│   │   │   ├── upload.test.tsx     # Upload page tests
│   │   │   └── jobs.test.tsx       # Jobs routes tests
│   ├── components/
│   │   └── __tests__/
│   │       └── components.test.tsx # Component tests
│   └── lib/
│       └── __tests__/
│           └── api.test.ts         # API client tests
├── vitest.config.ts           # Vitest configuration
└── vitest.setup.ts            # Test setup
```

**Conventions:**

- Test files: `*.test.tsx` or `*.test.ts`
- Co-locate tests in `__tests__/` subdirectories next to source code
- Use Vitest with React Testing Library
- Test user interactions, not implementation

### Workers (Vitest)

```
workers/
├── tests/
│   ├── job-status.test.ts     # Status query tests
│   ├── submit-job.test.ts     # Job submission tests
│   └── upload.test.ts         # Upload worker tests
└── vitest.config.ts           # Vitest configuration
```

**Conventions:**

- Test files: `*.test.ts`
- Use Vitest's built-in mocking
- Test worker behavior in isolation

## Writing Tests

### .NET Example

```csharp
using Xunit;

public class ModuleTests
{
    [Fact]
    public void TestFunction()
    {
        // Arrange
        var expected = "value";
        
        // Act
        var result = MyFunction();
        
        // Assert
        Assert.Equal(expected, result);
    }
}
```

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
# .NET
cd tests && dotnet test --collect:"XPlat Code Coverage"
# Coverage report in tests/TestResults/

# Python (hpc_runner)
cd hpc_runner && uv run pytest --cov=. --cov-report=html
open htmlcov/index.html

# Client
cd client && npm run test:coverage
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

### Azure Pipelines

- `azure-pipelines.yml` - Main CI/CD pipeline (tests + linting + deployment)
- Separate jobs for .NET, Python, and TypeScript tests
- Parallel test execution for faster feedback

### Pipeline Status

View test results in Azure DevOps portal

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

### .NET

```bash
# Run specific test
dotnet test --filter "FullyQualifiedName=Namespace.ClassName.TestMethod"

# Verbose output
dotnet test -v detailed

# Debug mode
dotnet test --logger "console;verbosity=detailed"
```

### Python

```bash
# Run specific test
uv run pytest tests/test_runner.py::test_function

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

### .NET Dependencies

- `xunit` - Test framework
- `xunit.runner.visualstudio` - Test runner
- `Moq` or `NSubstitute` - Mocking libraries
- `coverlet.collector` - Coverage collection

### Python Dependencies

- `pytest` - Test framework
- `pytest-cov` - Coverage plugin

### JavaScript/TypeScript Dependencies

- `@testing-library/react` - React testing utilities (frontend only)
- `jsdom` - DOM environment for tests
- `vitest` - Fast test framework

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

### Vitest configuration issues

- Clear cache: `npx vitest --clearCache`
- Check `vitest.config.ts` and `vitest.setup.ts`
- Verify Vite/Next.js compatibility

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [.NET testing](https://learn.microsoft.com/en-us/dotnet/core/testing/)
