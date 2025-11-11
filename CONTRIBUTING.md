# Contributing to LOKI Interceptor

Thank you for your interest in contributing to LOKI Interceptor! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Commit Messages](#commit-messages)
7. [Pull Request Process](#pull-request-process)
8. [Reporting Issues](#reporting-issues)
9. [Documentation](#documentation)

---

## Code of Conduct

### Our Commitment

We are committed to providing a welcoming and inspiring community for all. Please read and adhere to our Code of Conduct:

- **Be Respectful**: Treat all contributors with respect
- **Be Inclusive**: Welcome contributions from all backgrounds
- **Be Professional**: Maintain a professional tone in all communications
- **Be Constructive**: Focus on ideas, not individuals
- **Zero Tolerance**: Harassment, discrimination, or abuse is not tolerated

### Reporting Violations

Report violations to: support@highlandai.com

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Anthropic API key

### Fork & Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/loki-interceptor.git
cd loki-interceptor

# Add upstream remote
git remote add upstream https://github.com/Johnobhoy88/loki-interceptor.git

# Verify remotes
git remote -v
```

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-fix-name

# Branch naming convention:
# - feature/description-with-hyphens
# - fix/description-with-hyphens
# - docs/description-with-hyphens
# - test/description-with-hyphens
```

### 2. Make Your Changes

```bash
# Edit files
nano backend/core/document_validator.py

# Run tests frequently
pytest tests/

# Run linter
pylint backend/

# Format code
black backend/

# Check type hints
mypy backend/
```

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_validator.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run tests matching pattern
pytest -k "validation" -v

# Run slow tests
pytest --slow
```

### 4. Commit Your Changes

```bash
# Stage changes
git add backend/core/document_validator.py

# Commit with message (see guidelines below)
git commit -m "feat: add support for custom validation patterns"

# Or interactive commit
git add -p  # Choose which chunks to stage
```

### 5. Push & Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Go to https://github.com/YOUR_USERNAME/loki-interceptor
# Click "Compare & pull request"
```

---

## Coding Standards

### Python Style

We follow **PEP 8** with some customizations:

```python
# Good: Clear variable names
validation_results = validator.validate_document(text)

# Bad: Unclear abbreviations
val_res = validator.validate_doc(text)

# Good: Proper docstrings
def validate_document(text: str) -> Dict:
    """
    Validate document against compliance modules.

    Args:
        text: Document text to validate

    Returns:
        Dict with validation results

    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    ...

# Bad: No docstring
def validate(t):
    ...
```

### Type Hints

Use type hints for all functions:

```python
from typing import List, Dict, Optional, Tuple

def correct_document(
    text: str,
    validation_results: Dict,
    auto_apply: bool = False
) -> Dict:
    """Apply corrections to document."""
    ...

class DocumentValidator:
    def __init__(self) -> None:
        """Initialize validator."""
        ...

    def validate_document(
        self,
        text: str,
        modules: List[str]
    ) -> Dict:
        """Validate document."""
        ...
```

### File Organization

```
backend/
├── __init__.py                 # Empty or minimal
├── core/
│   ├── __init__.py
│   ├── document_validator.py   # Main validator
│   ├── document_corrector.py   # Main corrector
│   └── correction_patterns.py  # Pattern registry
├── modules/
│   └── fca_uk/
│       ├── __init__.py
│       ├── gates/              # Individual gates
│       ├── patterns.json        # Pattern definitions
│       └── rules.py            # Business logic
├── api/
│   ├── main.py                 # FastAPI app
│   ├── routes/                 # API endpoints
│   └── models/                 # Request/response models
└── tests/
    └── ...
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `DocumentValidator` |
| Functions | snake_case | `validate_document` |
| Constants | UPPER_SNAKE_CASE | `MAX_TEXT_LENGTH` |
| Private | _leading_underscore | `_internal_method` |
| Protected | _leading_underscore | `_protected_attr` |

### Import Organization

```python
# 1. Standard library imports
import json
from typing import Dict, List
from pathlib import Path

# 2. Third-party imports
import requests
from fastapi import FastAPI

# 3. Local imports
from backend.core.document_validator import DocumentValidator
from backend.core.correction_patterns import CorrectionPatternRegistry
```

---

## Testing Guidelines

### Test Structure

```python
# Test file: tests/unit/test_validator.py

import pytest
from backend.core.document_validator import DocumentValidator

class TestDocumentValidator:
    """Tests for DocumentValidator class."""

    @pytest.fixture
    def validator(self):
        """Create validator fixture."""
        return DocumentValidator()

    def test_validate_valid_document(self, validator):
        """Test validation of compliant document."""
        text = "Compliant financial document"
        result = validator.validate_document(
            text,
            "financial",
            ["fca_uk"]
        )
        assert result['validation']['status'] == 'PASS'

    def test_validate_invalid_document(self, validator):
        """Test validation of non-compliant document."""
        text = "Guaranteed 15% returns forever"
        result = validator.validate_document(
            text,
            "financial",
            ["fca_uk"]
        )
        assert result['validation']['status'] == 'FAIL'

    def test_validate_empty_text(self, validator):
        """Test validation handles empty text."""
        with pytest.raises(ValueError):
            validator.validate_document("", "financial", [])
```

### Test Coverage

- Target: >85% code coverage
- All public methods must have tests
- All edge cases should be tested
- Use fixtures for common setup

```bash
# Check coverage
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

### Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/unit/test_validator.py::TestDocumentValidator::test_validate_valid_document

# With output
pytest -v -s

# With coverage
pytest --cov=backend

# Watch mode (requires pytest-watch)
ptw
```

---

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvement
- `chore`: Build, dependencies, etc.

### Example Commits

```
feat(validator): add support for custom validation rules

Add ability to register custom validation patterns at runtime.
Patterns are loaded from a configuration file and compiled
on startup for performance.

Closes #123
```

```
fix(corrector): prevent text corruption in template insertion

The template insertion strategy was not properly handling
multi-line templates, causing text to be inserted in the
wrong location. Fixed by normalizing line endings before
insertion.

Fixes #456
```

```
docs: update deployment guide with Docker examples

Added comprehensive Docker deployment section including:
- Building images
- Docker Compose setup
- Registry configuration
```

---

## Pull Request Process

### Before Creating PR

- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black backend/`
- [ ] Linter passes: `pylint backend/`
- [ ] Types check: `mypy backend/`
- [ ] Coverage maintained: `pytest --cov`
- [ ] Documentation updated
- [ ] Commit messages follow guidelines

### Creating PR

1. **Write descriptive title**:
   ```
   Add support for custom validation patterns
   ```

2. **Write comprehensive description**:
   ```markdown
   ## Description
   Adds ability to register custom validation patterns at runtime.

   ## Changes
   - Add `add_custom_pattern()` method to `CorrectionPatternRegistry`
   - Add validation for pattern configuration
   - Add tests for custom pattern registration

   ## Testing
   - Tested with valid custom patterns
   - Tested with invalid patterns (raises appropriate errors)
   - Coverage: 92%

   ## Related Issues
   Closes #123
   ```

3. **Link related issues**:
   - Use `Closes #123` to auto-close issues
   - Use `Related to #456` for related issues

### PR Review Process

- **At least 1 approval** required before merge
- Address all review comments
- Re-request review after changes
- Be respectful and constructive in discussions

### Merge Criteria

- [ ] All tests passing
- [ ] Code review approved
- [ ] Coverage maintained or improved
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commits are clean and well-described

---

## Reporting Issues

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version: 3.10
- OS: Ubuntu 20.04
- LOKI version: 1.0.0

## Logs
```
Error traceback here
```

## Possible Solution
(Optional) Your suggested fix
```

### Feature Request Template

```markdown
## Description
Clear description of the feature

## Use Case
Why this feature is needed

## Proposed Solution
How this could be implemented

## Alternatives
Other approaches considered

## Additional Context
Any relevant information
```

---

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Include type hints
- Add examples for complex functions

```python
def validate_document(
    text: str,
    document_type: str,
    modules: List[str],
    context: Optional[Dict] = None
) -> Dict:
    """
    Validate document against compliance modules.

    Performs comprehensive compliance validation by running
    the document text against specified compliance modules.
    Each module contains multiple gates that check for
    regulatory violations.

    Args:
        text: Document text to validate. Required.
        document_type: Type of document (e.g., 'financial').
            Used to apply document-specific rules.
        modules: List of compliance modules to check against.
            Valid values: 'fca_uk', 'gdpr_uk', 'tax_uk', etc.
        context: Optional context dictionary for validation.
            Can include fields like 'industry', 'country', etc.

    Returns:
        Dictionary with validation results containing:
        - validation: Detailed validation results
        - risk: Overall risk level
        - suggestions_available: Whether suggestions are included

    Raises:
        ValueError: If text is empty or modules list is empty
        KeyError: If invalid module name specified
        Exception: If validation engine encounters an error

    Example:
        >>> validator = DocumentValidator()
        >>> results = validator.validate_document(
        ...     "Your document...",
        ...     "financial",
        ...     ["fca_uk"]
        ... )
        >>> print(results['validation']['overall_risk'])
        'MEDIUM'
    """
```

### Update Documentation

When making changes that affect users:
- Update README.md
- Update relevant guide in docs/
- Update API docs if endpoints change
- Add entry to CHANGELOG.md

---

## Development Tools

### Recommended Tools

```bash
# Code formatting
pip install black
black backend/

# Linting
pip install pylint
pylint backend/

# Type checking
pip install mypy
mypy backend/

# Pre-commit hooks
pip install pre-commit
pre-commit run --all-files

# Testing
pip install pytest pytest-cov pytest-watch
pytest --cov

# API testing
pip install httpie
http POST localhost:8000/api/v1/validate < payload.json
```

### IDE Setup

**VS Code** `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "editor.formatOnSave": true
}
```

---

## Useful Resources

- [Python PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Git Workflow](https://git-scm.com/)

---

## Questions?

- Check existing [issues](https://github.com/Johnobhoy88/loki-interceptor/issues)
- Review [documentation](https://github.com/Johnobhoy88/loki-interceptor/wiki)
- Email: support@highlandai.com

---

**Thank you for contributing!**

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
