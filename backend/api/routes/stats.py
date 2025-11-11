"""
Statistics and Analytics API routes
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status

from ..models.stats import (
    SystemStats,
    ModuleStats,
    RiskTrend,
    AnalyticsOverview,
    CacheStats
)
from ..dependencies import (
    get_engine,
    get_audit_logger,
    get_cache,
    check_rate_limit
)

router = APIRouter()


@router.get(
    "/stats",
    response_model=SystemStats,
    status_code=status.HTTP_200_OK,
    summary="Get system statistics",
    description="Get comprehensive system-wide statistics",
    response_description="System statistics"
)
async def get_system_stats(
    include_trends: bool = Query(False, description="Include recent risk trends"),
    _: bool = Depends(check_rate_limit)
):
    """
    Get system-wide statistics

    Returns comprehensive statistics including:
    - Total validations and corrections
    - Module and gate counts
    - System uptime
    - Average validation time
    - Risk distribution
    - Cache statistics
    - Recent trends (optional)

    **Example:**
    ```
    GET /api/v1/stats?include_trends=true
    ```

    **Response:**
    ```json
    {
      "total_validations": 15250,
      "total_corrections": 8340,
      "total_modules": 10,
      "total_gates": 234,
      "uptime_seconds": 86400.5,
      "average_validation_time_ms": 234.5,
      "peak_validations_per_hour": 450,
      "risk_distribution": {
        "LOW": 10000,
        "MEDIUM": 3000,
        "HIGH": 2000,
        "CRITICAL": 250
      }
    }
    ```
    """
    engine = get_engine()
    audit_logger = get_audit_logger()
    cache = get_cache()

    # Get audit stats
    audit_stats = audit_logger.get_stats()

    # Get cache stats
    cache_stats_data = cache.get_stats()
    cache_stats = CacheStats(
        total_entries=cache_stats_data.get('total_entries', 0),
        cache_hits=cache_stats_data.get('cache_hits', 0),
        cache_misses=cache_stats_data.get('cache_misses', 0),
        hit_rate=cache_stats_data.get('hit_rate', 0.0),
        memory_usage_mb=cache_stats_data.get('memory_usage_mb', 0.0),
        oldest_entry_age_seconds=cache_stats_data.get('oldest_entry_age_seconds', 0.0)
    )

    # Count total gates
    total_gates = 0
    for module_obj in engine.modules.values():
        if hasattr(module_obj, 'gates'):
            total_gates += len(module_obj.gates)

    # Get recent trends if requested
    recent_trends = []
    if include_trends:
        trends_data = audit_logger.get_risk_trends(days=7)
        for trend in trends_data:
            if isinstance(trend, dict):
                recent_trends.append(
                    RiskTrend(
                        date=trend.get('date', ''),
                        low_count=trend.get('low_count', 0),
                        medium_count=trend.get('medium_count', 0),
                        high_count=trend.get('high_count', 0),
                        critical_count=trend.get('critical_count', 0),
                        total=trend.get('total', 0)
                    )
                )

    import time
    from ..main import _startup_time

    return SystemStats(
        total_validations=audit_stats.get('total_validations', 0),
        total_corrections=audit_stats.get('total_corrections', 0),
        total_modules=len(engine.modules),
        total_gates=total_gates,
        uptime_seconds=time.time() - _startup_time,
        average_validation_time_ms=audit_stats.get('average_execution_time_ms', 0.0),
        peak_validations_per_hour=audit_stats.get('peak_validations_per_hour', 0),
        risk_distribution=audit_stats.get('risk_distribution', {}),
        cache_stats=cache_stats,
        recent_trends=recent_trends
    )


@router.get(
    "/stats/analytics",
    response_model=AnalyticsOverview,
    status_code=status.HTTP_200_OK,
    summary="Get analytics overview",
    description="Get comprehensive analytics for a time period",
    response_description="Analytics overview"
)
async def get_analytics_overview(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    _: bool = Depends(check_rate_limit)
):
    """
    Get comprehensive analytics overview

    Returns detailed analytics for the specified time period including:
    - Risk trends over time
    - Module performance statistics
    - Top failing gates
    - Document type distribution

    **Example:**
    ```
    GET /api/v1/stats/analytics?days=30
    ```

    Analyzes the last 30 days of validation data.
    """
    audit_logger = get_audit_logger()

    # Calculate time range
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get risk trends
    trends_data = audit_logger.get_risk_trends(days=days)
    risk_trends = []
    for trend in trends_data:
        if isinstance(trend, dict):
            risk_trends.append(
                RiskTrend(
                    date=trend.get('date', ''),
                    low_count=trend.get('low_count', 0),
                    medium_count=trend.get('medium_count', 0),
                    high_count=trend.get('high_count', 0),
                    critical_count=trend.get('critical_count', 0),
                    total=trend.get('total', 0)
                )
            )

    # Get module performance
    module_perf_data = audit_logger.get_module_performance(
        since=period_start.isoformat()
    )
    module_performance = []
    for mod_data in module_perf_data:
        if isinstance(mod_data, dict):
            module_performance.append(
                ModuleStats(
                    module_id=mod_data.get('module_id', ''),
                    module_name=mod_data.get('module_name', ''),
                    total_executions=mod_data.get('total_executions', 0),
                    total_failures=mod_data.get('total_failures', 0),
                    failure_rate=mod_data.get('failure_rate', 0.0),
                    average_execution_time_ms=mod_data.get('average_execution_time_ms', 0.0),
                    most_common_failures=mod_data.get('most_common_failures', [])
                )
            )

    # Get top failing gates
    top_failing_gates = audit_logger.get_top_gate_failures(
        since=period_start.isoformat()
    )

    # Get stats for document type distribution
    stats = audit_logger.get_stats(since=period_start.isoformat())

    return AnalyticsOverview(
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        total_validations=stats.get('total_validations', 0),
        risk_trends=risk_trends,
        module_performance=module_performance,
        top_failing_gates=top_failing_gates,
        document_type_distribution=stats.get('document_type_distribution', {})
    )


@router.get(
    "/stats/cache",
    response_model=CacheStats,
    status_code=status.HTTP_200_OK,
    summary="Get cache statistics",
    description="Get cache performance statistics",
    response_description="Cache statistics"
)
async def get_cache_stats(
    _: bool = Depends(check_rate_limit)
):
    """
    Get cache performance statistics

    Returns cache statistics including:
    - Total cached entries
    - Cache hits and misses
    - Hit rate
    - Memory usage
    - Oldest entry age

    **Example:**
    ```
    GET /api/v1/stats/cache
    ```
    """
    cache = get_cache()
    cache_stats_data = cache.get_stats()

    return CacheStats(
        total_entries=cache_stats_data.get('total_entries', 0),
        cache_hits=cache_stats_data.get('cache_hits', 0),
        cache_misses=cache_stats_data.get('cache_misses', 0),
        hit_rate=cache_stats_data.get('hit_rate', 0.0),
        memory_usage_mb=cache_stats_data.get('memory_usage_mb', 0.0),
        oldest_entry_age_seconds=cache_stats_data.get('oldest_entry_age_seconds', 0.0)
    )


@router.post(
    "/stats/cache/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear cache",
    description="Clear the validation cache",
    response_description="Success message"
)
async def clear_cache(
    _: bool = Depends(check_rate_limit)
):
    """
    Clear the validation cache

    Removes all cached validation results. This operation cannot be undone.

    **Example:**
    ```
    POST /api/v1/stats/cache/clear
    ```
    """
    cache = get_cache()
    cache.clear()

    return {
        "success": True,
        "message": "Cache cleared successfully"
    }
