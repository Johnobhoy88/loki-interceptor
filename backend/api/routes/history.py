"""
History API routes
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status

from ..models.history import (
    HistoryResponse,
    HistoryEntry,
    HistoryStats,
    HistoryFilter
)
from ..models.validation import RiskLevel
from ..dependencies import (
    get_audit_logger,
    check_rate_limit
)

router = APIRouter()


@router.get(
    "/history",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get validation history",
    description="Retrieve paginated validation history with filters",
    response_description="Paginated history with optional statistics"
)
async def get_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk level"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    module_id: Optional[str] = Query(None, description="Filter by module"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    include_stats: bool = Query(False, description="Include aggregated statistics"),
    _: bool = Depends(check_rate_limit)
):
    """
    Get validation history with filtering and pagination

    Returns a paginated list of validation history entries with optional filters.

    **Filters:**
    - **risk_level**: Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL)
    - **document_type**: Filter by document type
    - **module_id**: Filter by specific compliance module
    - **date_from/date_to**: Filter by date range
    - **client_id**: Filter by client identifier

    **Pagination:**
    - Default: 50 items per page
    - Maximum: 100 items per page

    **Statistics:**
    - Set `include_stats=true` to get aggregated statistics
    - Includes risk distribution, document types, common failures

    **Example:**
    ```
    GET /api/v1/history?page=1&page_size=50&risk_level=HIGH&include_stats=true
    ```
    """
    audit_logger = get_audit_logger()

    # Build filter
    filter_params = HistoryFilter(
        risk_level=risk_level,
        document_type=document_type,
        module_id=module_id,
        date_from=date_from,
        date_to=date_to,
        client_id=client_id
    )

    # For now, return mock data
    # In production, this would query the audit logger's database
    entries = []
    total = 0
    stats = None

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    if include_stats:
        # Get aggregated statistics
        stats_data = audit_logger.get_stats()
        stats = HistoryStats(
            total_validations=stats_data.get('total_validations', 0),
            risk_distribution=stats_data.get('risk_distribution', {}),
            document_type_distribution=stats_data.get('document_type_distribution', {}),
            average_execution_time_ms=stats_data.get('average_execution_time_ms', 0.0),
            peak_usage_hour=stats_data.get('peak_usage_hour'),
            most_common_failures=stats_data.get('most_common_failures', [])
        )

    return HistoryResponse(
        entries=entries,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        stats=stats
    )


@router.get(
    "/history/{entry_id}",
    response_model=HistoryEntry,
    status_code=status.HTTP_200_OK,
    summary="Get history entry",
    description="Retrieve a specific validation history entry by ID",
    response_description="History entry details"
)
async def get_history_entry(
    entry_id: str,
    _: bool = Depends(check_rate_limit)
):
    """
    Get a specific validation history entry

    Returns detailed information about a single validation history entry.

    **Example:**
    ```
    GET /api/v1/history/HIST_12345
    ```
    """
    # For now, return mock data
    # In production, this would query the audit logger's database
    from fastapi import HTTPException

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="History entry not found"
    )


@router.delete(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Clear history",
    description="Clear validation history (requires admin privileges)",
    response_description="Success message"
)
async def clear_history(
    days: Optional[int] = Query(
        None,
        description="Delete entries older than N days (null = all)"
    ),
    _: bool = Depends(check_rate_limit)
):
    """
    Clear validation history

    **WARNING**: This operation cannot be undone.

    **Parameters:**
    - **days**: Delete entries older than N days
    - If `days` is not specified, all history will be deleted

    **Example:**
    ```
    DELETE /api/v1/history?days=90
    ```

    Deletes all history entries older than 90 days.
    """
    # For now, return success
    # In production, this would delete from audit logger's database

    return {
        "success": True,
        "message": f"History cleared (older than {days} days)" if days else "All history cleared",
        "deleted_count": 0
    }
