"""
Comprehensive Health Check and Monitoring System
Monitors all platform components with self-healing capabilities
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import psutil
import redis
from sqlalchemy import create_engine, text
from collections import deque

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time: float = 0.0  # milliseconds
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time,
            'metadata': self.metadata,
        }


@dataclass
class SystemHealth:
    """Overall system health report"""
    status: HealthStatus
    checks: List[HealthCheck]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    uptime: float = 0.0  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'uptime': self.uptime,
            'checks': [check.to_dict() for check in self.checks],
            'summary': {
                'total': len(self.checks),
                'healthy': sum(1 for c in self.checks if c.status == HealthStatus.HEALTHY),
                'degraded': sum(1 for c in self.checks if c.status == HealthStatus.DEGRADED),
                'unhealthy': sum(1 for c in self.checks if c.status == HealthStatus.UNHEALTHY),
            }
        }


class HealthMonitor:
    """
    Comprehensive Health Monitoring System
    Monitors all platform components with self-healing capabilities
    """

    def __init__(self, config):
        """
        Initialize health monitor

        Args:
            config: PlatformConfig instance
        """
        self.config = config
        self.start_time = time.time()
        self.checks: Dict[str, Callable] = {}
        self.health_history: deque = deque(maxlen=100)
        self.failure_counts: Dict[str, int] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default health checks"""
        self.register_check('database', self._check_database)
        self.register_check('redis', self._check_redis)
        self.register_check('system_resources', self._check_system_resources)
        self.register_check('disk_space', self._check_disk_space)
        self.register_check('memory', self._check_memory)
        self.register_check('cpu', self._check_cpu)

    def register_check(self, name: str, check_func: Callable):
        """
        Register a health check

        Args:
            name: Check name
            check_func: Async function that returns HealthCheck
        """
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")

    def register_recovery_handler(self, check_name: str, handler: Callable):
        """
        Register a recovery handler for a specific check

        Args:
            check_name: Name of the health check
            handler: Async recovery function
        """
        self.recovery_handlers[check_name] = handler
        logger.info(f"Registered recovery handler for: {check_name}")

    async def _check_database(self) -> HealthCheck:
        """Check database connectivity"""
        start = time.time()
        try:
            engine = create_engine(self.config.database.url, pool_pre_ping=True)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            response_time = (time.time() - start) * 1000
            return HealthCheck(
                name='database',
                status=HealthStatus.HEALTHY,
                message='Database connection successful',
                response_time=response_time,
                metadata={'url': self.config.database.host}
            )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            logger.error(f"Database health check failed: {e}")
            return HealthCheck(
                name='database',
                status=HealthStatus.UNHEALTHY,
                message=f'Database connection failed: {str(e)}',
                response_time=response_time
            )

    async def _check_redis(self) -> HealthCheck:
        """Check Redis connectivity"""
        start = time.time()
        try:
            client = redis.Redis(
                host=self.config.redis.host,
                port=self.config.redis.port,
                password=self.config.redis.password,
                db=self.config.redis.db,
                socket_connect_timeout=5
            )
            client.ping()
            info = client.info()

            response_time = (time.time() - start) * 1000
            return HealthCheck(
                name='redis',
                status=HealthStatus.HEALTHY,
                message='Redis connection successful',
                response_time=response_time,
                metadata={
                    'connected_clients': info.get('connected_clients'),
                    'used_memory_human': info.get('used_memory_human'),
                }
            )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            logger.error(f"Redis health check failed: {e}")
            return HealthCheck(
                name='redis',
                status=HealthStatus.UNHEALTHY,
                message=f'Redis connection failed: {str(e)}',
                response_time=response_time
            )

    async def _check_system_resources(self) -> HealthCheck:
        """Check overall system resources"""
        start = time.time()
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine status based on thresholds
            status = HealthStatus.HEALTHY
            messages = []

            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                messages.append(f"CPU usage critical: {cpu_percent}%")
            elif cpu_percent > 70:
                status = HealthStatus.DEGRADED
                messages.append(f"CPU usage high: {cpu_percent}%")

            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                messages.append(f"Memory usage critical: {memory.percent}%")
            elif memory.percent > 70:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                messages.append(f"Memory usage high: {memory.percent}%")

            if disk.percent > 90:
                status = HealthStatus.UNHEALTHY
                messages.append(f"Disk usage critical: {disk.percent}%")
            elif disk.percent > 80:
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
                messages.append(f"Disk usage high: {disk.percent}%")

            message = '; '.join(messages) if messages else 'System resources normal'
            response_time = (time.time() - start) * 1000

            return HealthCheck(
                name='system_resources',
                status=status,
                message=message,
                response_time=response_time,
                metadata={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                }
            )
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return HealthCheck(
                name='system_resources',
                status=HealthStatus.UNKNOWN,
                message=f'Failed to check system resources: {str(e)}'
            )

    async def _check_disk_space(self) -> HealthCheck:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            status = HealthStatus.HEALTHY

            if disk.percent > 90:
                status = HealthStatus.UNHEALTHY
            elif disk.percent > 80:
                status = HealthStatus.DEGRADED

            return HealthCheck(
                name='disk_space',
                status=status,
                message=f'Disk usage: {disk.percent}%',
                metadata={
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                }
            )
        except Exception as e:
            return HealthCheck(
                name='disk_space',
                status=HealthStatus.UNKNOWN,
                message=str(e)
            )

    async def _check_memory(self) -> HealthCheck:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            status = HealthStatus.HEALTHY

            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
            elif memory.percent > 70:
                status = HealthStatus.DEGRADED

            return HealthCheck(
                name='memory',
                status=status,
                message=f'Memory usage: {memory.percent}%',
                metadata={
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                }
            )
        except Exception as e:
            return HealthCheck(
                name='memory',
                status=HealthStatus.UNKNOWN,
                message=str(e)
            )

    async def _check_cpu(self) -> HealthCheck:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            status = HealthStatus.HEALTHY

            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
            elif cpu_percent > 70:
                status = HealthStatus.DEGRADED

            return HealthCheck(
                name='cpu',
                status=status,
                message=f'CPU usage: {cpu_percent}%',
                metadata={
                    'percent': cpu_percent,
                    'count': cpu_count,
                }
            )
        except Exception as e:
            return HealthCheck(
                name='cpu',
                status=HealthStatus.UNKNOWN,
                message=str(e)
            )

    async def check_health(self) -> SystemHealth:
        """
        Run all health checks and return system health

        Returns:
            SystemHealth report
        """
        checks = []

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                checks.append(result)

                # Track failures and attempt recovery
                if result.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                    self.failure_counts[name] = self.failure_counts.get(name, 0) + 1

                    # Attempt recovery if handler is registered
                    if name in self.recovery_handlers and self.failure_counts[name] >= 3:
                        logger.warning(f"Attempting recovery for {name}")
                        try:
                            await self.recovery_handlers[name]()
                            self.failure_counts[name] = 0
                        except Exception as e:
                            logger.error(f"Recovery failed for {name}: {e}")
                else:
                    self.failure_counts[name] = 0

            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                checks.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f'Check failed: {str(e)}'
                ))

        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            overall_status = HealthStatus.DEGRADED
        elif all(c.status == HealthStatus.HEALTHY for c in checks):
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN

        uptime = time.time() - self.start_time
        health = SystemHealth(
            status=overall_status,
            checks=checks,
            uptime=uptime
        )

        # Store in history
        self.health_history.append(health)

        return health

    async def start_monitoring(self, interval: int = 30):
        """
        Start continuous health monitoring

        Args:
            interval: Check interval in seconds
        """
        if self._monitoring:
            logger.warning("Monitoring already started")
            return

        self._monitoring = True
        logger.info(f"Starting health monitoring (interval: {interval}s)")

        async def monitor_loop():
            while self._monitoring:
                try:
                    await self.check_health()
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(interval)

        self._monitor_task = asyncio.create_task(monitor_loop())

    async def stop_monitoring(self):
        """Stop continuous health monitoring"""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped health monitoring")

    def get_health_history(self, last_n: Optional[int] = None) -> List[SystemHealth]:
        """
        Get health check history

        Args:
            last_n: Number of recent checks to return (None for all)

        Returns:
            List of SystemHealth reports
        """
        if last_n:
            return list(self.health_history)[-last_n:]
        return list(self.health_history)

    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.start_time

    def get_metrics(self) -> Dict[str, Any]:
        """Get health metrics summary"""
        if not self.health_history:
            return {}

        recent_checks = list(self.health_history)[-10:]

        return {
            'uptime': self.get_uptime(),
            'total_checks': len(self.health_history),
            'recent_status': recent_checks[-1].status.value if recent_checks else 'unknown',
            'failure_counts': dict(self.failure_counts),
            'average_response_times': self._calculate_avg_response_times(recent_checks),
        }

    def _calculate_avg_response_times(self, health_checks: List[SystemHealth]) -> Dict[str, float]:
        """Calculate average response times for each check"""
        response_times: Dict[str, List[float]] = {}

        for health in health_checks:
            for check in health.checks:
                if check.name not in response_times:
                    response_times[check.name] = []
                response_times[check.name].append(check.response_time)

        return {
            name: sum(times) / len(times) if times else 0
            for name, times in response_times.items()
        }
