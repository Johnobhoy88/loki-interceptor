"""
Correction Monitoring Dashboard - Real-time monitoring and analytics

Features:
- Real-time metrics
- Job queue monitoring
- Performance analytics
- Resource utilization
- Error tracking
- Historical trends
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import asyncio

try:
    from ..core.correction_scheduler import CorrectionScheduler
    from ..core.batch_corrector import BatchCorrector
except ImportError:
    pass


@dataclass
class CorrectionMetrics:
    """Correction metrics snapshot"""
    timestamp: datetime
    total_corrections: int
    successful_corrections: int
    failed_corrections: int
    average_execution_time_ms: float
    average_improvement_score: float
    queue_length: int
    active_jobs: int
    throughput_per_minute: float


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_connections: int


class CorrectionDashboard:
    """
    Real-time monitoring dashboard for correction system

    Features:
    - Live metrics collection
    - Performance tracking
    - Resource monitoring
    - Analytics and trends
    - Alerting (basic)
    """

    def __init__(self, metrics_retention_hours: int = 24):
        """
        Initialize dashboard

        Args:
            metrics_retention_hours: How long to retain metrics (default: 24 hours)
        """
        self.metrics_retention_hours = metrics_retention_hours
        self.metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 data points
        self.error_log: deque = deque(maxlen=100)  # Keep last 100 errors
        self.start_time = datetime.utcnow()

        # Performance counters
        self.counters = {
            'total_corrections': 0,
            'successful_corrections': 0,
            'failed_corrections': 0,
            'total_execution_time_ms': 0.0,
            'total_improvement_score': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }

        # Time-based metrics (last minute)
        self.recent_corrections: deque = deque(maxlen=100)

    async def collect_metrics(self) -> CorrectionMetrics:
        """Collect current correction metrics"""
        # Get queue stats
        queue_stats = await CorrectionScheduler.get_queue_stats()

        # Calculate averages
        avg_execution_time = 0.0
        avg_improvement = 0.0

        if self.counters['successful_corrections'] > 0:
            avg_execution_time = (
                self.counters['total_execution_time_ms'] /
                self.counters['successful_corrections']
            )
            avg_improvement = (
                self.counters['total_improvement_score'] /
                self.counters['successful_corrections']
            )

        # Calculate throughput (corrections per minute)
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        recent_count = sum(
            1 for ts in self.recent_corrections
            if ts > one_minute_ago
        )

        metrics = CorrectionMetrics(
            timestamp=now,
            total_corrections=self.counters['total_corrections'],
            successful_corrections=self.counters['successful_corrections'],
            failed_corrections=self.counters['failed_corrections'],
            average_execution_time_ms=round(avg_execution_time, 2),
            average_improvement_score=round(avg_improvement, 3),
            queue_length=queue_stats.get('queue_length', 0),
            active_jobs=queue_stats.get('processing', 0),
            throughput_per_minute=recent_count
        )

        # Store in history
        self.metrics_history.append(metrics)

        # Clean old metrics
        self._clean_old_metrics()

        return metrics

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system resource metrics"""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            connections = len(psutil.net_connections())

            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu,
                memory_percent=memory,
                disk_usage_percent=disk,
                active_connections=connections
            )
        except ImportError:
            # psutil not available, return mock data
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                active_connections=0
            )

    def record_correction(
        self,
        execution_time_ms: float,
        improvement_score: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Record a correction event

        Args:
            execution_time_ms: Execution time in milliseconds
            improvement_score: Improvement score (0.0-1.0)
            success: Whether correction was successful
            error: Error message (if failed)
        """
        self.counters['total_corrections'] += 1

        if success:
            self.counters['successful_corrections'] += 1
            self.counters['total_execution_time_ms'] += execution_time_ms
            self.counters['total_improvement_score'] += improvement_score
            self.recent_corrections.append(datetime.utcnow())
        else:
            self.counters['failed_corrections'] += 1

            # Log error
            if error:
                self.error_log.append({
                    'timestamp': datetime.utcnow(),
                    'error': error,
                    'execution_time_ms': execution_time_ms
                })

    def record_cache_hit(self):
        """Record a cache hit"""
        self.counters['cache_hits'] += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.counters['cache_misses'] += 1

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete dashboard data

        Returns:
            Dashboard data with metrics, stats, and trends
        """
        # Collect current metrics
        current_metrics = await self.collect_metrics()
        system_metrics = await self.collect_system_metrics()

        # Get queue stats
        queue_stats = await CorrectionScheduler.get_queue_stats()

        # Calculate cache hit rate
        total_cache_requests = (
            self.counters['cache_hits'] +
            self.counters['cache_misses']
        )
        cache_hit_rate = 0.0
        if total_cache_requests > 0:
            cache_hit_rate = self.counters['cache_hits'] / total_cache_requests

        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()

        # Get trends
        trends = self._calculate_trends()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime_seconds,
            'current_metrics': asdict(current_metrics),
            'system_metrics': asdict(system_metrics),
            'queue_stats': queue_stats,
            'cache_stats': {
                'hits': self.counters['cache_hits'],
                'misses': self.counters['cache_misses'],
                'hit_rate': round(cache_hit_rate, 3)
            },
            'trends': trends,
            'recent_errors': list(self.error_log)[-10:],  # Last 10 errors
            'health': self._assess_health(current_metrics, system_metrics)
        }

    async def get_performance_report(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate performance report for specified time period

        Args:
            hours: Number of hours to include in report

        Returns:
            Performance report with analytics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter metrics within time period
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {
                'period_hours': hours,
                'data_points': 0,
                'message': 'No data available for specified period'
            }

        # Calculate aggregates
        total_corrections = sum(m.total_corrections for m in recent_metrics)
        successful = sum(m.successful_corrections for m in recent_metrics)
        failed = sum(m.failed_corrections for m in recent_metrics)

        avg_execution_time = sum(
            m.average_execution_time_ms for m in recent_metrics
        ) / len(recent_metrics)

        avg_improvement = sum(
            m.average_improvement_score for m in recent_metrics
        ) / len(recent_metrics)

        avg_throughput = sum(
            m.throughput_per_minute for m in recent_metrics
        ) / len(recent_metrics)

        # Peak metrics
        peak_throughput = max(m.throughput_per_minute for m in recent_metrics)
        peak_queue = max(m.queue_length for m in recent_metrics)

        return {
            'period_hours': hours,
            'start_time': cutoff_time.isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'data_points': len(recent_metrics),
            'summary': {
                'total_corrections': total_corrections,
                'successful': successful,
                'failed': failed,
                'success_rate': round(successful / max(total_corrections, 1), 3),
                'average_execution_time_ms': round(avg_execution_time, 2),
                'average_improvement_score': round(avg_improvement, 3),
                'average_throughput_per_minute': round(avg_throughput, 2)
            },
            'peaks': {
                'max_throughput_per_minute': peak_throughput,
                'max_queue_length': peak_queue
            },
            'timeline': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'throughput': m.throughput_per_minute,
                    'queue_length': m.queue_length,
                    'avg_execution_time_ms': m.average_execution_time_ms
                }
                for m in recent_metrics[-50:]  # Last 50 data points
            ]
        }

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate metric trends"""
        if len(self.metrics_history) < 2:
            return {
                'throughput_trend': 'stable',
                'execution_time_trend': 'stable',
                'queue_trend': 'stable'
            }

        # Get recent and older metrics
        recent = list(self.metrics_history)[-10:]  # Last 10 data points
        older = list(self.metrics_history)[-20:-10] if len(self.metrics_history) >= 20 else recent

        # Calculate averages
        recent_throughput = sum(m.throughput_per_minute for m in recent) / len(recent)
        older_throughput = sum(m.throughput_per_minute for m in older) / len(older)

        recent_exec_time = sum(m.average_execution_time_ms for m in recent) / len(recent)
        older_exec_time = sum(m.average_execution_time_ms for m in older) / len(older)

        recent_queue = sum(m.queue_length for m in recent) / len(recent)
        older_queue = sum(m.queue_length for m in older) / len(older)

        # Determine trends
        def trend(recent_val, older_val, threshold=0.1):
            if recent_val > older_val * (1 + threshold):
                return 'increasing'
            elif recent_val < older_val * (1 - threshold):
                return 'decreasing'
            else:
                return 'stable'

        return {
            'throughput_trend': trend(recent_throughput, older_throughput),
            'execution_time_trend': trend(recent_exec_time, older_exec_time),
            'queue_trend': trend(recent_queue, older_queue),
            'throughput_change_percent': round(
                ((recent_throughput - older_throughput) / max(older_throughput, 0.01)) * 100, 1
            ),
            'execution_time_change_percent': round(
                ((recent_exec_time - older_exec_time) / max(older_exec_time, 0.01)) * 100, 1
            )
        }

    def _assess_health(
        self,
        metrics: CorrectionMetrics,
        system: SystemMetrics
    ) -> Dict[str, Any]:
        """Assess overall system health"""
        issues = []
        warnings = []

        # Check queue length
        if metrics.queue_length > 100:
            issues.append("High queue length detected")
        elif metrics.queue_length > 50:
            warnings.append("Queue length elevated")

        # Check error rate
        total = metrics.total_corrections
        if total > 0:
            error_rate = metrics.failed_corrections / total
            if error_rate > 0.1:
                issues.append(f"High error rate: {error_rate:.1%}")
            elif error_rate > 0.05:
                warnings.append(f"Elevated error rate: {error_rate:.1%}")

        # Check system resources
        if system.cpu_percent > 90:
            issues.append("High CPU usage")
        elif system.cpu_percent > 75:
            warnings.append("Elevated CPU usage")

        if system.memory_percent > 90:
            issues.append("High memory usage")
        elif system.memory_percent > 75:
            warnings.append("Elevated memory usage")

        # Determine overall status
        if issues:
            status = "unhealthy"
        elif warnings:
            status = "degraded"
        else:
            status = "healthy"

        return {
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _clean_old_metrics(self):
        """Remove metrics older than retention period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.metrics_retention_hours)

        # Clean metrics history
        while self.metrics_history and self.metrics_history[0].timestamp < cutoff_time:
            self.metrics_history.popleft()

    async def start_collection_loop(self, interval_seconds: int = 60):
        """
        Start periodic metrics collection

        Args:
            interval_seconds: Collection interval in seconds
        """
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(interval_seconds)


# Global dashboard instance
_dashboard: Optional[CorrectionDashboard] = None


def get_dashboard() -> CorrectionDashboard:
    """Get global dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = CorrectionDashboard()
    return _dashboard


def reset_dashboard():
    """Reset global dashboard instance"""
    global _dashboard
    _dashboard = CorrectionDashboard()
