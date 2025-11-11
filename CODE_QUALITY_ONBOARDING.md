# Code Quality Onboarding Guide

Welcome to the LOKI Interceptor development team! This guide will help you understand and follow our code quality standards.

---

## Quick Start (5 minutes)

### 1. Install Tools

```bash
# Clone the repo
git clone <repo-url>
cd loki-interceptor

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 2. Setup Pre-commit Hooks

```bash
# Install pre-commit framework
pip install pre-commit

# Install git hooks
pre-commit install

# Verify installation
pre-commit run --all-files
```

### 3. Configure Your IDE

#### VS Code
Create `.vscode/settings.json`:
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
  "python.linting.mypyEnabled": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

#### PyCharm
1. Go to Settings → Editor → Code Style
2. Set line length to 100
3. Enable Black formatter: Install → Run on Format Code
4. Configure isort: Go to Tools → Python Integrated Tools

---

## Understanding Our Standards

### Code Style: Black Formatter

**Why Black?**
- Consistent formatting across the project
- No more style debates in code reviews
- Automatic formatting saves time

**Key Rules:**
- Line length: 100 characters
- Indent with 4 spaces
- Strings use double quotes

**Example:**

```python
# Bad (before Black)
def calculate_score(document,config,threshold=0.5,strict=False):
    """Calculate compliance score"""
    score=process(document,config)
    if score>=threshold:return True
    return False

# Good (after Black)
def calculate_score(
    document, config, threshold=0.5, strict=False
) -> bool:
    """Calculate compliance score."""
    score = process(document, config)
    if score >= threshold:
        return True
    return False
```

**Use Black:** `black <file-or-directory>`

### Import Organization: isort

**Why isort?**
- Consistent import ordering
- Prevents merge conflicts
- Works great with Black

**Rules:**
1. Standard library imports
2. Third-party imports
3. Local application imports

**Example:**

```python
# Good import order
import os
import sys
from pathlib import Path
from typing import Dict, List

import click
import pandas as pd
from fastapi import FastAPI

from backend.models import User
from backend.utils import log_error
```

**Use isort:** `isort <file-or-directory>`

### Linting: Flake8

**Why Flake8?**
- Catches bugs and style issues
- Configurable severity levels
- Large plugin ecosystem

**Common Issues to Watch:**

| Issue | Problem | Fix |
|-------|---------|-----|
| F401 | Unused import | Remove it or use it |
| D415 | Missing period in docstring | Add period: `"""Doc string."""` |
| E302 | Need 2 blank lines | Add blank line |
| W293 | Blank line with whitespace | Remove whitespace |

**Check code:** `flake8 backend/`

### Type Hints: mypy

**Why Type Hints?**
- Catches bugs early
- Improves code readability
- Better IDE support

**Example:**

```python
# Without type hints (unclear)
def process_documents(docs, config=None):
    results = []
    for doc in docs:
        results.append(validate(doc, config))
    return results

# With type hints (clear)
from typing import Optional, List

def process_documents(
    docs: List[Document],
    config: Optional[ProcessingConfig] = None
) -> List[ValidationResult]:
    """Process multiple documents and return results."""
    results = []
    for doc in docs:
        results.append(validate(doc, config))
    return results
```

**Check types:** `mypy backend/`

### Docstrings: Google Style

**Why Documentation?**
- Helps others understand your code
- Improves IDE autocomplete
- Makes debugging easier

**Template:**

```python
def validate_compliance(
    document: Document,
    frameworks: List[str],
    strict: bool = False
) -> ValidationResult:
    """Validate document against compliance frameworks.

    Performs comprehensive validation across multiple frameworks
    and returns detailed results.

    Args:
        document: Document to validate
        frameworks: List of framework codes (e.g., ['FCA', 'GDPR'])
        strict: If True, fail on first validation error

    Returns:
        ValidationResult with validation details and scores

    Raises:
        ValueError: If frameworks list is empty
        DocumentError: If document is invalid

    Example:
        >>> doc = load_document("path/to/doc")
        >>> result = validate_compliance(doc, ["FCA", "GDPR"])
        >>> if result.is_valid:
        ...     print("Document is compliant")
    """
```

---

## Your First Commit

### Step 1: Create a Branch

```bash
git checkout -b feature/my-new-feature
```

### Step 2: Write Code

Create or modify Python files following our standards.

### Step 3: Run Pre-commit Checks

```bash
# Auto-format your code
black backend/ tests/
isort backend/ tests/

# Check for issues
flake8 backend/ tests/
mypy backend/

# Or run all checks at once
pre-commit run --all-files
```

### Step 4: Write Tests

```bash
# Create tests in appropriate directory
# tests/my_feature/test_functionality.py

def test_my_feature_works():
    """Test that my feature works correctly."""
    # Arrange
    input_data = prepare_test_data()

    # Act
    result = my_feature(input_data)

    # Assert
    assert result is not None
    assert result.is_valid
```

### Step 5: Run Tests

```bash
# Run specific test
pytest tests/my_feature/test_functionality.py -v

# Run all tests
pytest tests/ backend/tests/ -v

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Step 6: Commit Code

```bash
# Pre-commit hooks run automatically
git add .
git commit -m "feat(module): description of feature"

# Hooks check your code and either pass or fail
# If they fail, fix issues and commit again
```

### Step 7: Push and Create PR

```bash
git push origin feature/my-new-feature

# Create pull request on GitHub
# Code quality checks run automatically
# Address any feedback before merging
```

---

## Code Review Checklist

Before submitting your PR, verify:

- [ ] Code follows Black formatting (`black .`)
- [ ] Imports are organized with isort (`isort .`)
- [ ] Flake8 passes (`flake8 backend/`)
- [ ] Type hints are present (function signatures)
- [ ] Docstrings are complete (all public functions)
- [ ] Tests are written and passing
- [ ] Test coverage hasn't decreased
- [ ] No hardcoded secrets or passwords
- [ ] Commit message follows convention
- [ ] Branch is up to date with main

---

## Common Issues & Solutions

### Issue: Pre-commit hooks fail on commit

**Solution:** Run the hooks manually to fix issues:
```bash
pre-commit run --all-files
# or let them auto-fix:
black .
isort .
```

### Issue: "Line too long" error from flake8

**Solution:** Black will wrap long lines automatically:
```bash
black backend/
```

### Issue: "Missing docstring" error

**Solution:** Add a docstring following Google style:
```python
def my_function():
    """Short description of function.

    Longer explanation if needed.
    """
```

### Issue: "Unused import" error (F401)

**Solution:** Either use the import or remove it:
```python
# Remove if unused
# from typing import Any  # Not used anywhere

# Or use it
from typing import Optional
config: Optional[str] = None
```

### Issue: "Type error" from mypy

**Solution:** Add proper type hints:
```python
# Before
def get_user(user_id):
    return find_user(user_id)

# After
def get_user(user_id: int) -> Optional[User]:
    return find_user(user_id)
```

### Issue: Tests fail locally but pass in CI

**Solution:** Make sure you're using the same Python version:
```bash
python --version  # Should be 3.11+
pip install -r requirements.txt
pytest tests/
```

---

## Tools Explained

### Black Formatter
- **Purpose:** Automatic code formatting
- **Command:** `black backend/`
- **Config:** `pyproject.toml` (line-length = 100)
- **Speed:** Very fast

### isort
- **Purpose:** Organize imports
- **Command:** `isort backend/`
- **Config:** `pyproject.toml` (profile = "black")
- **Speed:** Fast

### Flake8
- **Purpose:** Code style and quality checks
- **Command:** `flake8 backend/`
- **Config:** `.flake8`
- **Plugins:** 6+ plugins enabled
- **Speed:** Medium

### mypy
- **Purpose:** Type checking
- **Command:** `mypy backend/`
- **Config:** `mypy.ini`
- **Speed:** Slower (thorough analysis)

### pytest
- **Purpose:** Unit testing
- **Command:** `pytest tests/ backend/tests/`
- **Config:** `pyproject.toml` [tool.pytest]
- **Speed:** Varies (depends on test count)

### Bandit
- **Purpose:** Security scanning
- **Command:** `bandit -r backend/`
- **Config:** `.bandit`
- **Speed:** Fast

---

## Learning Resources

### Official Documentation
- **Black:** https://black.readthedocs.io/
- **isort:** https://pycqa.github.io/isort/
- **Flake8:** https://flake8.pycqa.org/
- **mypy:** https://mypy.readthedocs.io/
- **pytest:** https://docs.pytest.org/

### Our Documentation
- **Code Standards:** `CODE_STANDARDS.md` - Comprehensive guide
- **Quality Report:** `CODE_QUALITY_REPORT.md` - Current status
- **Technical Debt:** `TECHNICAL_DEBT_TRACKER.md` - Known issues

### Best Practices
- **Google Python Style Guide:** https://google.github.io/styleguide/pyguide.html
- **PEP 8:** https://www.python.org/dev/peps/pep-0008/
- **PEP 257:** https://www.python.org/dev/peps/pep-0257/
- **Real Python:** https://realpython.com/

---

## Getting Help

### Questions?

1. **Check documentation first:**
   - `CODE_STANDARDS.md` - Coding standards
   - `CODE_QUALITY_REPORT.md` - Quality metrics
   - GitHub Discussions - Common questions

2. **Ask in Slack:**
   - #development - General questions
   - #code-review - PR review help
   - @code-quality-team - Direct help

3. **Open an issue:**
   - GitHub Issues for process improvements
   - Include error message and example code

### Getting Code Review Feedback

When reviewers ask for changes:

1. Make the requested changes
2. Run all checks: `pre-commit run --all-files`
3. Commit again: `git commit --amend` or new commit
4. Push: `git push --force-with-lease`
5. Respond to review feedback

---

## Continuous Learning

### Weekly Tips
Join us for:
- **Weekly standup:** Tuesday 10am - Code quality updates
- **Monthly workshop:** Third Thursday - New tool/practice training
- **Ad-hoc Q&A:** Anytime in #development

### Improving Your Skills
- Read other developers' code
- Review PRs from experienced developers
- Attend code review sessions
- Practice writing tests
- Learn one new tool per month

---

## Team Expectations

As part of our development team, we expect:

1. **Code Quality:** All code must pass automated checks
2. **Documentation:** Document your code as you write it
3. **Testing:** Write tests for new features
4. **Review:** Participate in code reviews (both giving and receiving)
5. **Collaboration:** Help teammates improve their code
6. **Continuous Improvement:** Always look for ways to make things better

---

## Success Metrics

You're doing great when:

- ✓ Your commits pass all pre-commit checks
- ✓ Your PRs get approved quickly (1-2 reviews)
- ✓ Your code is covered by tests (75%+ coverage)
- ✓ Teammates compliment your code clarity
- ✓ You're helping others improve their code

---

## Quick Reference

### Commands You'll Use Often

```bash
# Format and fix issues
black .
isort .

# Check code quality
flake8 backend/
mypy backend/

# Run tests
pytest tests/ --cov=backend

# Pre-commit (automatic on commit)
pre-commit run --all-files

# Before committing
git add .
git commit -m "type(scope): message"
```

### File Locations

```
Configuration Files:
  .flake8                 - Linting rules
  .bandit                 - Security rules
  mypy.ini                - Type checking rules
  pyproject.toml          - Tool configurations
  .pre-commit-config.yaml - Pre-commit hooks

Documentation:
  CODE_STANDARDS.md       - Detailed standards
  CODE_QUALITY_REPORT.md  - Quality metrics
  TECHNICAL_DEBT_TRACKER.md - Known issues
```

---

## Feedback

Have suggestions for improving our code quality process?

1. Open an issue with the `enhancement` label
2. Discuss with the code quality team
3. Submit a PR with improvements
4. Share in team meetings

Your feedback makes us better!

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Contact:** code-quality-team@loki.ai

Welcome to the team! Happy coding! 🚀

