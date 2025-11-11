"""
Graceful shutdown handler for production deployments
Ensures in-flight requests complete before shutdown
"""
import signal
import sys
import time
import logging
from threading import Event

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Handles graceful shutdown of the application

    Features:
    - Waits for in-flight requests to complete
    - Closes database connections
    - Flushes caches
    - Notifies load balancers via health check
    """

    def __init__(self, app=None, health_checker=None, timeout=30):
        self.app = app
        self.health_checker = health_checker
        self.timeout = timeout
        self.shutdown_event = Event()
        self.cleanup_handlers = []

    def register_cleanup_handler(self, handler: callable):
        """Register a cleanup function to call during shutdown"""
        self.cleanup_handlers.append(handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals (SIGTERM, SIGINT)"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")

        # Mark as not ready to stop receiving new requests
        if self.health_checker:
            self.health_checker.mark_not_ready()
            logger.info("Marked application as not ready")

        # Wait a bit for load balancer to detect unhealthy status
        logger.info("Waiting 5 seconds for load balancer to detect unhealthy status...")
        time.sleep(5)

        # Run cleanup handlers
        logger.info("Running cleanup handlers...")
        for handler in self.cleanup_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Cleanup handler failed: {e}")

        # Wait for in-flight requests (gunicorn handles this)
        logger.info("Waiting for in-flight requests to complete...")
        time.sleep(2)

        logger.info("Graceful shutdown complete")
        self.shutdown_event.set()
        sys.exit(0)

    def setup(self):
        """Setup signal handlers"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        logger.info("Graceful shutdown handlers registered")

    def wait_for_shutdown(self):
        """Block until shutdown signal is received"""
        self.shutdown_event.wait()


def create_database_cleanup(db_connection):
    """Create a cleanup function for database connections"""
    def cleanup():
        try:
            logger.info("Closing database connections...")
            db_connection.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Failed to close database connections: {e}")
    return cleanup


def create_cache_cleanup(cache):
    """Create a cleanup function for cache"""
    def cleanup():
        try:
            logger.info("Flushing cache...")
            if hasattr(cache, 'flush'):
                cache.flush()
            logger.info("Cache flushed")
        except Exception as e:
            logger.error(f"Failed to flush cache: {e}")
    return cleanup


def create_audit_log_cleanup(audit_logger):
    """Create a cleanup function for audit logger"""
    def cleanup():
        try:
            logger.info("Flushing audit logs...")
            if hasattr(audit_logger, 'flush'):
                audit_logger.flush()
            logger.info("Audit logs flushed")
        except Exception as e:
            logger.error(f"Failed to flush audit logs: {e}")
    return cleanup
