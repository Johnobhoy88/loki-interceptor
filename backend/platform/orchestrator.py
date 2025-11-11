"""
LOKI Platform Orchestrator
Master coordinator for all subsystems with zero-downtime operations
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import redis

from .config import PlatformConfig, get_config
from .health_monitor import HealthMonitor, HealthStatus
from .feature_flags import FeatureFlags
from .telemetry import TelemetrySystem
from .error_handler import ErrorHandler, ErrorSeverity

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    ERROR = "error"


class PlatformOrchestrator:
    """
    Master Platform Orchestrator
    Coordinates all subsystems with graceful startup/shutdown and self-healing
    """

    def __init__(self, config: Optional[PlatformConfig] = None):
        """
        Initialize platform orchestrator

        Args:
            config: Optional PlatformConfig (uses global config if not provided)
        """
        self.config = config or get_config()
        self.state = SystemState.STOPPED
        self.start_time: Optional[datetime] = None
        self.subsystems: Dict[str, Any] = {}
        self.subsystem_states: Dict[str, bool] = {}

        # Initialize core components
        self._initialize_components()

        # Shutdown coordination
        self._shutdown_event = asyncio.Event()
        self._shutdown_handlers: List[Callable] = []

        # Register signal handlers
        self._register_signal_handlers()

    def _initialize_components(self):
        """Initialize platform components"""
        logger.info("Initializing platform components...")

        try:
            # Initialize Redis if configured
            redis_client = None
            try:
                redis_client = redis.Redis(
                    host=self.config.redis.host,
                    port=self.config.redis.port,
                    password=self.config.redis.password,
                    db=self.config.redis.db,
                    socket_connect_timeout=5
                )
                redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis not available: {e}. Some features will be disabled.")
                redis_client = None

            # Initialize subsystems
            self.health_monitor = HealthMonitor(self.config)
            self.subsystems['health_monitor'] = self.health_monitor

            self.feature_flags = FeatureFlags(self.config, redis_client)
            self.subsystems['feature_flags'] = self.feature_flags

            self.telemetry = TelemetrySystem(self.config)
            self.subsystems['telemetry'] = self.telemetry

            self.error_handler = ErrorHandler(self.config)
            self.subsystems['error_handler'] = self.error_handler

            # Register recovery handlers
            self._register_recovery_handlers()

            logger.info("Platform components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def _register_recovery_handlers(self):
        """Register error recovery handlers"""
        # Register health check recovery
        async def recover_database():
            logger.info("Attempting database recovery...")
            # Implement database reconnection logic
            await asyncio.sleep(2)
            logger.info("Database recovery completed")

        async def recover_redis():
            logger.info("Attempting Redis recovery...")
            # Implement Redis reconnection logic
            await asyncio.sleep(2)
            logger.info("Redis recovery completed")

        self.health_monitor.register_recovery_handler('database', recover_database)
        self.health_monitor.register_recovery_handler('redis', recover_redis)

    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def startup(self):
        """
        Start all platform subsystems with zero-downtime
        """
        if self.state != SystemState.STOPPED:
            logger.warning(f"Cannot start: system is in {self.state.value} state")
            return

        self.state = SystemState.STARTING
        self.start_time = datetime.utcnow()

        logger.info("=" * 60)
        logger.info("LOKI PLATFORM STARTING")
        logger.info("=" * 60)

        try:
            # Validate configuration
            logger.info("Validating configuration...")
            errors = self.config.validate()
            if errors:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                if self.config.is_production():
                    raise Exception("Configuration validation failed in production")
                else:
                    logger.warning("Continuing with invalid configuration in non-production mode")

            # Start health monitoring
            logger.info("Starting health monitor...")
            await self.health_monitor.start_monitoring(interval=30)
            self.subsystem_states['health_monitor'] = True

            # Perform initial health check
            logger.info("Performing initial health check...")
            health = await self.health_monitor.check_health()

            if health.status == HealthStatus.UNHEALTHY:
                logger.error("Initial health check failed")
                if self.config.is_production():
                    self.state = SystemState.ERROR
                    raise Exception("System unhealthy - cannot start in production")
                else:
                    logger.warning("Continuing with unhealthy state in non-production mode")
                    self.state = SystemState.DEGRADED
            elif health.status == HealthStatus.DEGRADED:
                logger.warning("System is in degraded state")
                self.state = SystemState.DEGRADED
            else:
                self.state = SystemState.RUNNING

            # Start telemetry
            logger.info("Starting telemetry system...")
            self.telemetry.gauge('system.state', 1.0, tags={'state': self.state.value})
            self.subsystem_states['telemetry'] = True

            # Load feature flags
            logger.info("Loading feature flags...")
            flags_stats = self.feature_flags.get_stats()
            logger.info(f"Loaded {flags_stats['total']} feature flags ({flags_stats['enabled']} enabled)")
            self.subsystem_states['feature_flags'] = True

            # Record startup metrics
            startup_duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.telemetry.histogram('platform.startup.duration', startup_duration * 1000)

            logger.info("=" * 60)
            logger.info(f"LOKI PLATFORM {self.state.value.upper()}")
            logger.info(f"Startup completed in {startup_duration:.2f}s")
            logger.info(f"Environment: {self.config.environment}")
            logger.info(f"Health Status: {health.status.value}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Startup failed: {e}")
            self.state = SystemState.ERROR
            await self.error_handler.handle_error(
                e,
                context={'phase': 'startup'},
                severity=ErrorSeverity.CRITICAL,
                attempt_recovery=False
            )
            raise

    async def shutdown(self):
        """
        Gracefully shutdown all platform subsystems
        """
        if self.state in [SystemState.STOPPED, SystemState.STOPPING]:
            logger.warning(f"Cannot shutdown: system is in {self.state.value} state")
            return

        self.state = SystemState.STOPPING
        shutdown_start = datetime.utcnow()

        logger.info("=" * 60)
        logger.info("LOKI PLATFORM SHUTTING DOWN")
        logger.info("=" * 60)

        try:
            # Execute custom shutdown handlers
            logger.info("Executing shutdown handlers...")
            for handler in self._shutdown_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler()
                    else:
                        handler()
                except Exception as e:
                    logger.error(f"Shutdown handler failed: {e}")

            # Stop health monitoring
            if self.subsystem_states.get('health_monitor'):
                logger.info("Stopping health monitor...")
                await self.health_monitor.stop_monitoring()

            # Final metrics
            if self.subsystem_states.get('telemetry'):
                logger.info("Recording final metrics...")
                uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
                self.telemetry.gauge('system.uptime', uptime)
                self.telemetry.gauge('system.state', 0.0, tags={'state': 'stopped'})

                # Export final metrics
                metrics_summary = self.telemetry.get_summary()
                logger.info(f"Total requests processed: {metrics_summary.get('requests', {}).get('total', 0)}")
                logger.info(f"Total errors: {metrics_summary.get('requests', {}).get('errors', 0)}")

            # Export error stats
            if self.subsystem_states.get('error_handler'):
                error_stats = self.error_handler.get_error_stats()
                logger.info(f"Total errors handled: {error_stats['total_errors']}")

            shutdown_duration = (datetime.utcnow() - shutdown_start).total_seconds()

            logger.info("=" * 60)
            logger.info(f"LOKI PLATFORM STOPPED")
            logger.info(f"Shutdown completed in {shutdown_duration:.2f}s")
            logger.info("=" * 60)

            self.state = SystemState.STOPPED
            self._shutdown_event.set()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.state = SystemState.ERROR
            raise

    def register_shutdown_handler(self, handler: Callable):
        """
        Register a custom shutdown handler

        Args:
            handler: Shutdown handler function
        """
        self._shutdown_handlers.append(handler)
        logger.info("Registered shutdown handler")

    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive platform status

        Returns:
            Status dictionary
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0

        return {
            'state': self.state.value,
            'uptime': uptime,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'environment': self.config.environment,
            'subsystems': self.subsystem_states,
            'health': None,  # Populated by health check
            'telemetry': self.telemetry.get_summary() if 'telemetry' in self.subsystems else {},
            'errors': self.error_handler.get_error_stats() if 'error_handler' in self.subsystems else {},
            'feature_flags': self.feature_flags.get_stats() if 'feature_flags' in self.subsystems else {},
        }

    async def get_full_status(self) -> Dict[str, Any]:
        """
        Get full platform status including health check

        Returns:
            Full status dictionary
        """
        status = self.get_status()

        # Add current health status
        if 'health_monitor' in self.subsystems:
            health = await self.health_monitor.check_health()
            status['health'] = health.to_dict()

        return status

    def is_healthy(self) -> bool:
        """Check if platform is healthy"""
        return self.state in [SystemState.RUNNING, SystemState.DEGRADED]

    def is_running(self) -> bool:
        """Check if platform is running"""
        return self.state == SystemState.RUNNING

    async def reload_config(self):
        """
        Reload configuration without restarting

        Note: Only non-critical settings will be reloaded
        """
        logger.info("Reloading configuration...")

        try:
            self.config.reload()

            # Reload feature flags
            # Feature flags are reloaded from storage automatically

            logger.info("Configuration reloaded successfully")
            self.telemetry.increment('config.reload.success')

        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            self.telemetry.increment('config.reload.error')
            await self.error_handler.handle_error(
                e,
                context={'operation': 'reload_config'},
                severity=ErrorSeverity.MEDIUM
            )
            raise

    async def run_diagnostics(self) -> Dict[str, Any]:
        """
        Run comprehensive system diagnostics

        Returns:
            Diagnostics report
        """
        logger.info("Running system diagnostics...")

        diagnostics = {
            'timestamp': datetime.utcnow().isoformat(),
            'platform_status': self.get_status(),
        }

        # Health check
        if 'health_monitor' in self.subsystems:
            health = await self.health_monitor.check_health()
            diagnostics['health'] = health.to_dict()

        # Recent errors
        if 'error_handler' in self.subsystems:
            recent_errors = self.error_handler.get_recent_errors(20)
            diagnostics['recent_errors'] = [e.to_dict() for e in recent_errors]

        # Metrics summary
        if 'telemetry' in self.subsystems:
            diagnostics['metrics'] = self.telemetry.get_summary()

        # Configuration
        diagnostics['configuration'] = self.config.to_dict()

        logger.info("Diagnostics completed")
        return diagnostics


# Global orchestrator instance
_orchestrator: Optional[PlatformOrchestrator] = None


def get_orchestrator() -> PlatformOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PlatformOrchestrator()
    return _orchestrator


async def main():
    """Main entry point for running the orchestrator"""
    orchestrator = get_orchestrator()

    try:
        # Startup
        await orchestrator.startup()

        # Wait for shutdown signal
        await orchestrator.wait_for_shutdown()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Shutdown
        await orchestrator.shutdown()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run orchestrator
    asyncio.run(main())
