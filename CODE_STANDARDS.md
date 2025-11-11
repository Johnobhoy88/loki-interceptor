# Code Standards and Guidelines

This document defines the coding standards, best practices, and quality expectations for the LOKI Interceptor project.

## Table of Contents

1. [Python Code Style](#python-code-style)
2. [Type Hints and Type Safety](#type-hints-and-type-safety)
3. [Documentation and Docstrings](#documentation-and-docstrings)
4. [Testing Standards](#testing-standards)
5. [Error Handling](#error-handling)
6. [Performance Guidelines](#performance-guidelines)
7. [Security Best Practices](#security-best-practices)
8. [Commit Message Standards](#commit-message-standards)
9. [Code Review Checklist](#code-review-checklist)
10. [Tools and Automation](#tools-and-automation)

---

## Python Code Style

### Formatting with Black

All Python code must be formatted using [Black](https://github.com/psf/black).

**Configuration:**
- Line length: 100 characters
- Target Python version: 3.11+

**Auto-formatting:**
```bash
black .
```

### Import Organization with isort

Imports must be organized using [isort](https://pycqa.github.io/isort/) following the Black profile.

**Rules:**
1. Standard library imports (alphabetical)
2. Third-party imports (alphabetical)
3. Local/application imports (alphabetical)

**Example:**
```python
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import click
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

from backend.core import config
from backend.models import User
```

**Auto-formatting:**
```bash
isort .
```

### Code Quality with Flake8

All code must pass [Flake8](https://flake8.pycqa.org/) linting.

**Key Rules:**
- Maximum complexity: 10 (McCabe complexity)
- Maximum line length: 100 characters
- No trailing whitespace
- 2 blank lines between module-level definitions
- 1 blank line between class methods

**Configuration:** See `.flake8`

**Check code:**
```bash
flake8 backend/
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | lowercase_with_underscores | `compliance_engine.py` |
| Classes | PascalCase | `ComplianceOrchestrator` |
| Functions | lowercase_with_underscores | `validate_document()` |
| Constants | UPPERCASE_WITH_UNDERSCORES | `MAX_RETRY_ATTEMPTS = 3` |
| Private methods | _lowercase_with_underscore | `_internal_validate()` |
| Protected methods | _lowercase_with_underscore | `_protected_method()` |
| Module-level private | _lowercase_with_underscore | `_internal_config` |

### Line Length

Maximum line length is **100 characters**. This is enforced by Black and Flake8.

```python
# Good
def validate_compliance(
    document: Document,
    config: ComplianceConfig,
    strict_mode: bool = False
) -> ValidationResult:
    """Validate document against compliance rules."""

# Bad
def validate_compliance(document: Document, config: ComplianceConfig, strict_mode: bool = False) -> ValidationResult:
    """Validate document against compliance rules."""
```

### Comments

- Use comments sparingly; prefer clear code
- Use `#` for inline comments with a space: `# Comment here`
- Multi-line comments should be docstrings, not comment blocks
- Avoid obvious comments

```python
# Good
user_count = len(active_users)  # Filter includes verified users only

# Bad
user_count = len(active_users)  # Get the count of users
x = y + 1  # Add one to y
```

---

## Type Hints and Type Safety

### Type Hints are Required

All function signatures must include type hints. This is enforced by mypy.

**Example:**
```python
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

def process_documents(
    documents: List[Document],
    config: Optional[ProcessingConfig] = None,
    callbacks: Optional[Dict[str, Any]] = None
) -> ProcessingResult:
    """
    Process multiple documents.

    Args:
        documents: List of documents to process
        config: Optional processing configuration
        callbacks: Optional callback functions

    Returns:
        Processing results with metadata
    """
    # Implementation
```

### Type Hint Best Practices

1. **Use specific types over generic Any**
   ```python
   # Good
   def get_config(key: str) -> str | None:
       ...

   # Bad
   def get_config(key):
       ...
   ```

2. **Use Union for multiple types**
   ```python
   from typing import Union

   def parse_value(value: Union[str, int, float]) -> float:
       ...
   ```

3. **Use Optional for nullable values**
   ```python
   from typing import Optional

   def get_user(user_id: int) -> Optional[User]:
       ...
   ```

4. **Use Protocol for structural typing**
   ```python
   from typing import Protocol

   class Validator(Protocol):
       def validate(self, data: Dict) -> bool:
           ...
   ```

### Type Checking with mypy

Run type checks regularly:

```bash
mypy backend/
```

**Configuration:** See `mypy.ini`

---

## Documentation and Docstrings

### Docstring Format

Use Google-style docstrings for all public modules, classes, and functions.

**Module Docstring:**
```python
"""
Compliance orchestration engine for multi-framework validation.

This module handles the orchestration of compliance checks across different
regulatory frameworks including FCA, GDPR, and tax compliance.
"""
```

**Class Docstring:**
```python
class ComplianceOrchestrator:
    """Orchestrate compliance checks across multiple frameworks.

    This class manages the execution and coordination of compliance validators
    for different regulatory frameworks.

    Attributes:
        config: Orchestration configuration
        validators: Dictionary of framework validators
        logger: Logger instance

    Example:
        >>> orchestrator = ComplianceOrchestrator(config)
        >>> result = orchestrator.validate_document(doc)
    """
```

**Function Docstring:**
```python
def validate_document(
    document: Document,
    frameworks: List[str],
    strict: bool = False
) -> ValidationResult:
    """Validate document against specified compliance frameworks.

    Performs comprehensive compliance validation across multiple frameworks
    and returns detailed validation results.

    Args:
        document: Document to validate
        frameworks: List of framework codes (e.g., ['FCA', 'GDPR'])
        strict: If True, fail on first validation error

    Returns:
        ValidationResult containing all validation details

    Raises:
        ValueError: If frameworks list is empty
        DocumentError: If document is invalid

    Note:
        This method may take considerable time for complex documents.
        Consider using async_validate_document for large batches.

    Example:
        >>> doc = Document(content="...")
        >>> result = validate_document(doc, ["FCA", "GDPR"])
        >>> if result.is_valid:
        ...     print("Validation passed")
    """
```

### Docstring Coverage

Maintain at least 50% docstring coverage. Check with:

```bash
interrogate --vv -f html .
```

**Required documentation:**
- All public modules
- All public classes
- All public methods and functions
- Complex private methods (if not self-explanatory)

### Inline Comments

Use inline comments for complex logic, not for obvious code:

```python
# Good - explains the "why"
if compliance_score < MINIMUM_THRESHOLD:
    # Need human review for borderline cases to ensure accuracy
    escalate_to_human_reviewer(document)

# Bad - explains the obvious
x = y + 1  # Add one to y
```

---

## Testing Standards

### Test Organization

**Directory structure:**
```
backend/
  tests/
    __init__.py
    test_models.py
    test_api.py
    compliance/
      test_orchestrator.py
      test_validators.py
    gates/
      test_implementation.py
```

### Test Naming

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*`
- Test functions: `test_*`

```python
class TestComplianceOrchestrator:
    """Tests for ComplianceOrchestrator."""

    def test_validate_document_with_valid_input(self):
        """Should validate document successfully."""
        # Arrange
        doc = self._create_valid_document()

        # Act
        result = self.orchestrator.validate_document(doc)

        # Assert
        assert result.is_valid
```

### Test Coverage

**Minimum coverage requirements:**
- Overall: 75%
- Critical paths: 90%
- Compliance modules: 85%

**Check coverage:**
```bash
pytest --cov=backend --cov-report=html
```

### AAA Pattern

Follow the Arrange-Act-Assert pattern:

```python
def test_gate_blocks_invalid_document(self):
    """Gate should block documents that fail validation."""
    # Arrange - set up test data
    invalid_doc = Document(content="<invalid>")
    gate = ComplianceGate(config)

    # Act - perform the operation
    result = gate.evaluate(invalid_doc)

    # Assert - verify the results
    assert not result.passed
    assert "validation" in result.message.lower()
```

### Test Markers

Use pytest markers for organizing tests:

```python
@pytest.mark.compliance
def test_fca_compliance_validation():
    """Test FCA compliance validation."""
    ...

@pytest.mark.integration
def test_multi_framework_validation():
    """Test validation across multiple frameworks."""
    ...

@pytest.mark.slow
def test_large_document_processing():
    """Test processing of large documents."""
    ...
```

### Mocking and Fixtures

Use fixtures for test setup:

```python
@pytest.fixture
def compliance_config():
    """Return test compliance configuration."""
    return ComplianceConfig(
        frameworks=['FCA', 'GDPR'],
        strict_mode=True
    )

@pytest.fixture
def sample_document():
    """Return a sample document for testing."""
    return Document(
        content="Sample content",
        metadata={"source": "test"}
    )

def test_validation(compliance_config, sample_document):
    """Test validation with fixtures."""
    orchestrator = ComplianceOrchestrator(compliance_config)
    result = orchestrator.validate_document(sample_document)
    assert result is not None
```

---

## Error Handling

### Exception Hierarchy

Create custom exceptions for different error types:

```python
class LOKIError(Exception):
    """Base exception for LOKI errors."""
    pass

class ValidationError(LOKIError):
    """Raised when validation fails."""
    pass

class ComplianceError(LOKIError):
    """Raised when compliance check fails."""
    pass

class ConfigurationError(LOKIError):
    """Raised for configuration errors."""
    pass
```

### Exception Handling Best Practices

```python
# Good - specific exceptions
try:
    result = validate_document(doc)
except ValidationError as e:
    logger.error("Validation failed", exc_info=True)
    raise
except ComplianceError as e:
    logger.warning("Compliance issue detected", exc_info=True)
    handle_compliance_issue(e)

# Bad - generic exception handling
try:
    result = validate_document(doc)
except Exception:
    pass
```

### Logging Errors

Always include context in error logging:

```python
import logging

logger = logging.getLogger(__name__)

try:
    process_document(doc)
except ValidationError as e:
    logger.error(
        "Document validation failed",
        extra={
            "document_id": doc.id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        },
        exc_info=True
    )
```

---

## Performance Guidelines

### Code Complexity

Maximum cyclomatic complexity: **10**

Check with:
```bash
flake8 --statistics backend/
```

### Function Length

Keep functions focused and under 50 lines when possible:

```python
# Good - focused function
def validate_tax_compliance(document: Document) -> bool:
    """Validate tax compliance requirements."""
    if not document.has_tax_id():
        return False

    if not document.has_tax_returns():
        return False

    return True

# Bad - too many responsibilities
def process_everything(document: Document) -> bool:
    # Validate tax
    # Validate GDPR
    # Validate FCA
    # Update database
    # Send notifications
    # Generate reports
    # ... 100 lines total
```

### Async/Await

Use async for I/O-bound operations:

```python
# Good - async for I/O
async def fetch_documents(doc_ids: List[str]) -> List[Document]:
    """Fetch multiple documents concurrently."""
    tasks = [get_document(doc_id) for doc_id in doc_ids]
    return await asyncio.gather(*tasks)

# Avoid blocking operations in async code
async def process_documents(docs: List[Document]):
    for doc in docs:
        # Don't do this - blocks the event loop
        time.sleep(1)

        # Do this instead
        await asyncio.sleep(1)
```

---

## Security Best Practices

### Password and Secrets

Never hardcode passwords or secrets:

```python
# Bad
API_KEY = "sk_live_12345678"
DATABASE_URL = "postgresql://user:password@localhost/db"

# Good
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

### SQL Injection Prevention

Always use parameterized queries:

```python
# Good - parameterized query
query = select(User).where(User.id == user_id)
user = session.execute(query).scalar_one_or_none()

# Bad - string concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"
user = session.execute(text(query)).scalar_one_or_none()
```

### Authentication and Authorization

```python
# Always verify authentication and authorization
@app.get("/compliance/documents")
async def get_documents(current_user: User = Depends(get_current_user)):
    """Get documents for authenticated user."""
    # Verify user has permission
    if not current_user.has_permission("read:documents"):
        raise HTTPException(status_code=403, detail="Forbidden")

    return get_user_documents(current_user.id)
```

### Dependency Validation

Scan for vulnerable dependencies:

```bash
safety check
```

---

## Commit Message Standards

### Format

Follow Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only
- **style**: Code style changes (Black, isort)
- **refactor**: Code refactoring without feature/fix
- **perf**: Performance improvements
- **test**: Test additions or modifications
- **chore**: Build, CI, dependencies
- **ci**: CI/CD configuration changes

### Examples

```
feat(compliance): add FCA consumer duty validator

Add new validator for FCA consumer duty compliance checks.
Implements comprehensive validation rules for consumer protection
requirements under the updated FCA regulations.

Implements #42
Closes #43
```

```
fix(gates): resolve false positive in risk categorizer

Fix issue where legitimate business transactions were incorrectly
flagged as high-risk. Improved risk scoring algorithm to consider
transaction context and historical patterns.

Fixes #89
```

```
docs: update API documentation

Update API documentation to reflect recent changes to the
compliance validation endpoints.
```

### Guidelines

1. Use imperative mood: "add" not "added" or "adds"
2. Don't capitalize the subject
3. No period at the end of subject
4. Keep subject under 50 characters
5. Reference issues: "Closes #123" or "Fixes #456"
6. Explain what and why, not how

---

## Code Review Checklist

### Before Submitting for Review

- [ ] Code passes all linters (Black, Flake8, isort, mypy)
- [ ] All new code has docstrings
- [ ] All functions have type hints
- [ ] Test coverage meets minimum threshold (75%)
- [ ] All tests pass: `pytest`
- [ ] No hardcoded secrets or credentials
- [ ] Security issues checked: `bandit -r backend/`
- [ ] Complexity checked: `flake8 --max-complexity=10`
- [ ] Commit message follows Conventional Commits
- [ ] Branch is up to date with main

### During Code Review

- [ ] Code is clear and maintainable
- [ ] Naming is descriptive and follows conventions
- [ ] No unnecessary complexity
- [ ] Error handling is appropriate
- [ ] Security best practices are followed
- [ ] Performance implications considered
- [ ] Documentation is accurate and complete
- [ ] Tests cover happy path and error cases
- [ ] No code duplication
- [ ] Dependencies are necessary and vetted

### Common Issues

| Issue | Suggestion |
|-------|-----------|
| Large functions | Break into smaller, focused functions |
| Unclear names | Rename to be descriptive |
| Missing docstrings | Add documentation |
| Type hints missing | Add type annotations |
| No tests | Add comprehensive tests |
| Hardcoded values | Use configuration |
| Catching all exceptions | Catch specific exceptions |

---

## Tools and Automation

### Pre-commit Hooks

Install and use pre-commit hooks to enforce standards:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

### Automated Checks

Run before committing:

```bash
# Format code
black .
isort .

# Check code quality
flake8 backend/ tests/
mypy backend/

# Security check
bandit -r backend/

# Run tests with coverage
pytest --cov=backend --cov-report=term-missing

# Check dependency vulnerabilities
safety check
```

### CI/CD Integration

All checks run automatically on:
- Pull request creation
- Commits to main branch
- Weekly scheduled runs

See `.github/workflows/code-quality.yml` for details.

### IDE Configuration

**VS Code settings.json:**
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true
}
```

---

## Continuous Improvement

### Code Metrics

Regular code quality metrics:
- Cyclomatic complexity
- Test coverage
- Code duplication
- Technical debt tracking

### Technical Debt

Log technical debt as comments:

```python
# TODO: Refactor this function for better performance #123
# FIXME: Handle edge case for empty documents #456
# HACK: Temporary workaround for API rate limiting
```

Use GitHub issues to track long-term improvements.

---

## Enforcement

- **Automated**: Pre-commit hooks, CI/CD pipelines
- **Manual**: Code review process
- **Escalation**: Blocking merges for critical issues

For questions or clarifications, contact the development team or open an issue.

---

**Last Updated:** 2025-11-11
**Maintained By:** Code Quality Engineering Team
