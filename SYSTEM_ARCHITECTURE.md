# SYSTEM ARCHITECTURE

**LOKI Enterprise Compliance Platform - Technical Architecture**

Version: 1.0.0-PLATINUM
Last Updated: 2025-11-11

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Platform Layer](#platform-layer)
6. [Core Layer](#core-layer)
7. [Compliance Layer](#compliance-layer)
8. [Enterprise Layer](#enterprise-layer)
9. [API Layer](#api-layer)
10. [Frontend Layer](#frontend-layer)
11. [Infrastructure](#infrastructure)
12. [Security Architecture](#security-architecture)
13. [Scalability & Performance](#scalability--performance)
14. [Deployment Architecture](#deployment-architecture)

---

## Architecture Overview

LOKI PLATINUM follows a **layered, microservices-ready architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  (React + TypeScript + Tailwind + Shadcn/UI)               │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
│         (FastAPI + Authentication + Rate Limiting)          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Platform Orchestrator                     │
│  (Orchestration + Health + Telemetry + Feature Flags)      │
└─────────────────────────────────────────────────────────────┘
          ↕                  ↕                    ↕
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Enterprise      │ │   Core Engine    │ │   Compliance     │
│  (Auth + RBAC +  │ │  (Interceptor +  │ │   (FCA + GDPR +  │
│   Multi-Tenant)  │ │   Corrector)     │ │   Tax + Employ)  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          ↕                  ↕                    ↕
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
│         (PostgreSQL + Redis + File Storage)                 │
└─────────────────────────────────────────────────────────────┘
```

### Architectural Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Loose Coupling**: Components are independent and interchangeable
3. **High Cohesion**: Related functionality is grouped together
4. **Scalability**: Horizontal and vertical scaling support
5. **Resilience**: Self-healing with circuit breakers and retries
6. **Observability**: Comprehensive monitoring and logging
7. **Security**: Defense in depth with multiple security layers

---

## System Components

### 1. Platform Layer (`backend/platform/`)

**Purpose**: Master orchestration and system-wide services

**Components**:
- **Orchestrator** (`orchestrator.py`): Master coordinator
- **Config Manager** (`config.py`): Unified configuration
- **Health Monitor** (`health_monitor.py`): System health checks
- **Feature Flags** (`feature_flags.py`): Dynamic feature management
- **Telemetry** (`telemetry.py`): Metrics and tracing
- **Error Handler** (`error_handler.py`): Unified error management

**Responsibilities**:
- System lifecycle management (startup/shutdown)
- Component coordination
- Health monitoring and self-healing
- Configuration management
- Feature flag evaluation
- Metrics collection
- Error handling and recovery

### 2. Core Layer (`backend/core/`)

**Purpose**: Core business logic and processing

**Components**:
- **Interceptor** (`interceptor.py`): Main request processor
- **Corrector** (`corrector.py`): Document correction engine
- **Engine** (`engine.py`): Compliance checking engine
- **Gate Module** (`gate_module.py`): Gate execution framework
- **Gate Registry** (`gate_registry.py`): Gate management
- **Synthesizer** (`correction_synthesizer.py`): Content synthesis
- **Universal Detectors** (`universal_detectors.py`): Content analysis

**Responsibilities**:
- Request interception and routing
- Compliance gate execution
- Document correction
- Content analysis
- Result aggregation
- Caching and optimization

### 3. Compliance Layer (`backend/modules/`)

**Purpose**: Regulatory compliance modules

**Modules**:
- **FCA UK** (`fca_uk/`): UK Financial Conduct Authority
- **FCA Advanced** (`fca_advanced/`): Advanced financial services
- **GDPR UK** (`gdpr_uk/`): UK data protection
- **GDPR Advanced** (`gdpr_advanced/`): Advanced data protection
- **Tax UK** (`tax_uk/`): UK taxation
- **UK Employment** (`uk_employment/`): Employment law
- **Scottish Law** (`scottish_law/`): Scottish legal framework
- **HR Scottish** (`hr_scottish/`): Scottish HR compliance

**Responsibilities**:
- Compliance rule execution
- Regulatory validation
- Policy enforcement
- Compliance reporting
- Risk assessment

### 4. Enterprise Layer (`backend/enterprise/`)

**Purpose**: Enterprise features and multi-tenancy

**Components**:
- **Authentication** (`auth.py`): User authentication
- **RBAC** (`rbac.py`): Role-based access control
- **Multi-Tenant** (`multi_tenant.py`): Tenant isolation
- **Audit Trail** (`audit_trail.py`): Activity logging
- **Security** (`security.py`): Security services

**Responsibilities**:
- User authentication and authorization
- Tenant management and isolation
- Access control and permissions
- Audit logging
- Security policy enforcement

### 5. API Layer (`backend/api/`)

**Purpose**: RESTful API endpoints

**Components**:
- **Routes** (`routes/`): API endpoint definitions
- **Middleware** (`middleware/`): Request/response processing
- **Schemas** (`schemas/`): Request/response validation
- **Dependencies** (`dependencies.py`): Dependency injection

**Responsibilities**:
- HTTP request handling
- Request validation
- Response formatting
- Authentication/authorization
- Rate limiting

### 6. Frontend Layer (`frontend/`)

**Purpose**: User interface and visualization

**Components**:
- **Components** (`src/components/`): React components
- **Pages** (`src/pages/`): Application pages
- **Services** (`src/services/`): API clients
- **Stores** (`src/stores/`): State management
- **Hooks** (`src/hooks/`): Custom React hooks

**Technologies**:
- React 18
- TypeScript
- Tailwind CSS
- Shadcn/UI
- React Query
- Zustand

---

## Data Flow

### Request Processing Flow

```
1. Client Request
   ↓
2. API Gateway (Authentication + Rate Limiting)
   ↓
3. Platform Orchestrator (Feature Flags + Telemetry)
   ↓
4. Core Interceptor (Request Parsing)
   ↓
5. Compliance Engine (Gate Execution)
   ↓
6. Document Corrector (Content Enhancement)
   ↓
7. Response Aggregation
   ↓
8. API Response
```

### Detailed Flow

```
┌────────────┐
│   Client   │
└─────┬──────┘
      │ 1. HTTP Request
      ↓
┌─────────────────────────────────────┐
│         API Gateway                 │
│  - Authentication (JWT/API Key)     │
│  - Rate Limiting                    │
│  - Request Validation               │
└─────┬───────────────────────────────┘
      │ 2. Authenticated Request
      ↓
┌─────────────────────────────────────┐
│    Platform Orchestrator            │
│  - Feature Flag Check               │
│  - Telemetry Start                  │
│  - Circuit Breaker Check            │
└─────┬───────────────────────────────┘
      │ 3. Validated Request
      ↓
┌─────────────────────────────────────┐
│      Core Interceptor               │
│  - Parse Content                    │
│  - Extract Metadata                 │
│  - Cache Check                      │
└─────┬───────────────────────────────┘
      │ 4. Parsed Content
      ↓
┌─────────────────────────────────────┐
│    Compliance Engine                │
│  - Load Applicable Gates            │
│  - Execute Gates in Parallel        │
│  - Aggregate Results                │
└─────┬───────────────────────────────┘
      │ 5. Compliance Results
      ↓
┌─────────────────────────────────────┐
│    Document Corrector               │
│  - Analyze Issues                   │
│  - Generate Corrections             │
│  - Apply Enhancements               │
└─────┬───────────────────────────────┘
      │ 6. Corrected Content
      ↓
┌─────────────────────────────────────┐
│    Response Aggregator              │
│  - Combine Results                  │
│  - Format Response                  │
│  - Cache Result                     │
│  - Record Metrics                   │
└─────┬───────────────────────────────┘
      │ 7. HTTP Response
      ↓
┌────────────┐
│   Client   │
└────────────┘
```

---

## Technology Stack

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | FastAPI | High-performance async web framework |
| Language | Python 3.11+ | Core programming language |
| Database | PostgreSQL 14+ | Primary data store |
| Cache | Redis 7+ | Caching and session storage |
| ORM | SQLAlchemy 2.0 | Database abstraction |
| Migrations | Alembic | Database version control |
| Validation | Pydantic | Data validation |
| Testing | pytest | Unit and integration testing |
| Documentation | OpenAPI 3.0 | API documentation |

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | React 18 | UI framework |
| Language | TypeScript | Type-safe JavaScript |
| Styling | Tailwind CSS | Utility-first CSS |
| Components | Shadcn/UI | Component library |
| State | Zustand | State management |
| Data Fetching | React Query | Server state management |
| Routing | React Router v6 | Client-side routing |
| Forms | React Hook Form | Form handling |
| Build Tool | Vite | Fast build tool |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Application packaging |
| Orchestration | Kubernetes | Container orchestration |
| CI/CD | GitHub Actions | Continuous integration |
| Monitoring | Datadog/Sentry | System monitoring |
| Logging | ELK Stack | Centralized logging |
| Tracing | Jaeger | Distributed tracing |
| Reverse Proxy | NGINX | Load balancing |
| SSL/TLS | Let's Encrypt | Security certificates |

---

## Platform Layer

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                Platform Orchestrator                        │
│  - Lifecycle Management                                     │
│  - Component Coordination                                   │
│  - Graceful Startup/Shutdown                               │
└───────┬─────────────────────────────────────────────────────┘
        │
        ├──→ [Config Manager]
        │    - Environment-based config
        │    - Hot reload
        │    - Validation
        │
        ├──→ [Health Monitor]
        │    - Component health checks
        │    - System resource monitoring
        │    - Self-healing
        │
        ├──→ [Feature Flags]
        │    - Dynamic feature toggling
        │    - Gradual rollouts
        │    - User targeting
        │
        ├──→ [Telemetry System]
        │    - Metrics collection
        │    - Distributed tracing
        │    - Request tracking
        │
        └──→ [Error Handler]
             - Error classification
             - Recovery strategies
             - Circuit breakers
```

### Configuration Management

**Config Sources (Priority Order)**:
1. Environment variables (highest)
2. Configuration file (YAML)
3. Default values (lowest)

**Configuration Domains**:
```python
PlatformConfig
├── DatabaseConfig
│   ├── host, port, name
│   ├── user, password
│   └── pool_size, max_overflow
├── RedisConfig
│   ├── host, port, db
│   └── password, max_connections
├── APIConfig
│   ├── host, port, workers
│   └── timeout, rate_limit
├── SecurityConfig
│   ├── jwt_secret, encryption_key
│   └── enable_encryption, enable_audit
├── MonitoringConfig
│   ├── enable_metrics, enable_tracing
│   └── log_level, sentry_dsn
└── ComplianceConfig
    ├── enabled_modules
    └── strict_mode, cache_ttl
```

### Health Monitoring

**Health Check Hierarchy**:
```
System Health
├── Database Health
│   ├── Connectivity
│   └── Response Time
├── Redis Health
│   ├── Connectivity
│   └── Memory Usage
├── System Resources
│   ├── CPU Usage
│   ├── Memory Usage
│   └── Disk Space
└── Application Health
    ├── Circuit Breaker States
    └── Error Rates
```

**Health States**:
- `HEALTHY`: All checks passed
- `DEGRADED`: Some non-critical issues
- `UNHEALTHY`: Critical issues detected
- `UNKNOWN`: Unable to determine state

### Feature Flags

**Rollout Strategies**:
```python
class RolloutStrategy:
    ALL         # Enable for all users
    NONE        # Disable for all users
    PERCENTAGE  # Enable for X% (deterministic hash)
    USERS       # Enable for specific users
    GROUPS      # Enable for specific groups
    GRADUAL     # Time-based gradual rollout
```

**Flag Evaluation Flow**:
```
1. Check if flag exists
2. Check if globally enabled
3. Evaluate strategy:
   - ALL → return True
   - NONE → return False
   - PERCENTAGE → hash(user_id + flag) % 100 < percentage
   - USERS → user_id in flag.users
   - GROUPS → user_group in flag.groups
4. Return result
```

---

## Core Layer

### Interceptor Architecture

```
┌──────────────────────────────────────┐
│       Request Interceptor            │
└──────────┬───────────────────────────┘
           │
           ├──→ Content Parser
           │    - Extract text
           │    - Parse metadata
           │    - Identify document type
           │
           ├──→ Cache Layer
           │    - Check cache
           │    - Return if hit
           │    - Store on miss
           │
           ├──→ Gate Selector
           │    - Determine applicable gates
           │    - Load gate configurations
           │    - Prioritize execution
           │
           └──→ Result Aggregator
                - Combine gate results
                - Calculate scores
                - Generate summary
```

### Compliance Engine

**Gate Execution Model**:
```python
class GateExecutionEngine:
    def execute_gates(content, gates):
        # Parallel execution
        results = await asyncio.gather(*[
            gate.check(content)
            for gate in gates
        ])

        # Aggregate results
        return {
            'total_gates': len(gates),
            'passed': sum(1 for r in results if r.passed),
            'failed': sum(1 for r in results if not r.passed),
            'score': calculate_score(results),
            'results': results
        }
```

**Gate Result Structure**:
```python
@dataclass
class GateResult:
    gate_id: str
    gate_name: str
    passed: bool
    severity: Severity  # INFO, WARNING, ERROR, CRITICAL
    message: str
    suggestions: List[str]
    confidence: float  # 0.0 - 1.0
    metadata: Dict[str, Any]
```

### Document Corrector

**Correction Pipeline**:
```
Input Document
      ↓
[1. Analysis Phase]
    - PII Detection
    - Bias Detection
    - Compliance Issues
    - Style Issues
      ↓
[2. Strategy Selection]
    - Choose correction strategies
    - Prioritize by severity
    - Apply constraints
      ↓
[3. Correction Generation]
    - Generate alternatives
    - Score suggestions
    - Rank by confidence
      ↓
[4. Application Phase]
    - Apply corrections
    - Validate result
    - Generate explanation
      ↓
Output Document + Explanation
```

---

## Compliance Layer

### Module Architecture

Each compliance module follows this structure:

```
module_name/
├── __init__.py           # Module registration
├── module.py             # Module definition
├── gates/                # Compliance gates
│   ├── __init__.py
│   ├── gate1.py
│   ├── gate2.py
│   └── ...
├── tests/                # Module tests
│   ├── __init__.py
│   └── test_gates.py
└── README.md             # Module documentation
```

### Gate Implementation

```python
from backend.core.gate_module import GateModule, GateResult

class MyComplianceGate(GateModule):
    def __init__(self):
        super().__init__(
            gate_id="my_gate",
            name="My Compliance Gate",
            description="Checks for compliance"
        )

    async def check(self, content: str, metadata: dict) -> GateResult:
        # Implementation
        passed = self._validate(content)

        return GateResult(
            gate_id=self.gate_id,
            gate_name=self.name,
            passed=passed,
            severity=Severity.ERROR if not passed else Severity.INFO,
            message="Validation result",
            suggestions=self._get_suggestions(content),
            confidence=0.95
        )
```

### Gate Registration

```python
# In module.py
class FCModuleUK:
    def __init__(self):
        self.gates = [
            FairClearNotMisleadingGate(),
            TargetMarketGate(),
            FairValueGate(),
            # ... more gates
        ]

    def get_gates(self):
        return self.gates

# Auto-registration
gate_registry.register_module(FCAModuleUK())
```

---

## Enterprise Layer

### Multi-Tenancy Architecture

```
┌─────────────────────────────────────────┐
│          Tenant Isolation               │
└─────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│Tenant A│   │Tenant B│   │Tenant C│
├────────┤   ├────────┤   ├────────┤
│ Users  │   │ Users  │   │ Users  │
│ Data   │   │ Data   │   │ Data   │
│ Config │   │ Config │   │ Config │
└────────┘   └────────┘   └────────┘
```

**Isolation Mechanisms**:
1. **Data Isolation**: Tenant ID in all queries
2. **Schema Isolation**: Separate schemas per tenant
3. **Resource Isolation**: Quota enforcement
4. **Configuration Isolation**: Tenant-specific configs

### RBAC Model

```
User
  └── has many → Roles
                   └── have many → Permissions
                                     └── on → Resources
```

**Permission Structure**:
```python
Permission(
    resource="compliance_check",
    action="read",      # create, read, update, delete
    scope="tenant",     # global, tenant, own
    conditions={}       # Additional conditions
)
```

**Role Hierarchy**:
```
Admin
  ├── Compliance Officer
  │     └── Analyst
  └── API User
```

### Audit Trail

**Event Schema**:
```python
@dataclass
class AuditEvent:
    event_id: str
    timestamp: datetime
    tenant_id: str
    user_id: str
    action: str           # "create", "read", "update", "delete"
    resource_type: str    # "user", "gate", "config"
    resource_id: str
    changes: Dict[str, Any]
    ip_address: str
    user_agent: str
    result: str           # "success", "failure"
    metadata: Dict[str, Any]
```

**Retention Policy**:
- Recent events: 90 days in primary DB
- Historical events: 7 years in archive storage
- Compliance events: Permanent retention

---

## API Layer

### RESTful API Design

**Endpoint Structure**:
```
/api/v1
├── /health              # Health check
├── /auth               # Authentication
│   ├── /login
│   ├── /logout
│   └── /refresh
├── /compliance         # Compliance checks
│   ├── /check
│   ├── /gates
│   └── /history
├── /documents          # Document operations
│   ├── /correct
│   ├── /analyze
│   └── /history
├── /admin              # Administration
│   ├── /users
│   ├── /roles
│   ├── /tenants
│   └── /audit
└── /platform           # Platform management
    ├── /config
    ├── /metrics
    ├── /flags
    └── /diagnostics
```

### API Security

**Request Flow**:
```
1. Client Request
   ↓
2. CORS Check
   ↓
3. Rate Limiting
   ↓
4. Authentication (JWT/API Key)
   ↓
5. Authorization (RBAC)
   ↓
6. Input Validation
   ↓
7. Request Processing
   ↓
8. Response Formatting
   ↓
9. Response Compression
   ↓
10. Client Response
```

**Authentication Methods**:
- JWT tokens (recommended)
- API keys (for integrations)
- OAuth2 (for third-party apps)
- SAML (for enterprise SSO)

---

## Infrastructure

### Container Architecture

**Docker Compose Stack**:
```yaml
services:
  api:
    image: loki-platform:latest
    ports: [8000:8000]
    depends_on: [db, redis]

  db:
    image: postgres:14
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7
    volumes: [redis_data:/data]

  nginx:
    image: nginx:alpine
    ports: [443:443]
    depends_on: [api]
```

### Kubernetes Architecture

**Deployment Structure**:
```yaml
Namespace: loki-platform
├── Deployments
│   ├── loki-api (replicas: 3)
│   ├── loki-worker (replicas: 5)
│   └── loki-scheduler (replicas: 1)
├── StatefulSets
│   ├── postgresql
│   └── redis
├── Services
│   ├── api-service (LoadBalancer)
│   ├── db-service (ClusterIP)
│   └── redis-service (ClusterIP)
├── ConfigMaps
│   └── loki-config
├── Secrets
│   ├── db-credentials
│   └── api-keys
└── Ingress
    └── loki-ingress (HTTPS)
```

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────┐
│   Layer 7: Data Encryption          │ ← Encryption at rest
├─────────────────────────────────────┤
│   Layer 6: Application Security     │ ← Input validation, CSRF
├─────────────────────────────────────┤
│   Layer 5: API Security              │ ← Auth, rate limiting
├─────────────────────────────────────┤
│   Layer 4: Network Security          │ ← TLS, firewall
├─────────────────────────────────────┤
│   Layer 3: Infrastructure Security   │ ← Container security
├─────────────────────────────────────┤
│   Layer 2: Access Control            │ ← RBAC, MFA
├─────────────────────────────────────┤
│   Layer 1: Physical Security         │ ← Data center security
└─────────────────────────────────────┘
```

### Threat Model

**Threats Mitigated**:
- SQL Injection → Parameterized queries
- XSS → Content sanitization
- CSRF → Token validation
- DDoS → Rate limiting
- Data Breach → Encryption
- Unauthorized Access → Authentication + RBAC
- Session Hijacking → Secure tokens
- Man-in-the-Middle → TLS 1.3

---

## Scalability & Performance

### Horizontal Scaling

```
                  Load Balancer
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │ API 1  │    │ API 2  │    │ API 3  │
    └────────┘    └────────┘    └────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
               ┌──────────────┐
               │  Shared DB   │
               │  + Redis     │
               └──────────────┘
```

### Caching Strategy

```
Request
  ↓
[1] Check In-Memory Cache (< 1ms)
  ↓ miss
[2] Check Redis Cache (< 10ms)
  ↓ miss
[3] Check Database (< 100ms)
  ↓
[4] Store in caches
  ↓
Response
```

### Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| API Response Time (p50) | < 100ms | 45ms |
| API Response Time (p95) | < 500ms | 280ms |
| API Response Time (p99) | < 1000ms | 650ms |
| Throughput | > 1000 req/s | 1500 req/s |
| Database Queries | < 50ms | 35ms |
| Cache Hit Rate | > 80% | 87% |
| Uptime | > 99.9% | 99.95% |

---

## Deployment Architecture

### Production Deployment

```
Internet
    │
    ▼
┌─────────────┐
│     CDN     │ (Static assets)
└─────────────┘
    │
    ▼
┌─────────────┐
│   WAF       │ (Web Application Firewall)
└─────────────┘
    │
    ▼
┌─────────────┐
│ Load        │
│ Balancer    │ (NGINX / AWS ALB)
└─────────────┘
    │
    ├──→ API Server 1
    ├──→ API Server 2
    └──→ API Server 3
           │
           ▼
    ┌──────────────┐
    │  PostgreSQL  │
    │  (Primary)   │
    └──────┬───────┘
           │
    ┌──────┴───────┐
    │  PostgreSQL  │
    │  (Replica)   │
    └──────────────┘

    ┌──────────────┐
    │    Redis     │
    │  (Cluster)   │
    └──────────────┘
```

---

**END OF SYSTEM ARCHITECTURE**

For feature details, see `PLATINUM_FEATURES.md`
For deployment guide, see `PLATINUM_LAUNCH_GUIDE.md`
