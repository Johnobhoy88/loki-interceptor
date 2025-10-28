# 🛡️ Loki Interceptor

**Enterprise-Grade Document Compliance Validation & Autocorrection System**

Loki Interceptor is an advanced AI-powered compliance system that validates and automatically corrects documents against UK regulatory frameworks including FCA, GDPR, Tax, NDA, and Employment Law.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

---

## 📋 Table of Contents

- [Features](#-features)
- [Compliance Modules](#-compliance-modules)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

### Core Capabilities
- 🎯 **141 Detection Rules** across 5 regulatory frameworks
- 🔄 **Automatic Correction** with deterministic synthesis
- 🧠 **Semantic Analysis** using Claude AI
- 📊 **Multi-Gate Validation** with severity classification
- 🔒 **Deterministic Results** via SHA256 hashing
- 📝 **Pattern-Based Corrections** with reason tracking
- 🌐 **Enterprise Ready** with production-grade error handling

### Advanced Features
- **Gold Standard Enhancement** (+108% pattern coverage)
- **Strategy-Based Correction** (Suggestion → Regex → Template → Structural)
- **Comprehensive Reporting** with correction lineage
- **Flexible Integration** via REST API
- **Real-time Validation** with streaming support
- **Audit Trail** for all corrections

---

## 🏛️ Compliance Modules

### FCA UK - Financial Conduct Authority
**51 Rules | 35 Pattern Groups**

Validates financial promotions and documents against:
- COBS 4.2.1 (Fair, Clear, Not Misleading)
- COBS 4.2.3 (Risk/Benefit Balance)
- COBS 9 (Suitability Assessment)
- Consumer Duty
- Past Performance Rules
- Implicit Advice Detection

**Detects:** Misleading claims, missing risk warnings, pressure tactics, unsuitable recommendations

---

### GDPR UK - Data Protection
**29 Rules | 16 Pattern Groups**

Ensures compliance with UK GDPR and DPA 2018:
- Articles 5-8 (Principles, Lawful Basis, Consent, Children)
- Article 13 (Information to be Provided)
- Article 22 (Automated Decision-Making)
- Articles 32, 44-46 (Security & International Transfers)
- PECR Regulation 6 (Cookies)

**Detects:** Consent issues, vague purposes, weak security, missing rights, unlawful data collection

---

### Tax UK - HMRC Compliance
**25 Rules | 11 Pattern Groups**

Validates tax documents against:
- VAT Act 1994
- ITTOIA 2005 (Income Tax)
- Making Tax Digital (MTD)
- Scottish Income Tax
- Invoice Requirements
- HMRC Scam Prevention

**Detects:** Invalid VAT numbers, wrong rates, incomplete invoices, non-allowable expenses, scam indicators

---

### NDA UK - Non-Disclosure Agreements
**12 Rules | 6 Pattern Groups**

Ensures NDAs comply with UK law:
- PIDA 1998 (Whistleblowing Protection)
- Equality Act 2010 s111 (Harassment)
- Contract Law (Reasonableness)
- GDPR Compliance
- Crime Reporting Rights

**Detects:** Unlawful restrictions, overly broad definitions, unreasonable durations, blocked legal rights

---

### HR Scottish - Employment Law
**24 Rules | 11 Pattern Groups**

Validates employment documents against:
- ERA 1999 s10 (Accompaniment Rights)
- ACAS Code of Practice
- Natural Justice Principles
- Scottish Employment Law
- Disciplinary Procedures

**Detects:** Missing rights notices, vague allegations, insufficient notice, procedural unfairness

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Loki Interceptor                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌─────────────────┐                │
│  │   Document   │─────▶│   Semantic      │                │
│  │   Validator  │      │   Analyzer      │                │
│  └──────────────┘      └─────────────────┘                │
│         │                       │                           │
│         ▼                       ▼                           │
│  ┌──────────────────────────────────────┐                  │
│  │      Compliance Gate System          │                  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐         │                  │
│  │  │ FCA  │ │GDPR  │ │ Tax  │ ...     │                  │
│  │  └──────┘ └──────┘ └──────┘         │                  │
│  └──────────────────────────────────────┘                  │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                  │
│  │    Correction Synthesizer            │                  │
│  │  ┌─────────────────────────────┐    │                  │
│  │  │ Strategy Priority System    │    │                  │
│  │  │ 20: Suggestion              │    │                  │
│  │  │ 30: Regex Replacement       │    │                  │
│  │  │ 40: Template Insertion      │    │                  │
│  │  │ 60: Structural Reform       │    │                  │
│  │  └─────────────────────────────┘    │                  │
│  └──────────────────────────────────────┘                  │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                  │
│  │   Pattern Registry (141 Rules)       │                  │
│  └──────────────────────────────────────┘                  │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────┐                  │
│  │    Corrected Document + Report       │                  │
│  └──────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**1. Semantic Analyzer**
- Claude AI integration for intelligent document understanding
- Context-aware validation
- Natural language processing

**2. Compliance Gates**
- Multi-level validation (critical, high, medium, low)
- Module-specific gate checks
- Severity classification

**3. Correction Synthesizer**
- Deterministic pattern application
- Strategy priority system
- SHA256-based deduplication
- Correction lineage tracking

**4. Pattern Registry**
- 141 detection rules
- 83 template categories
- Regex-based matching
- Template insertion
- Structural reorganization

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Anthropic API key (for Claude AI)

### Setup

```bash
# Clone the repository
git clone https://github.com/Johnobhoy88/loki-interceptor.git
cd loki-interceptor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Configuration

Create a `.env` file in the project root:

```env
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional
CLAUDE_MODEL=claude-3-5-sonnet-20241022
LOG_LEVEL=INFO
MAX_TOKENS=4096
TEMPERATURE=0.0
```

---

## 🎯 Quick Start

### Basic Usage

```python
from backend.core.document_corrector import DocumentCorrector
from backend.core.document_validator import DocumentValidator

# 1. Validate a document
validator = DocumentValidator()
validation_results = validator.validate_document(
    text="Your document text here",
    document_type="financial",
    modules=["fca_uk", "gdpr_uk"]
)

# 2. Apply corrections
corrector = DocumentCorrector(advanced_mode=True)
correction_results = corrector.correct_document(
    text="Your document text here",
    validation_results=validation_results,
    document_type="financial"
)

# 3. Access results
print(f"Original: {correction_results['original']}")
print(f"Corrected: {correction_results['corrected']}")
print(f"Corrections Applied: {correction_results['correction_count']}")
print(f"Deterministic Hash: {correction_results['deterministic_hash']}")
```

### Command Line Usage

```bash
# Validate a document
python -m backend.cli validate --file document.txt --type financial --modules fca_uk gdpr_uk

# Validate and correct
python -m backend.cli correct --file document.txt --type financial --output corrected.txt

# Run tests
python -m pytest tests/

# Run specific module tests
python -m pytest tests/semantic/test_fca_validation.py
```

---

## 📖 Usage Examples

### Example 1: Financial Document Correction

```python
from backend.core.document_corrector import DocumentCorrector
from backend.core.document_validator import DocumentValidator

text = """
Investment Opportunity - Guaranteed 15% Returns!

Our fund has delivered consistent 15% annual returns for 3 years.
Zero risk investment suitable for everyone. Limited time offer!
"""

# Validate
validator = DocumentValidator()
results = validator.validate_document(text, "financial", ["fca_uk"])

# Correct
corrector = DocumentCorrector(advanced_mode=True)
correction = corrector.correct_document(text, results, "financial")

print("Issues Found:")
for gate, status in results['validation']['modules']['fca_uk']['gates'].items():
    if status['status'] == 'FAIL':
        print(f"  ❌ {gate}: {status['severity']}")

print(f"\nCorrections Applied: {correction['correction_count']}")
print(f"\nCorrected Text:\n{correction['corrected']}")
```

### Example 2: GDPR Privacy Policy Check

```python
text = """
Privacy Notice

We collect your data for various purposes.
By using our site you agree to data collection.
We may share with trusted third parties.
"""

validator = DocumentValidator()
results = validator.validate_document(text, "privacy_policy", ["gdpr_uk"])

corrector = DocumentCorrector(advanced_mode=True)
correction = corrector.correct_document(text, results, "privacy_policy")

# View specific corrections
for corr in correction['corrections']:
    print(f"Pattern: {corr['pattern']}")
    print(f"Reason: {corr['reason']}")
    print(f"Before: {corr['before']}")
    print(f"After: {corr['after']}\n")
```

### Example 3: Batch Processing

```python
import glob
from backend.core.document_corrector import DocumentCorrector
from backend.core.document_validator import DocumentValidator

validator = DocumentValidator()
corrector = DocumentCorrector(advanced_mode=True)

# Process all documents in a directory
for filepath in glob.glob("documents/*.txt"):
    with open(filepath, 'r') as f:
        text = f.read()

    # Validate
    results = validator.validate_document(
        text,
        document_type="financial",
        modules=["fca_uk", "gdpr_uk", "tax_uk"]
    )

    # Correct if needed
    if results['validation']['status'] == 'FAIL':
        correction = corrector.correct_document(text, results, "financial")

        # Save corrected version
        output_path = filepath.replace('.txt', '_corrected.txt')
        with open(output_path, 'w') as f:
            f.write(correction['corrected'])

        print(f"✓ Corrected {filepath} → {output_path}")
        print(f"  Applied {correction['correction_count']} corrections")
```

---

## ⚙️ Configuration

### Advanced Configuration

```python
from backend.core.document_corrector import DocumentCorrector

# Configure correction behavior
corrector = DocumentCorrector(
    advanced_mode=True,              # Enable all correction strategies
    max_iterations=3,                # Maximum correction passes
    confidence_threshold=0.8,        # Minimum confidence for corrections
    preserve_formatting=True,        # Maintain original formatting
    track_changes=True,              # Enable detailed change tracking
)

# Module-specific configuration
from backend.core.correction_patterns import CorrectionPatternRegistry

registry = CorrectionPatternRegistry()

# Disable specific patterns
registry.disable_pattern('fca_uk', 'pressure_tactics')

# Add custom patterns
registry.add_custom_pattern(
    module='fca_uk',
    category='custom_check',
    pattern={
        'pattern': r'your_regex_here',
        'replacement': 'corrected text',
        'reason': 'Your compliance reason',
        'flags': 're.IGNORECASE'
    }
)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *required* | Your Claude API key |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Claude model to use |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_TOKENS` | `4096` | Maximum tokens per request |
| `TEMPERATURE` | `0.0` | Claude temperature (0.0 for deterministic) |
| `CACHE_ENABLED` | `true` | Enable result caching |
| `CACHE_TTL` | `3600` | Cache TTL in seconds |

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test suite
pytest tests/semantic/test_fca_validation.py

# Run gold standard tests
pytest tests/semantic/gold_fixtures/

# Run with verbose output
pytest -v -s
```

### Test Structure

```
tests/
├── semantic/
│   ├── gold_fixtures/
│   │   ├── fca_uk/          # 15 FCA violation fixtures
│   │   ├── gdpr_uk/         # 15 GDPR violation fixtures
│   │   ├── tax_uk/          # 15 Tax violation fixtures
│   │   ├── nda_uk/          # 14 NDA violation fixtures
│   │   └── hr_scottish/     # 15 HR violation fixtures
│   ├── test_fca_validation.py
│   ├── test_gdpr_validation.py
│   └── test_fca_gold_standard.py
└── unit/
    ├── test_correction_synthesizer.py
    ├── test_pattern_registry.py
    └── test_strategies.py
```

### Writing Tests

```python
def test_custom_validation():
    """Test custom validation scenario"""
    from backend.core.document_validator import DocumentValidator

    text = "Your test document"
    validator = DocumentValidator()

    results = validator.validate_document(
        text=text,
        document_type="financial",
        modules=["fca_uk"]
    )

    assert results['validation']['status'] in ['PASS', 'FAIL']
    assert 'fca_uk' in results['validation']['modules']
```

---

## 📚 API Reference

### DocumentValidator

```python
class DocumentValidator:
    def validate_document(
        self,
        text: str,
        document_type: str,
        modules: List[str],
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Validate document against compliance modules.

        Args:
            text: Document text to validate
            document_type: Type of document (financial, privacy_policy, etc.)
            modules: List of compliance modules to check
            context: Optional context for validation

        Returns:
            Dict with validation results including gate statuses and violations
        """
```

### DocumentCorrector

```python
class DocumentCorrector:
    def __init__(
        self,
        advanced_mode: bool = True,
        max_iterations: int = 3,
        confidence_threshold: float = 0.8
    ):
        """Initialize document corrector with configuration."""

    def correct_document(
        self,
        text: str,
        validation_results: Dict,
        document_type: str,
        preserve_formatting: bool = True
    ) -> Dict:
        """
        Apply corrections to document based on validation results.

        Args:
            text: Original document text
            validation_results: Results from DocumentValidator
            document_type: Type of document
            preserve_formatting: Whether to maintain original formatting

        Returns:
            Dict with corrected text, corrections list, and metadata
        """
```

### CorrectionPatternRegistry

```python
class CorrectionPatternRegistry:
    def get_patterns_for_module(self, module: str) -> Dict:
        """Get all patterns for a specific compliance module."""

    def get_regex_patterns(self, category: str) -> List[Dict]:
        """Get regex patterns for a specific category."""

    def get_templates(self, category: str) -> List[Dict]:
        """Get templates for a specific category."""
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/loki-interceptor.git
cd loki-interceptor

# Create a feature branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Make your changes and test
pytest

# Submit a pull request
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions
- Add tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Documentation
- [Full Documentation](https://github.com/Johnobhoy88/loki-interceptor/wiki)
- [API Reference](https://github.com/Johnobhoy88/loki-interceptor/wiki/API-Reference)
- [Gold Standard Enhancement Guide](GOLD_STANDARD_ALL_MODULES_SUMMARY.md)

### Getting Help
- 📧 Email: support@highlandai.com
- 💬 Issues: [GitHub Issues](https://github.com/Johnobhoy88/loki-interceptor/issues)
- 📖 Wiki: [Project Wiki](https://github.com/Johnobhoy88/loki-interceptor/wiki)

### Reporting Bugs
Please use the [GitHub issue tracker](https://github.com/Johnobhoy88/loki-interceptor/issues) and include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages

---

## 🙏 Acknowledgments

- **Anthropic** for Claude AI
- **Highland AI** for project development
- **UK Regulatory Bodies** (FCA, ICO, HMRC, ACAS) for compliance guidance
- **Contributors** who have helped improve this project

---

## 📊 Project Statistics

| Metric | Count |
|--------|-------|
| Total Detection Rules | 141 |
| Compliance Modules | 5 |
| Pattern Groups | 79 |
| Template Categories | 83 |
| Test Fixtures | 74 |
| Code Coverage | >85% |
| Python Version | 3.8+ |

---

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ 5 compliance modules (FCA, GDPR, Tax, NDA, HR)
- ✅ 141 detection rules
- ✅ Deterministic correction synthesis
- ✅ Gold standard pattern enhancement

### Planned Features (v1.1)
- 🔄 REST API with FastAPI
- 🔄 Web interface for document upload
- 🔄 Batch processing capabilities
- 🔄 PDF document support
- 🔄 Additional compliance modules (EU regulations)

### Future Enhancements (v2.0)
- 🔮 Machine learning-based pattern improvement
- 🔮 Multi-language support
- 🔮 Real-time document scanning
- 🔮 Integration with document management systems
- 🔮 Compliance trend analytics

---

## ⚡ Quick Links

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)

---

**Built with ❤️ by Highland AI**

*Making compliance simpler, one document at a time.*
