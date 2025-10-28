---
name: loki-architecture
description: Expert in LOKI system architecture, components, data flow, API structure, frontend-backend integration, and overall system design
---

# LOKI Architecture Skill

You are an expert in the LOKI compliance checking system architecture. This skill provides comprehensive knowledge of system design, components, data flow, API structure, and integration patterns.

## System Overview

LOKI is a **full-stack compliance validation and correction system** with:

- **Architecture:** Next.js full-stack application
- **Frontend:** React with Next.js 14 App Router
- **Backend:** Python validation engine + Next.js API routes
- **Deployment:** Vercel (serverless)
- **Database:** None (stateless validation)
- **AI/ML:** None (fully rule-based)

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Next.js 14 Frontend)                        │
│  - Document input                                               │
│  - Validation results display                                   │
│  - Correction preview                                           │
│  - Compliance reports                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/JSON
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      API LAYER                                  │
│                (Next.js API Routes)                             │
│  - POST /api/validate                                           │
│  - POST /api/correct                                            │
│  - GET  /api/health                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Python Bridge
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   VALIDATION ENGINE                             │
│                   (Python Backend)                              │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Gate Loader  │  │   Engine     │  │  Corrector   │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         │                  │                  │                 │
│  ┌──────▼──────────────────▼──────────────────▼───────┐        │
│  │           MODULE REGISTRY                           │        │
│  │  - FCA UK    - GDPR UK    - Tax UK                 │        │
│  │  - NDA UK    - HR Scottish                         │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │         CORRECTION SYSTEM ✅ PRODUCTION READY      │        │
│  │  - Pattern Registry (107 patterns)                 │        │
│  │    • FCA UK: 23 | GDPR UK: 31 | Tax UK: 18        │        │
│  │    • NDA UK: 15 | HR Scottish: 20                  │        │
│  │  - 4 Correction Strategies                         │        │
│  │  - Deterministic Synthesizer                       │        │
│  │  - Validation Layer                                │        │
│  │  - Performance: 5.15M chars/sec (515x threshold)   │        │
│  │  - Test Status: 11/11 PASSED (100%)                │        │
│  └─────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Components

**Location:** `frontend/src/`

```
frontend/src/
├── app/
│   ├── page.js              # Main page
│   ├── layout.js            # Root layout
│   ├── globals.css          # Global styles
│   └── api/                 # API routes
│       ├── validate/
│       │   └── route.js     # Validation endpoint
│       ├── correct/
│       │   └── route.js     # Correction endpoint
│       └── health/
│           └── route.js     # Health check
├── components/
│   ├── ValidationForm.jsx   # Document input form
│   ├── ResultsDisplay.jsx   # Validation results
│   ├── CorrectionView.jsx   # Correction preview
│   └── GateStatus.jsx       # Gate status display
└── lib/
    ├── api.js               # API client
    └── utils.js             # Utility functions
```

**Key Components:**

1. **ValidationForm** - Main user input
   - Document text input
   - Document type selector
   - Submit button
   - Loading states

2. **ResultsDisplay** - Show validation results
   - Overall status badge
   - Module breakdowns
   - Gate results
   - Violation highlighting

3. **CorrectionView** - Preview corrections
   - Before/after comparison
   - Correction details
   - Apply corrections button

### Backend Components

**Location:** `backend/`

```
backend/
├── core/
│   ├── engine.py                      # Main validation engine
│   ├── gate_loader.py                 # Gate discovery and loading
│   ├── corrector.py                   # Document corrector
│   ├── correction_strategies.py       # Correction strategies (4 strategies)
│   ├── correction_patterns.py         # Pattern registry (107 patterns)
│   ├── correction_synthesizer.py      # Synthesis engine
│   ├── test_advanced_corrector.py     # Baseline tests (8 tests)
│   ├── test_enhanced_corrections.py   # Module tests (6 tests)
│   ├── comprehensive_test_runner.py   # Production tests (11 tests)
│   └── CORRECTOR_README.md            # Correction system docs
├── modules/
│   ├── fca_uk/
│   │   ├── module.py                # FCA module definition
│   │   └── gates/                   # 26 FCA gates
│   ├── gdpr_uk/
│   │   ├── module.py                # GDPR module definition
│   │   └── gates/                   # 22 GDPR gates
│   ├── tax_uk/
│   │   ├── module.py                # Tax module definition
│   │   └── gates/                   # Tax gates
│   ├── nda_uk/
│   │   ├── module.py                # NDA module definition
│   │   └── gates/                   # NDA gates
│   └── hr_scottish/
│       ├── module.py                # HR module definition
│       └── gates/                   # 24 HR gates
├── api/
│   └── routes.py                    # API route handlers (local dev)
└── server.js                        # Express server (local dev)
```

**Key Components:**

1. **ValidationEngine** (`core/engine.py`)
   - Orchestrates validation
   - Loads modules
   - Runs gates
   - Aggregates results

2. **GateLoader** (`core/gate_loader.py`)
   - Discovers modules
   - Loads gate classes
   - Validates gate structure

3. **DocumentCorrector** (`core/corrector.py`)
   - Main correction interface
   - Strategy orchestration
   - Pattern management

## Data Flow

### Validation Flow

```
1. User Input
   ↓
   [Frontend: ValidationForm]
   - Document text
   - Document type

2. API Request
   ↓
   POST /api/validate
   {
     "text": "...",
     "document_type": "financial"
   }

3. API Route Handler
   ↓
   [Next.js API Route]
   - Parse request
   - Call Python engine

4. Validation Engine
   ↓
   [Python: ValidationEngine]
   - Load modules
   - Execute gates
   - Aggregate results

5. Module Processing
   ↓
   [Each Module]
   - Check relevance
   - Run gates
   - Collect results

6. Gate Execution
   ↓
   [Each Gate]
   - Check if relevant
   - Analyze document
   - Return status

7. Result Aggregation
   ↓
   [Engine]
   - Combine module results
   - Calculate overall status
   - Format response

8. API Response
   ↓
   {
     "validation": {
       "overall_status": "FAIL",
       "modules": {...}
     }
   }

9. Display Results
   ↓
   [Frontend: ResultsDisplay]
   - Show status
   - Display violations
   - Offer corrections
```

### Correction Flow

```
1. User Action
   ↓
   [Frontend: Click "Auto-correct"]

2. API Request
   ↓
   POST /api/correct
   {
     "text": "...",
     "validation_results": {...},
     "advanced_options": {...}
   }

3. Document Corrector
   ↓
   [Python: DocumentCorrector]
   - Extract failing gates
   - Initialize synthesizer

4. Pattern Matching
   ↓
   [Pattern Registry]
   - Load patterns for gates
   - Register with strategies

5. Strategy Execution
   ↓
   [Strategies (priority order)]
   - SuggestionExtraction (20)
   - RegexReplacement (30)
   - TemplateInsertion (40)
   - StructuralReorganization (60)

6. Synthesis
   ↓
   [Synthesizer]
   - Apply strategies
   - Track corrections
   - Calculate hashes

7. Validation
   ↓
   [CorrectionValidator]
   - Check integrity
   - Verify structure
   - Detect issues

8. API Response
   ↓
   {
     "original": "...",
     "corrected": "...",
     "corrections_applied": [...],
     "determinism": {...}
   }

9. Display Corrections
   ↓
   [Frontend: CorrectionView]
   - Show before/after
   - List corrections
   - Allow apply/reject
```

## API Specification

### Endpoints

#### 1. POST /api/validate

**Purpose:** Validate document compliance

**Request:**
```typescript
interface ValidateRequest {
  text: string;                    // Document text
  document_type?: string;          // Optional: 'financial' | 'privacy' | 'tax' | 'nda' | 'employment'
}
```

**Response:**
```typescript
interface ValidateResponse {
  validation: {
    overall_status: 'PASS' | 'FAIL' | 'WARNING';
    overall_severity: 'critical' | 'high' | 'medium' | 'low' | 'none';
    timestamp: string;
    modules: {
      [moduleId: string]: {
        status: 'PASS' | 'FAIL' | 'WARNING' | 'N/A';
        gates: {
          [gateId: string]: {
            status: 'PASS' | 'FAIL' | 'WARNING' | 'N/A';
            severity: 'critical' | 'high' | 'medium' | 'low' | 'none';
            message: string;
            legal_source?: string;
            suggestion?: string;
            penalty?: string;
            spans?: Array<{
              type: string;
              start: number;
              end: number;
              text: string;
              severity: string;
            }>;
            details?: string[];
          }
        }
      }
    }
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Investment with guaranteed returns!",
    "document_type": "financial"
  }'
```

#### 2. POST /api/correct

**Purpose:** Correct document compliance issues

**Request:**
```typescript
interface CorrectRequest {
  text: string;
  validation_results: ValidateResponse;
  document_type?: string;
  advanced_options?: {
    multi_level?: boolean;
    context_aware?: boolean;
    document_metadata?: {
      document_type: string;
      module_id?: string;
      confidence?: number;
      industry?: string;
      jurisdiction?: string;
    }
  }
}
```

**Response:**
```typescript
interface CorrectResponse {
  original: string;
  corrected: string;
  corrections_applied: Array<{
    gate_id: string;
    gate_severity: string;
    strategy: string;
    metadata: {
      strategy: string;
      changes: number;
      locations: number[];
      reason: string;
      examples: string[];
    };
    text_length_delta: number;
  }>;
  unchanged: boolean;
  correction_count: number;
  strategies_applied: string[];
  determinism: {
    input_hash: string;
    output_hash: string;
    repeatable: boolean;
  };
  validation: {
    valid: boolean;
    warnings: string[];
    errors: string[];
  };
  mode: 'advanced' | 'legacy';
  multi_level?: boolean;
  context_aware?: boolean;
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/correct \
  -H "Content-Type: application/json" \
  -d '{
    "text": "VAT threshold is £85,000",
    "validation_results": {...},
    "advanced_options": {
      "multi_level": true
    }
  }'
```

#### 3. GET /api/health

**Purpose:** Health check

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-25T12:00:00Z"
}
```

## Module System

### Module Structure

**Module Definition Pattern:**

```python
# backend/modules/{module_id}/module.py

def get_gates():
    """Return list of gate instances for this module"""
    from .gates.gate1 import Gate1
    from .gates.gate2 import Gate2

    return [
        Gate1(),
        Gate2(),
        # ... more gates
    ]

# Module metadata
MODULE_ID = "fca_uk"
MODULE_NAME = "FCA UK - Financial Conduct Authority"
MODULE_DESCRIPTION = "UK financial services regulation compliance"
```

### Module Registry

**Location:** `backend/core/gate_loader.py`

**Loading Process:**
```python
1. Scan backend/modules/ directory
2. Find module.py files
3. Import get_gates() function
4. Instantiate gate classes
5. Register in engine
```

**Module Discovery:**
```python
def discover_modules():
    modules = {}
    modules_dir = Path(__file__).parent.parent / 'modules'

    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and (module_dir / 'module.py').exists():
            module_id = module_dir.name
            module = import_module(f'backend.modules.{module_id}.module')
            modules[module_id] = {
                'gates': module.get_gates(),
                'name': getattr(module, 'MODULE_NAME', module_id),
                'description': getattr(module, 'MODULE_DESCRIPTION', '')
            }

    return modules
```

### Gate Interface

**Required Methods:**

```python
class Gate:
    def __init__(self):
        self.name = "gate_identifier"        # Required
        self.severity = "critical"           # Required
        self.legal_source = "Reference"      # Optional but recommended

    def _is_relevant(self, text: str) -> bool:
        """Optional but recommended - check if gate applies"""
        pass

    def check(self, text: str, document_type: str) -> dict:
        """Required - perform compliance check"""
        return {
            'status': 'PASS' | 'FAIL' | 'WARNING' | 'N/A',
            'severity': 'critical' | 'high' | 'medium' | 'low' | 'none',
            'message': 'Description',
            'legal_source': 'Legal reference',
            'suggestion': 'How to fix (optional)',
            'spans': [...],  # Optional
            'details': [...],  # Optional
            'penalty': 'Penalty info (optional)'
        }
```

## State Management

### Frontend State

**Component State:**
- Managed with React hooks (`useState`, `useEffect`)
- Local to components
- No global state management (Redux/Context not needed)

**Example:**
```javascript
function ValidationForm() {
  const [text, setText] = useState('');
  const [documentType, setDocumentType] = useState('financial');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    const response = await fetch('/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, document_type: documentType })
    });
    const data = await response.json();
    setResults(data);
    setLoading(false);
  };

  return (
    // ... JSX
  );
}
```

### Backend State

**Stateless Design:**
- No session storage
- No database
- Each request is independent
- Results not persisted

**Benefits:**
- Scales horizontally
- No state synchronization
- Simple deployment
- Fast failover

## Error Handling

### Frontend Error Handling

```javascript
async function validateDocument(text, documentType) {
  try {
    const response = await fetch('/api/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, document_type: documentType })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();

  } catch (error) {
    console.error('Validation error:', error);
    return {
      error: error.message,
      validation: {
        overall_status: 'ERROR',
        message: 'Failed to validate document'
      }
    };
  }
}
```

### Backend Error Handling

**API Route:**
```javascript
export async function POST(request) {
  try {
    const { text, document_type } = await request.json();

    // Input validation
    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: 'Invalid text parameter' },
        { status: 400 }
      );
    }

    // Process request
    const result = await validateDocument(text, document_type);

    return NextResponse.json(result);

  } catch (error) {
    console.error('Validation error:', error);

    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
```

**Python Engine:**
```python
def validate_document(text, document_type=None):
    try:
        # Validate inputs
        if not text or not isinstance(text, str):
            raise ValueError("Invalid text parameter")

        # Run validation
        results = engine.validate(text, document_type)

        return results

    except Exception as e:
        logging.error(f"Validation error: {e}")
        return {
            'validation': {
                'overall_status': 'ERROR',
                'error': str(e)
            }
        }
```

## Performance Considerations

### Frontend Optimization

1. **Code Splitting**
   - Lazy load components
   - Dynamic imports for large libraries

2. **Debouncing**
   - Debounce text input
   - Prevent excessive API calls

3. **Caching**
   - Cache validation results (session storage)
   - Avoid re-validating identical text

### Backend Optimization

1. **Gate Caching**
   - Gates loaded once at startup
   - Reused across requests

2. **Pattern Compilation**
   - Regex patterns compiled once
   - Stored in memory

3. **Lazy Loading**
   - Modules loaded on demand
   - Gates only executed if relevant

### Vercel Optimization

1. **Edge Functions**
   - Consider for simple routes
   - Lower latency

2. **Serverless Configuration**
   - Optimize function memory
   - Set appropriate timeouts

3. **Cold Start Mitigation**
   - Keep functions warm
   - Optimize bundle size

## Security Architecture

### Input Validation

**Frontend:**
```javascript
function sanitizeInput(text) {
  // Remove potentially malicious content
  return text
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<iframe[^>]*>.*?<\/iframe>/gi, '')
    .trim();
}
```

**Backend:**
```python
def validate_input(text):
    # Check text length
    if len(text) > 100000:  # 100KB limit
        raise ValueError("Text too long")

    # Check for null bytes
    if '\x00' in text:
        raise ValueError("Invalid characters")

    return text
```

### API Security

1. **Rate Limiting**
   - Limit requests per IP
   - Prevent abuse

2. **Input Validation**
   - Validate all inputs
   - Sanitize user data

3. **CORS**
   - Configure allowed origins
   - Restrict access

4. **No Authentication (Current)**
   - Public API
   - Consider adding auth for production

## Scalability

### Horizontal Scaling

**Vercel Serverless:**
- Automatic scaling
- No configuration needed
- Scales with traffic

**Stateless Design:**
- No session affinity required
- Any instance can handle any request

### Vertical Scaling

**Memory Allocation:**
- Configure Vercel function memory
- Balance cost vs performance

**Timeout Settings:**
- Set appropriate timeouts
- Prevent long-running requests

## Monitoring and Observability

### Logging

**Frontend:**
```javascript
console.log('[Validation] Request:', { text, documentType });
console.log('[Validation] Response:', result);
console.error('[Validation] Error:', error);
```

**Backend:**
```python
import logging

logging.info(f'Validation request: {len(text)} chars')
logging.debug(f'Gates executed: {gate_count}')
logging.error(f'Validation error: {error}')
```

### Metrics

**Track:**
- Request volume
- Response times
- Error rates
- Gate execution times
- Correction success rates

**Vercel Analytics:**
- Built-in analytics
- Function execution metrics
- Error tracking

## Deployment Architecture

### Vercel Deployment

```
GitHub Repository
      ↓
  [Push to branch]
      ↓
Vercel Auto-Deploy
      ↓
┌─────────────────┐
│  Build Process  │
│  - npm install  │
│  - npm build    │
└────────┬────────┘
         ↓
┌────────────────────┐
│ Serverless Deploy │
│ - Frontend: Static │
│ - API: Functions   │
└────────┬───────────┘
         ↓
┌────────────────┐
│  Production    │
│  - CDN         │
│  - Edge Cache  │
│  - Functions   │
└────────────────┘
```

### Environment Separation

**Development:**
- Local: localhost:3000, localhost:3001
- Runs on developer machine
- Hot reload enabled

**Preview (Vercel):**
- Per-branch deployments
- Automatic on push
- URL: `https://...-git-branch-user.vercel.app`

**Production (Vercel):**
- Main branch
- Custom domain
- URL: `https://loki-interceptor.vercel.app`

## Extension Points

### Adding New Modules

1. Create directory: `backend/modules/new_module/`
2. Create `module.py` with `get_gates()`
3. Create `gates/` directory
4. Implement gate classes
5. Register gates in `get_gates()`

### Adding New Gates

1. Create gate file: `backend/modules/{module}/gates/new_gate.py`
2. Implement gate class
3. Add to `module.py` gate list
4. Add correction patterns in `backend/core/correction_patterns.py`

### Adding New Correction Strategies

1. Extend `CorrectionStrategy` class
2. Implement `can_apply()` and `apply()`
3. Register in `DocumentCorrector`

### Adding New API Endpoints

1. Create: `frontend/src/app/api/new-endpoint/route.js`
2. Export `POST` or `GET` function
3. Implement handler logic
4. Return `NextResponse.json()`

## Architecture Patterns

### Patterns Used

1. **Strategy Pattern** - Correction strategies
2. **Registry Pattern** - Module/gate registration
3. **Factory Pattern** - Gate instantiation
4. **Template Method** - Gate check pattern
5. **Builder Pattern** - Result construction
6. **Singleton** - Engine instance (per request)

### Design Principles

1. **Separation of Concerns** - Frontend/Backend/Validation/Correction separate
2. **Open/Closed** - Open for extension (new modules), closed for modification
3. **Single Responsibility** - Each gate checks one thing
4. **Dependency Inversion** - Depend on abstractions (gate interface)
5. **Interface Segregation** - Minimal gate interface

## Production Status

### Current System State

**Correction System: ✅ PRODUCTION READY**
- Version: Enterprise-grade multi-level correction
- Pattern Count: 107 patterns (+133% from baseline of 46)
- Test Status: 11/11 PASSED (100%)
- Performance: 5.15M chars/sec (515x above 10K threshold)
- Determinism: Perfect (byte-identical across runs)
- Deployment: Ready for immediate production

**Module Coverage:**
- FCA UK: 23 patterns (100% critical gates covered)
- GDPR UK: 31 patterns (100% critical gates covered)
- Tax UK: 18 patterns (100% critical gates covered)
- NDA UK: 15 patterns (100% critical gates covered)
- HR Scottish: 20 patterns (100% critical gates covered)

**Strategy Distribution:**
- Regex Replacement: 61 patterns
- Template Insertion: 44 patterns
- Structural Reorganization: 2 patterns
- Suggestion Extraction: Dynamic (gate-driven)

**Quality Metrics:**
- Zero breaking changes
- Fully backward compatible
- All critical compliance gaps closed
- Perfect determinism verified
- Performance requirements exceeded

**Documentation:**
- TEST_REPORT.md: Complete production readiness report (22KB)
- CORRECTOR_README.md: System documentation
- Claude Skills: 5 comprehensive skills (6,700+ lines)
- Audit Reports: Complete gap analysis

**Deployment Configuration:**
- Platform: Vercel (serverless)
- Branch Strategy: Feature branch → Preview → Production
- CI/CD: Automated testing on push
- Monitoring: Test results tracking

### Recent Enhancements

**Enhancement Phase (Latest):**
1. Expanded pattern registry from 46 to 107 patterns
2. Closed all 59 critical correction gaps
3. Implemented 2 bug fixes (pattern matching, GDPR regex)
4. Added comprehensive test suite (11 tests)
5. Verified production readiness (100% pass rate)
6. Performance optimization (5.15M chars/sec)

**Files Modified:**
- backend/core/correction_patterns.py: 584 → 1,020+ lines
- backend/core/correction_strategies.py: Bug fixes applied
- New test suites: 3 files (test_advanced_corrector.py, test_enhanced_corrections.py, comprehensive_test_runner.py)
- Documentation: TEST_REPORT.md, CORRECTION_ENHANCEMENTS.md

## When to Use This Skill

Activate this skill when:
- Understanding system architecture
- Planning new features
- Integrating components
- Debugging data flow
- Optimizing performance
- Designing APIs
- Extending the system
- Reviewing architecture decisions
- Documenting system design
- Onboarding new developers
