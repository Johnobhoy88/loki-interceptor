"""
Enhanced health check and readiness probe system
"""
import time
from typing import Dict, Any
from datetime import datetime
import psutil
import os


class HealthChecker:
    """Comprehensive health checking for production deployments"""

    def __init__(self, app=None):
        self.app = app
        self.start_time = time.time()
        self.ready = False
        self.dependencies = {}

    def mark_ready(self):
        """Mark application as ready to receive traffic"""
        self.ready = True

    def mark_not_ready(self):
        """Mark application as not ready (e.g., during graceful shutdown)"""
        self.ready = False

    def register_dependency(self, name: str, check_func: callable):
        """Register a dependency check function"""
        self.dependencies[name] = check_func

    def check_database(self, db_connection) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Try a simple query
            db_connection.execute("SELECT 1")
            return {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }

    def check_redis(self, redis_client) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            redis_client.ping()
            info = redis_client.info()
            return {
                "status": "healthy",
                "message": "Redis connection successful",
                "memory_used": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}"
            }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024)
            }
        except Exception as e:
            return {
                "error": f"Failed to get system metrics: {str(e)}"
            }

    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self.start_time

    def liveness_check(self) -> Dict[str, Any]:
        """
        Liveness probe - Is the application running?
        Used by Kubernetes to restart unhealthy containers
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self.get_uptime()
        }

    def readiness_check(self) -> Dict[str, Any]:
        """
        Readiness probe - Is the application ready to serve traffic?
        Used by Kubernetes to add/remove from load balancer
        """
        if not self.ready:
            return {
                "status": "not_ready",
                "message": "Application is not ready to serve traffic",
                "timestamp": datetime.utcnow().isoformat()
            }

        # Check dependencies
        dependency_statuses = {}
        all_healthy = True

        for name, check_func in self.dependencies.items():
            try:
                result = check_func()
                dependency_statuses[name] = result
                if result.get("status") != "healthy":
                    all_healthy = False
            except Exception as e:
                dependency_statuses[name] = {
                    "status": "error",
                    "message": str(e)
                }
                all_healthy = False

        return {
            "status": "ready" if all_healthy else "degraded",
            "ready": all_healthy,
            "dependencies": dependency_statuses,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self.get_uptime()
        }

    def detailed_health_check(self, engine, cache) -> Dict[str, Any]:
        """
        Detailed health check with all components
        """
        health_data = {
            "status": "healthy" if self.ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self.get_uptime(),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("FLASK_ENV", "production"),

            # Application components
            "modules": {
                "loaded": list(engine.modules.keys()),
                "count": len(engine.modules)
            },

            # Cache stats
            "cache": cache.get_stats() if hasattr(cache, 'get_stats') else {},

            # System metrics
            "system": self.get_system_metrics(),

            # Dependencies
            "dependencies": {}
        }

        # Check all registered dependencies
        for name, check_func in self.dependencies.items():
            try:
                health_data["dependencies"][name] = check_func()
            except Exception as e:
                health_data["dependencies"][name] = {
                    "status": "error",
                    "message": str(e)
                }

        return health_data


# Global health checker instance
health_checker = HealthChecker()
