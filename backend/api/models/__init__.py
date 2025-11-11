"""
LOKI Interceptor API Models

Pydantic models for request/response validation
"""

from .validation import (
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    ModuleResult,
    GateResult,
    RiskLevel
)

from .correction import (
    CorrectionRequest,
    CorrectionResponse,
    CorrectionIssue,
    CorrectionApplication
)

from .history import (
    HistoryEntry,
    HistoryResponse,
    HistoryFilter,
    HistoryStats
)

from .modules import (
    ModuleInfo,
    ModulesResponse,
    GateInfo,
    GatesResponse
)

from .stats import (
    SystemStats,
    ModuleStats,
    RiskTrend,
    AnalyticsOverview
)

from .websocket import (
    WebSocketMessage,
    WebSocketValidationRequest,
    WebSocketValidationResponse,
    WebSocketError
)

from .common import (
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse,
    SortOrder,
    FilterOperator
)

__all__ = [
    # Validation
    'ValidationRequest',
    'ValidationResponse',
    'ValidationResult',
    'ModuleResult',
    'GateResult',
    'RiskLevel',

    # Correction
    'CorrectionRequest',
    'CorrectionResponse',
    'CorrectionIssue',
    'CorrectionApplication',

    # History
    'HistoryEntry',
    'HistoryResponse',
    'HistoryFilter',
    'HistoryStats',

    # Modules
    'ModuleInfo',
    'ModulesResponse',
    'GateInfo',
    'GatesResponse',

    # Stats
    'SystemStats',
    'ModuleStats',
    'RiskTrend',
    'AnalyticsOverview',

    # WebSocket
    'WebSocketMessage',
    'WebSocketValidationRequest',
    'WebSocketValidationResponse',
    'WebSocketError',

    # Common
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'SortOrder',
    'FilterOperator'
]
