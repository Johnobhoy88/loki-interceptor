# Developer Guide

Complete guide for developers contributing to or extending LOKI Interceptor.

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Core Concepts](#core-concepts)
4. [Running Tests](#running-tests)
5. [Adding Features](#adding-features)
6. [Debugging](#debugging)
7. [Performance Optimization](#performance-optimization)

---

## Development Setup

### 1. Clone Repository

```bash
# Fork on GitHub first, then clone
git clone https://github.com/YOUR_USERNAME/loki-interceptor.git
cd loki-interceptor

# Add upstream remote
git remote add upstream https://github.com/Johnobhoy88/loki-interceptor.git
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Configure IDE

**VS Code** - Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

**PyCharm** - Settings:
- Code Style: PEP 8
- Python > Code Style > Inspections: Enable all
- Tools > Python Integrated Tools > pytest

### 4. Verify Setup

```bash
# Check Python version
python --version  # Should be 3.8+

# Check imports
python -c "from backend.core.document_validator import DocumentValidator"

# Check tests
pytest --version
pytest tests/ -v --tb=short
```

---

## Project Structure

### Directory Layout

```
loki-interceptor/
├── backend/                      # Main application
│   ├── api/                      # FastAPI REST endpoints
│   │   ├── main.py              # App entry point
│   │   ├── routes/              # API route handlers
│   │   ├── models/              # Pydantic models
│   │   └── dependencies.py       # Dependency injection
│   ├── core/                     # Core business logic
│   │   ├── document_validator.py # Validation engine
│   │   ├── document_corrector.py # Correction engine
│   │   └── correction_patterns.py # Pattern registry
│   ├── modules/                  # Compliance modules
│   │   ├── fca_uk/
│   │   ├── gdpr_uk/
│   │   ├── tax_uk/
│   │   ├── nda_uk/
│   │   └── hr_scottish/
│   ├── analyzers/                # Universal analyzers
│   ├── db/                       # Database layer
│   ├── gates/                    # Base gate classes
│   └── cli.py                    # CLI interface
├── frontend/                     # Frontend (optional)
├── tests/                        # Test suite
│   ├── semantic/                 # Semantic tests
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── docs/                         # Documentation
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── .env.example                  # Example environment
└── README.md                     # Project README
```

### Key Files

| File | Purpose |
|------|---------|
| `backend/api/main.py` | FastAPI application |
| `backend/core/document_validator.py` | Validation logic |
| `backend/core/document_corrector.py` | Correction logic |
| `tests/semantic/gold_fixtures/` | Test cases |
| `docs/api/README.md` | API documentation |

---

## Core Concepts

### Document Validation Flow

```python
from backend.core.document_validator import DocumentValidator

validator = DocumentValidator()

# Validate document
result = validator.validate_document(
    text="Your document...",
    document_type="financial",
    modules=["fca_uk", "gdpr_uk"]
)

# Result structure
result = {
    'validation': {
        'status': 'FAIL',  # or 'PASS'
        'overall_risk': 'MEDIUM',  # LOW, MEDIUM, HIGH, CRITICAL
        'modules': {
            'fca_uk': {
                'gates_checked': 15,
                'gates_failed': 3,
                'gates': [
                    {
                        'gate_id': 'fair_clear_not_misleading',
                        'passed': False,
                        'severity': 'HIGH',
                        'message': 'Document contains misleading claims',
                        'suggestions': ['Remove unsubstantiated claims']
                    }
                ]
            }
        }
    }
}
```

### Document Correction Flow

```python
from backend.core.document_corrector import DocumentCorrector

corrector = DocumentCorrector(advanced_mode=True)

# Correct document
result = corrector.correct_document(
    text="Original text...",
    validation_results=validation_result,
    document_type="financial"
)

# Result structure
result = {
    'original': 'Original text...',
    'corrected': 'Corrected text...',
    'issues_found': 3,
    'issues_corrected': 2,
    'corrections': [
        {
            'original': 'guaranteed',
            'corrected': 'projected',
            'reason': 'FCA COBS 4.2.1 - Avoid guarantees',
            'strategy': 'regex_replacement',
            'confidence': 0.95
        }
    ]
}
```

### Gate System

Each compliance module contains multiple gates. A gate is a compliance check:

```python
# Example gate structure
gate = {
    'gate_id': 'fair_clear_not_misleading',
    'gate_name': 'Fair, Clear, Not Misleading',
    'passed': False,  # Did it pass?
    'severity': 'HIGH',  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    'message': 'Document contains misleading claims',
    'legal_source': 'COBS 4.2.1',  # Regulatory reference
    'suggestions': [  # Suggestions for fix
        'Remove unsubstantiated performance claims',
        'Add prominent risk warnings'
    ]
}
```

---

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with output
pytest -s

# Run specific file
pytest tests/unit/test_validator.py

# Run specific test
pytest tests/unit/test_validator.py::TestValidator::test_validate_valid_document

# Run tests matching pattern
pytest -k "validation"
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=backend --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Get coverage summary
pytest --cov=backend --cov-report=term-missing
```

### Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Semantic tests
pytest tests/semantic/

# Gold standard tests
pytest tests/semantic/gold_fixtures/

# Slow tests
pytest --slow
```

### Writing Tests

```python
# tests/unit/test_validator.py

import pytest
from backend.core.document_validator import DocumentValidator

class TestDocumentValidator:
    """Tests for DocumentValidator"""

    @pytest.fixture
    def validator(self):
        """Create validator fixture"""
        return DocumentValidator()

    def test_validate_valid_document(self, validator):
        """Test validation of compliant document"""
        text = "Compliant text"
        result = validator.validate_document(text, "financial", ["fca_uk"])
        assert result['validation']['status'] == 'PASS'

    def test_validate_invalid_document(self, validator):
        """Test validation of non-compliant document"""
        text = "Non-compliant text with guaranteed returns"
        result = validator.validate_document(text, "financial", ["fca_uk"])
        assert result['validation']['status'] == 'FAIL'

    def test_validate_empty_text(self, validator):
        """Test validation handles empty text"""
        with pytest.raises(ValueError):
            validator.validate_document("", "financial", [])

    @pytest.mark.parametrize("module", ["fca_uk", "gdpr_uk", "tax_uk"])
    def test_all_modules(self, validator, module):
        """Test validation with all modules"""
        result = validator.validate_document(
            "Test text",
            "financial",
            [module]
        )
        assert 'validation' in result
```

---

## Adding Features

### Adding a New Validation Rule

1. **Create gate class** in `backend/modules/{module}/gates/`:

```python
# backend/modules/fca_uk/gates/my_new_rule.py

class MyNewRuleGate:
    """Check for my new compliance rule"""

    gate_id = "my_new_rule"
    gate_name = "My New Rule"
    severity = "HIGH"
    legal_source = "COBS 1.2.3"

    def check(self, text: str, context: dict) -> dict:
        """
        Check if text complies with rule

        Returns:
            {
                'passed': bool,
                'message': str,
                'suggestions': [str, ...]
            }
        """
        if "violating_phrase" in text.lower():
            return {
                'passed': False,
                'message': 'Document contains violating phrase',
                'suggestions': ['Replace with compliant phrase']
            }

        return {
            'passed': True,
            'message': 'Compliant',
            'suggestions': []
        }
```

2. **Register in module** `backend/modules/fca_uk/__init__.py`:

```python
from .gates.my_new_rule import MyNewRuleGate

GATES = [
    MyNewRuleGate(),
    # ... other gates
]
```

3. **Add correction pattern** in pattern registry:

```python
# backend/core/correction_patterns.py

patterns = {
    "fca_uk": {
        "my_new_rule": {
            "patterns": [
                {
                    "regex": r"violating_phrase",
                    "replacement": "compliant_phrase",
                    "reason": "COBS 1.2.3 compliance"
                }
            ]
        }
    }
}
```

4. **Add tests** in `tests/semantic/test_my_new_rule.py`:

```python
def test_my_new_rule_valid():
    """Test compliant text passes"""
    validator = DocumentValidator()
    result = validator.validate_document(
        "Compliant text",
        "financial",
        ["fca_uk"]
    )
    assert result['validation']['status'] == 'PASS'

def test_my_new_rule_invalid():
    """Test non-compliant text fails"""
    validator = DocumentValidator()
    result = validator.validate_document(
        "Text with violating_phrase",
        "financial",
        ["fca_uk"]
    )
    assert result['validation']['status'] == 'FAIL'
```

### Adding a New Compliance Module

1. **Create module directory**: `backend/modules/my_module/`

2. **Create module structure**:

```
backend/modules/my_module/
├── __init__.py
├── gates/
│   ├── __init__.py
│   └── rule1.py
├── patterns.json
├── config.py
└── rules.py
```

3. **Implement gates** and register them

4. **Add module loader** in `backend/api/main.py`:

```python
# In lifespan function
engine.load_module('my_module')
```

5. **Add tests** for new module

---

## Debugging

### Enable Debug Logging

```bash
# Set log level
LOG_LEVEL=DEBUG python -m backend.api.main

# Save to file
python -m backend.api.main > logs/debug.log 2>&1

# Monitor in real-time
tail -f logs/debug.log
```

### Debug Individual Component

```python
# Debug validator
from backend.core.document_validator import DocumentValidator

validator = DocumentValidator()
text = "Your test text"

# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

result = validator.validate_document(text, "financial", ["fca_uk"])
print(result)
```

### Use Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()

# In debugger commands:
# l - list code
# n - next line
# s - step into
# c - continue
# p variable - print variable
# q - quit
```

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: API",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/api/main.py",
      "console": "integratedTerminal",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile validation
profiler = cProfile.Profile()
profiler.enable()

validator = DocumentValidator()
result = validator.validate_document(text, "financial", ["fca_uk"])

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

### Memory Optimization

```python
# Check memory usage
import tracemalloc

tracemalloc.start()

# Your code here
validator = DocumentValidator()
result = validator.validate_document(text, "financial", ["fca_uk"])

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f}MB")
print(f"Peak: {peak / 1024 / 1024:.1f}MB")
```

### Optimization Tips

1. **Cache patterns**: Pre-compile regex patterns
2. **Reduce gates**: Only load necessary gates
3. **Parallel processing**: Process documents in parallel
4. **Batch operations**: Validate multiple documents together
5. **Memory limits**: Set max cache size

---

## Best Practices

1. **Write tests first** (TDD approach)
2. **Add docstrings** to all functions
3. **Use type hints** for clarity
4. **Keep functions small** and focused
5. **Document changes** in CHANGELOG.md
6. **Run tests before commit**
7. **Follow PEP 8** style guide
8. **Review your own code** first

---

**See also**: [CONTRIBUTING.md](../../CONTRIBUTING.md) | [Architecture](../architecture/README.md) | [Testing](../guides/testing.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
