# LOKI Interceptor Architecture

System design and technical architecture of LOKI Interceptor.

## Overview

LOKI Interceptor is a layered architecture system composed of:
1. **API Layer** - FastAPI REST endpoints
2. **Validation Engine** - Core compliance checking
3. **Correction Engine** - Pattern-based fixes
4. **Compliance Modules** - Framework-specific rules
5. **Pattern Registry** - Detection and correction patterns

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REST API Layer                           │
│  (FastAPI endpoints, validation, correction, history)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Validation Orchestration                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Document Input → Universal Analyzers → Gate Engine │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Compliance Modules (5)                         │
│  ┌──────────┬──────────┬─────────┬────────┬────────────┐   │
│  │  FCA UK  │ GDPR UK  │ Tax UK  │ NDA UK │ HR Scottish│   │
│  └──────┬───┴──────┬───┴────┬────┴─────┬──┴──────┬─────┘   │
│         │ Gates    │ Gates  │ Gates    │ Gates   │ Gates   │
│         └──────────┴────────┴──────────┴─────────┴─────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Correction Engine                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Strategy Priority System                            │   │
│  │  1. Suggestion (20)    2. Regex (30)                │   │
│  │  3. Template (40)      4. Structural (60)           │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            Pattern Registry                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  141 Detection Rules | 83 Template Categories       │   │
│  │  Regex Patterns | Template Insertions | Replacements│   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. REST API Layer (FastAPI)

**Location**: `backend/api/`

**Endpoints**:
- `/api/v1/validate` - Document validation
- `/api/v1/correct` - Document correction
- `/api/v1/modules` - Module information
- `/api/v1/history` - Validation/correction history
- `/api/v1/stats` - System statistics
- `/api/v1/ws/validate` - WebSocket validation

**Features**:
- OpenAPI/Swagger documentation
- Request validation with Pydantic
- Rate limiting by IP
- Response caching
- Error handling & logging

### 2. Validation Engine

**Location**: `backend/core/document_validator.py`

**Process**:
1. Accept document and module list
2. Run universal analyzers (PII, contradictions, etc.)
3. For each module:
   - Load compliance module
   - Execute gates in sequence
   - Collect failures and severity
4. Calculate overall risk level
5. Return detailed results

**Key Methods**:
- `validate_document()` - Main validation
- `run_universal_analyzers()` - Generic analysis
- `execute_module_gates()` - Module-specific checks

### 3. Compliance Modules

**Location**: `backend/modules/`

Each module (`fca_uk/`, `gdpr_uk/`, etc.) contains:
- **Gates** - Individual compliance checks
- **Patterns** - Detection patterns
- **Rules** - Business logic
- **Legal references** - Regulation citations

**Module Structure**:
```
backend/modules/fca_uk/
├── gates/
│   ├── fair_clear_not_misleading.py
│   ├── risk_benefit_balance.py
│   └── ... (more gates)
├── patterns/
│   └── patterns.json
├── config.py
└── rules.py
```

### 4. Correction Engine

**Location**: `backend/core/document_corrector.py`

**Process**:
1. Accept validation results
2. Load pattern registry
3. For each issue:
   - Try Suggestion (priority 20)
   - If no match, try Regex (priority 30)
   - If no match, try Template (priority 40)
   - If no match, try Structural (priority 60)
4. Deduplicate corrections (SHA256)
5. Calculate confidence scores
6. Return corrected text + audit trail

**Strategies**:
- **Suggestion (20)**: Recommendations only
- **Regex (30)**: Text replacements
- **Template (40)**: Standard text insertion
- **Structural (60)**: Content reorganization

### 5. Pattern Registry

**Location**: `backend/core/correction_patterns.py`

**Contains**:
- 141 detection rules
- 83 template categories
- Regex patterns for each rule
- Template text for each category
- Confidence scoring rules

**Pattern Format**:
```json
{
  "fca_uk": {
    "fair_clear_not_misleading": {
      "patterns": [
        {"regex": "guaranteed", "replacement": "projected"}
      ],
      "templates": [
        {"context": "risk_warning", "text": "..."}
      ],
      "confidence": 0.95
    }
  }
}
```

---

## Data Flow

### Validation Flow

```
Request
  ↓
Parse & Validate Input
  ↓
Check Cache
  ↓ (Cache Miss)
Initialize Validation Engine
  ↓
Universal Analyzers
  ├─ PII Detection
  ├─ Contradiction Analysis
  └─ Context Extraction
  ↓
Load Compliance Modules
  ↓
Execute Gates
  ├─ FCA Gates (51 rules)
  ├─ GDPR Gates (29 rules)
  ├─ Tax Gates (25 rules)
  ├─ NDA Gates (12 rules)
  └─ HR Gates (24 rules)
  ↓
Calculate Risk Levels
  ├─ Per Module
  └─ Overall
  ↓
Format Results
  ↓
Cache Results
  ↓
Return Response
```

### Correction Flow

```
Request (with validation results)
  ↓
Load Pattern Registry
  ↓
Load Correction Strategies
  ↓
For Each Validation Issue:
  ├─ Priority 20: Check Suggestions
  ├─ Priority 30: Apply Regex
  ├─ Priority 40: Insert Templates
  └─ Priority 60: Structural Changes
  ↓
Deduplicate (SHA256)
  ↓
Calculate Confidence Scores
  ↓
Apply Corrections
  ├─ High Confidence (>0.85)
  ├─ Medium Confidence (0.60-0.85)
  └─ Low Confidence (<0.60)
  ↓
Format Results
  ↓
Return Response
```

---

## Key Classes & Interfaces

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
        """Validate document against modules"""
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
        """Initialize corrector"""

    def correct_document(
        self,
        text: str,
        validation_results: Dict,
        document_type: str,
        preserve_formatting: bool = True
    ) -> Dict:
        """Apply corrections to document"""
```

### CorrectionPatternRegistry

```python
class CorrectionPatternRegistry:
    def get_patterns_for_module(self, module: str) -> Dict:
        """Get all patterns for module"""

    def get_regex_patterns(self, category: str) -> List[Dict]:
        """Get regex patterns for category"""

    def get_templates(self, category: str) -> List[Dict]:
        """Get templates for category"""

    def add_custom_pattern(
        self,
        module: str,
        category: str,
        pattern: Dict
    ) -> None:
        """Add custom correction pattern"""
```

---

## Module Execution

Each compliance module follows a gate-based architecture:

### Gate System

Each gate is a compliance check:
- **Input**: Document text
- **Process**: Rule evaluation
- **Output**: Pass/Fail + severity
- **Metadata**: Legal reference, suggestions

### Gate Execution Order

```
1. Load module gates
2. For each gate:
   - Run validation logic
   - Check for violations
   - Assign severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
   - Collect suggestions
3. Aggregate results
4. Calculate module risk
```

### Gate Severity Levels

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Legal violation - must fix |
| **HIGH** | Significant compliance issue |
| **MEDIUM** | Moderate issue - review |
| **LOW** | Minor issue - optional |
| **INFO** | Informational - note only |

---

## Performance Considerations

### Caching Strategy

```python
Cache Key = SHA256(text + document_type + modules)

# Cache hit: <100ms
# Cache miss: 1-5 seconds
```

### Optimization Techniques

1. **Lazy Loading**: Modules loaded on-demand
2. **Pattern Compilation**: Regex patterns pre-compiled
3. **Deduplication**: SHA256-based correction dedup
4. **Batch Processing**: Up to 10 docs per request
5. **Streaming**: WebSocket for real-time results

### Scalability

| Scale | Approach |
|-------|----------|
| Single server | Gunicorn + Nginx |
| Multiple servers | Load balancer |
| High throughput | Kubernetes + cache |

---

## Error Handling

### Validation Errors

```python
# Input validation
if not text or len(text) < 10:
    raise ValueError("Text too short")

# Module not found
if module not in available_modules:
    raise ValueError(f"Module {module} not found")

# API errors
if response.status != 200:
    raise HTTPException(status_code=500)
```

### Correction Errors

```python
# Pattern matching error
try:
    match = regex_pattern.search(text)
except re.error as e:
    logger.error(f"Regex error: {e}")

# Confidence calculation error
if confidence < 0 or confidence > 1:
    confidence = 0.0
```

---

## Testing Architecture

### Test Structure

```
tests/
├── semantic/
│   ├── gold_fixtures/
│   │   ├── fca_uk/          # 15 test cases
│   │   ├── gdpr_uk/         # 15 test cases
│   │   └── ... (more modules)
│   ├── test_fca_validation.py
│   └── test_fca_gold_standard.py
└── unit/
    ├── test_validator.py
    ├── test_corrector.py
    └── test_patterns.py
```

### Test Coverage

- Unit tests: Core functionality
- Integration tests: Module interactions
- Semantic tests: Pattern accuracy
- Gold standard tests: Rule validation

---

## Security Architecture

### Input Validation

- Text length limits
- Character encoding validation
- Malicious pattern detection

### API Security

- Rate limiting (100 req/min per IP)
- CORS configuration
- Error message sanitization
- No sensitive data in logs

### Data Protection

- No text persistence (unless configured)
- Secure API key handling
- Audit trail encryption (planned)

---

## Deployment Topology

### Development

```
Developer Machine
└─ Python process
   └─ Backend modules
   └─ API endpoints
```

### Production

```
Load Balancer (nginx)
├─ API Server 1 (Gunicorn + 4 workers)
├─ API Server 2
└─ API Server 3

Cache Layer (Redis - optional)
Database Layer (PostgreSQL - planned)
```

---

## Future Architecture Enhancements

### Planned Improvements

1. **Microservices**: Separate services per module
2. **Message Queue**: Async job processing
3. **Caching Layer**: Redis for distributed cache
4. **Database**: Store validation history
5. **ML Pipeline**: Pattern improvement via ML

---

**See also**: [Code Structure](code-structure.md) | [API Reference](../api/README.md)

**Version**: 1.0.0
**Last Updated**: 2025-11-11
