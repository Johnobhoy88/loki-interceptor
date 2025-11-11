# LOKI Interceptor Database Schema Documentation

## Overview

This document describes the enterprise-grade database architecture for LOKI Interceptor, implementing comprehensive data persistence, versioning, audit trails, and analytics capabilities.

## Architecture

### Technology Stack
- **ORM**: SQLAlchemy 2.0+
- **Migration System**: Alembic 1.13+
- **Primary Database**: SQLite (file-based or in-memory)
- **Enterprise Support**: PostgreSQL compatible
- **Connection Pooling**: SQLAlchemy QueuePool/StaticPool
- **Data Export**: CSV, JSON, JSONL, Excel (openpyxl)

### Design Principles
1. **Repository Pattern**: Clean separation of data access logic
2. **Soft Deletes**: Preserve data integrity with logical deletion
3. **Version Control**: Full document versioning with parent-child relationships
4. **Audit Trail**: Comprehensive activity logging for compliance
5. **Performance**: Strategic indexing for common queries
6. **Flexibility**: JSON fields for extensible metadata

---

## Database Schema

### Schema Diagram

```
┌─────────────────┐
│      Tags       │
└─────────────────┘
        │
        │ many-to-many
        ▼
┌─────────────────┐         ┌──────────────────┐
│   Documents     │◄────────┤ Document_Tags    │
│                 │         │ (Association)    │
│  - id           │         └──────────────────┘
│  - content_hash │
│  - document_type│         ┌──────────────────┐
│  - content      │◄────────┤   Validations    │
│  - version      │         │                  │
│  - parent_id    │         │  - id            │
│  - is_latest    │         │  - document_id   │
│  - is_deleted   │         │  - overall_risk  │
└─────────────────┘         │  - status        │
        │                   └──────────────────┘
        │ self-referencing           │
        │ (versioning)               │
        │                            ▼
        │                   ┌──────────────────┐
        ├───────────────────┤ ValidationResult │
        │                   │                  │
        │                   │  - validation_id │
        │                   │  - gate_key      │
        │                   │  - status        │
        │                   │  - severity      │
        │                   └──────────────────┘
        │
        ▼
┌─────────────────┐         ┌──────────────────┐
│   Corrections   │◄────────┤ CorrectionHistory│
│                 │         │                  │
│  - id           │         │  - correction_id │
│  - document_id  │         │  - change_type   │
│  - validation_id│         │  - previous_state│
│  - status       │         │  - new_state     │
└─────────────────┘         └──────────────────┘

┌─────────────────┐
│   AuditTrail    │
│                 │
│  - id           │
│  - action       │
│  - entity_type  │
│  - entity_id    │
│  - actor_id     │
│  - changes      │
│  - timestamp    │
└─────────────────┘

┌─────────────────────────┐    ┌──────────────────┐
│ DataRetentionPolicies   │    │   ExportLogs     │
│                         │    │                  │
│  - id                   │    │  - id            │
│  - entity_type          │    │  - export_type   │
│  - retention_days       │    │  - entity_type   │
│  - action               │    │  - file_path     │
│  - is_active            │    │  - status        │
└─────────────────────────┘    └──────────────────┘
```

---

## Table Specifications

### 1. Documents

**Purpose**: Core table for storing all documents processed through LOKI Interceptor with versioning support.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| content_hash | String(64) | No | SHA-256 hash of content (unique) |
| document_type | Enum | No | Document classification (email, contract, etc.) |
| content | Text | No | Document content |
| content_length | Integer | No | Content length in characters |
| title | String(500) | Yes | Document title |
| description | Text | Yes | Document description |
| source | String(500) | Yes | Source system or file path |
| language | String(10) | Yes | Language code (default: 'en') |
| metadata_json | JSON | Yes | Additional metadata |
| client_id | String(100) | No | Client identifier |
| tenant_id | String(100) | Yes | Tenant identifier (multi-tenancy) |
| user_id | String(100) | Yes | User who created document |
| version | Integer | No | Version number (default: 1) |
| parent_id | Integer | Yes | Parent document ID (for versioning) |
| is_latest | Boolean | No | Flag for latest version |
| created_at | DateTime | No | Creation timestamp |
| updated_at | DateTime | No | Last update timestamp |
| deleted_at | DateTime | Yes | Soft delete timestamp |
| is_deleted | Boolean | No | Soft delete flag |

**Indexes**:
- `content_hash` (unique)
- `document_type`, `client_id`, `tenant_id`, `user_id`
- `is_latest`, `is_deleted`, `created_at`
- Composite: `(client_id, created_at)`, `(document_type, created_at)`, `(tenant_id, document_type)`

**Relationships**:
- `validations`: One-to-many with Validation
- `corrections`: One-to-many with Correction
- `audit_trails`: One-to-many with AuditTrail
- `parent`: Self-referencing for version control
- `tags`: Many-to-many through document_tags

---

### 2. Validations

**Purpose**: Tracks validation execution and results for each document.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| document_id | Integer | No | Foreign key to documents |
| modules_used | JSON | No | List of validation modules |
| config | JSON | Yes | Validation configuration |
| status | Enum | No | Validation status (pending, in_progress, completed, failed) |
| started_at | DateTime | Yes | Validation start time |
| completed_at | DateTime | Yes | Validation completion time |
| duration_ms | Integer | Yes | Execution duration in milliseconds |
| overall_risk | Enum | Yes | Overall risk level (critical, high, medium, low) |
| critical_count | Integer | No | Count of critical issues |
| high_count | Integer | No | Count of high severity issues |
| medium_count | Integer | No | Count of medium severity issues |
| low_count | Integer | No | Count of low severity issues |
| pass_count | Integer | No | Count of passed gates |
| fail_count | Integer | No | Count of failed gates |
| warning_count | Integer | No | Count of warnings |
| request_hash | String(64) | No | Unique request identifier |
| client_id | String(100) | No | Client identifier |
| user_id | String(100) | Yes | User who requested validation |
| error_message | Text | Yes | Error message if failed |
| error_traceback | Text | Yes | Error traceback for debugging |
| created_at | DateTime | No | Creation timestamp |

**Indexes**:
- `document_id`, `status`, `overall_risk`, `client_id`
- Composite: `(document_id, created_at)`, `(status, overall_risk)`, `(client_id, created_at)`

---

### 3. ValidationResult

**Purpose**: Stores individual gate/check results within a validation.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| validation_id | Integer | No | Foreign key to validations |
| scope | String(50) | No | Result scope (module, universal, analyzer, cross) |
| module_id | String(100) | Yes | Module identifier |
| gate_id | String(100) | No | Gate identifier |
| gate_key | String(255) | No | Full gate key (e.g., gdpr_uk.data_minimization) |
| status | Enum | No | Gate status (pass, fail, warning, skip, error) |
| severity | Enum | Yes | Severity level |
| message | Text | Yes | Result message |
| suggestion | Text | Yes | Suggested fix |
| legal_source | Text | Yes | Legal reference |
| confidence_score | Float | Yes | Confidence score (0.0-1.0) |
| evidence | JSON | Yes | Supporting evidence |
| metadata_json | JSON | Yes | Additional metadata |
| gate_version | String(20) | Yes | Gate version |
| created_at | DateTime | No | Creation timestamp |

**Indexes**:
- `validation_id`, `scope`, `gate_key`, `status`, `severity`
- Composite: `(validation_id, scope)`, `(gate_key, status)`, `(module_id, gate_id)`

---

### 4. Corrections

**Purpose**: Manages document corrections and their lifecycle.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| document_id | Integer | No | Foreign key to documents |
| validation_id | Integer | Yes | Foreign key to validations |
| correction_type | String(50) | No | Correction type (rewrite, suggestion, auto_fix) |
| target_gate | String(255) | Yes | Gate that triggered correction |
| original_content | Text | Yes | Original content |
| corrected_content | Text | Yes | Corrected content |
| diff | JSON | Yes | Structured diff |
| strategy | String(100) | Yes | Correction strategy used |
| confidence | Float | Yes | Confidence score (0.0-1.0) |
| reasoning | Text | Yes | Explanation of correction |
| status | Enum | No | Status (pending, applied, rejected, reverted) |
| applied_at | DateTime | Yes | When correction was applied |
| applied_by | String(100) | Yes | Who applied the correction |
| reviewed_at | DateTime | Yes | Review timestamp |
| reviewed_by | String(100) | Yes | Who reviewed the correction |
| review_notes | Text | Yes | Review notes |
| client_id | String(100) | No | Client identifier |
| metadata_json | JSON | Yes | Additional metadata |
| created_at | DateTime | No | Creation timestamp |
| updated_at | DateTime | No | Last update timestamp |

**Indexes**:
- `document_id`, `validation_id`, `status`, `client_id`
- Composite: `(document_id, status)`, `(validation_id, status)`, `(correction_type, status)`

---

### 5. CorrectionHistory

**Purpose**: Tracks all changes to correction records for audit purposes.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| correction_id | Integer | No | Foreign key to corrections |
| change_type | String(50) | No | Type of change (created, updated, applied, rejected, reverted) |
| previous_status | String(50) | Yes | Previous status |
| new_status | String(50) | No | New status |
| changes | JSON | Yes | Changed fields and values |
| reason | Text | Yes | Reason for change |
| changed_by | String(100) | Yes | Who made the change |
| changed_at | DateTime | No | When change was made |

**Indexes**:
- `correction_id`, `changed_at`
- Composite: `(correction_id, changed_at)`, `(change_type, changed_at)`

---

### 6. AuditTrail

**Purpose**: Comprehensive audit trail for all system operations.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| document_id | Integer | Yes | Foreign key to documents |
| validation_id | Integer | Yes | Foreign key to validations |
| action | String(100) | No | Action performed (create, read, update, delete, etc.) |
| entity_type | String(50) | No | Entity type (document, validation, correction) |
| entity_id | Integer | Yes | Entity ID |
| actor_id | String(100) | No | User or system that performed action |
| actor_type | String(50) | No | Actor type (user, system, api) |
| changes | JSON | Yes | Before/after values |
| metadata_json | JSON | Yes | Additional metadata |
| ip_address | String(45) | Yes | IP address (supports IPv6) |
| user_agent | String(500) | Yes | User agent string |
| request_id | String(100) | Yes | Request correlation ID |
| timestamp | DateTime | No | When action occurred |
| client_id | String(100) | No | Client identifier |
| tenant_id | String(100) | Yes | Tenant identifier |

**Indexes**:
- `action`, `entity_type`, `entity_id`, `actor_id`, `timestamp`
- Composite: `(action, timestamp)`, `(entity_type, entity_id, timestamp)`, `(actor_id, timestamp)`

---

### 7. Tags

**Purpose**: Flexible tagging system for document categorization.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| name | String(100) | No | Tag name (unique) |
| description | Text | Yes | Tag description |
| category | String(50) | Yes | Tag category |
| color | String(7) | Yes | Hex color code |
| created_at | DateTime | No | Creation timestamp |

---

### 8. DataRetentionPolicies

**Purpose**: Automated data lifecycle management.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| name | String(200) | No | Policy name (unique) |
| description | Text | Yes | Policy description |
| entity_type | String(50) | No | Target entity type |
| retention_days | Integer | No | Days to retain (must be > 0) |
| action | Enum | No | Action to take (archive, delete, anonymize, compress) |
| criteria | JSON | Yes | Additional criteria |
| is_active | Boolean | No | Whether policy is active |
| priority | Integer | No | Priority for conflict resolution (default: 100) |
| last_run | DateTime | Yes | Last execution time |
| next_run | DateTime | Yes | Next scheduled run |
| total_processed | Integer | No | Total records processed |
| total_affected | Integer | No | Total records affected |
| created_at | DateTime | No | Creation timestamp |
| updated_at | DateTime | No | Last update timestamp |
| created_by | String(100) | Yes | Policy creator |

---

### 9. ExportLogs

**Purpose**: Track data exports for compliance and management.

**Columns**:
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key |
| export_type | String(50) | No | Export format (csv, json, excel, jsonl) |
| entity_type | String(50) | No | Entity type exported |
| filters | JSON | Yes | Filters applied |
| fields | JSON | Yes | Fields included |
| record_count | Integer | No | Number of records exported |
| file_size_bytes | Integer | Yes | File size in bytes |
| file_path | String(500) | Yes | Path to export file |
| file_hash | String(64) | Yes | SHA-256 hash of file |
| status | String(50) | No | Export status (pending, completed, failed) |
| error_message | Text | Yes | Error message if failed |
| requested_by | String(100) | No | User who requested export |
| client_id | String(100) | No | Client identifier |
| requested_at | DateTime | No | Request timestamp |
| completed_at | DateTime | Yes | Completion timestamp |
| expires_at | DateTime | Yes | Export file expiration |

---

## Usage Examples

### 1. Creating a Document with Validation

```python
from backend.db.session import get_session
from backend.db.repositories import DocumentRepository, ValidationRepository
from backend.db.models import DocumentType, RiskLevel

# Create document
with get_session() as session:
    doc_repo = DocumentRepository(session)

    document = doc_repo.create_document(
        content="Sample financial document...",
        document_type=DocumentType.FINANCIAL,
        client_id="client_123",
        title="Q4 Financial Report",
        language="en"
    )

    # Create validation
    val_repo = ValidationRepository(session)
    validation = val_repo.create_validation(
        document_id=document.id,
        modules_used=["fca_uk", "gdpr_uk"],
        client_id="client_123"
    )

    session.commit()
```

### 2. Searching Documents

```python
from backend.db.query_builder import DocumentQueryBuilder
from backend.db.session import get_session

with get_session() as session:
    query = DocumentQueryBuilder(session)

    documents = query.by_client("client_123") \
        .by_type(DocumentType.FINANCIAL) \
        .not_deleted() \
        .latest_versions() \
        .search_content("annual report") \
        .order_by("created_at", SortOrder.DESC) \
        .limit(10) \
        .all()
```

### 3. Exporting Data

```python
from backend.db.export_manager import ExportManager, ExportFormat

export_mgr = ExportManager()

result = export_mgr.export_validations(
    format=ExportFormat.EXCEL,
    client_id="client_123",
    requested_by="user@example.com",
    filters={
        "risk_level": "critical",
        "start_date": "2025-01-01"
    }
)

print(f"Exported {result['record_count']} records to {result['file_path']}")
```

### 4. Creating a Backup

```python
from backend.db.backup_manager import BackupManager

backup_mgr = BackupManager()

backup_info = backup_mgr.create_backup(
    backup_name="daily_backup",
    compress=True,
    include_audit=False
)

print(f"Backup created: {backup_info['name']}")
print(f"Size: {backup_info['size']} bytes")
```

### 5. Audit Trail Query

```python
from backend.db.repositories import AuditRepository

with get_session() as session:
    audit_repo = AuditRepository(session)

    # Get all actions by a user
    actions = audit_repo.get_by_actor(
        actor_id="user@example.com",
        limit=100
    )

    # Get activity timeline
    timeline = audit_repo.get_activity_timeline(
        client_id="client_123",
        days=7
    )
```

---

## Migration Management

### Initialize Database

```bash
# Initialize database schema
alembic upgrade head
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123
```

### View Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose
```

---

## Performance Optimization

### Index Strategy

1. **Single-column indexes**: On frequently queried columns (client_id, status, timestamps)
2. **Composite indexes**: For common filter combinations
3. **Covering indexes**: For queries that can be satisfied by index alone

### Query Optimization Tips

1. Use the query builder for complex queries
2. Leverage eager loading for relationships
3. Use pagination for large result sets
4. Monitor query execution time with SQLAlchemy logging
5. Regularly analyze query plans with EXPLAIN

### Connection Pooling

- **SQLite**: Uses StaticPool for simplicity
- **PostgreSQL**: Uses QueuePool with configurable pool size
- Default pool size: 5 connections
- Max overflow: 10 connections
- Connection recycling: 1 hour

---

## Maintenance Tasks

### Database Health Check

```python
from backend.db.session import DatabaseHealth

# Check connection
is_healthy = DatabaseHealth.check_connection()

# Get pool statistics
stats = DatabaseHealth.get_stats()

# Get table counts
counts = DatabaseHealth.get_table_counts()
```

### Data Retention

```python
from backend.db.repositories import AuditRepository

with get_session() as session:
    audit_repo = AuditRepository(session)

    # Clean up old audit entries
    deleted = audit_repo.cleanup_old_entries(
        retention_days=365,
        batch_size=1000
    )
```

### Backup Cleanup

```python
from backend.db.backup_manager import BackupManager

backup_mgr = BackupManager()

# Delete old backups
deleted = backup_mgr.cleanup_old_backups(
    keep_count=10,
    keep_days=30
)
```

---

## Security Considerations

1. **SQL Injection Prevention**: All queries use parameterized statements via SQLAlchemy ORM
2. **Soft Deletes**: Preserve data integrity and enable recovery
3. **Audit Logging**: Comprehensive tracking of all operations
4. **Data Encryption**: Support for at-rest encryption (database-level)
5. **Access Control**: Integration with enterprise RBAC system
6. **PII Handling**: JSON fields allow flexible data masking

---

## Troubleshooting

### Common Issues

**Issue**: Migration conflicts
```bash
# Solution: Reset to head and re-run
alembic stamp head
alembic upgrade head
```

**Issue**: Connection pool exhaustion
```python
# Solution: Increase pool size or check for connection leaks
from backend.db.session import get_engine
engine = get_engine(pool_size=10, max_overflow=20)
```

**Issue**: Slow queries
```python
# Solution: Enable SQL logging to identify problematic queries
from backend.db.session import get_engine
engine = get_engine(echo=True)
```

---

## Future Enhancements

1. **Read Replicas**: Support for read-only database replicas
2. **Sharding**: Horizontal partitioning for very large deployments
3. **Time-Series Optimization**: Specialized tables for metrics
4. **Full-Text Search**: Integration with Elasticsearch
5. **Change Data Capture**: Real-time event streaming
6. **Automated Archiving**: Cold storage for historical data

---

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Maintained By**: LOKI Development Team
