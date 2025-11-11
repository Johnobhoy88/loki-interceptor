"""
Unified Configuration Management System
Provides centralized configuration for all platform components
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "loki"
    user: str = "loki_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

    @property
    def url(self) -> str:
        """Build database URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl: int = 3600
    max_connections: int = 50

    @property
    def url(self) -> str:
        """Build Redis URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 60
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: int = 100
    rate_limit_period: int = 60


@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 3600
    api_key_header: str = "X-API-Key"
    enable_encryption: bool = True
    encryption_key: str = ""
    enable_audit: bool = True
    enable_rate_limiting: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    metrics_port: int = 9090
    jaeger_endpoint: Optional[str] = None
    sentry_dsn: Optional[str] = None
    datadog_api_key: Optional[str] = None


@dataclass
class ComplianceConfig:
    """Compliance module configuration"""
    enabled_modules: List[str] = field(default_factory=lambda: [
        "fca_uk", "fca_advanced", "gdpr_uk", "gdpr_advanced",
        "tax_uk", "uk_employment", "scottish_law", "hr_scottish"
    ])
    strict_mode: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300
    max_concurrent_checks: int = 10


@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""
    enable_caching: bool = True
    enable_compression: bool = True
    enable_async: bool = True
    max_workers: int = 4
    queue_size: int = 1000
    batch_size: int = 100
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class FeatureFlagsConfig:
    """Feature flags configuration"""
    storage_backend: str = "redis"
    refresh_interval: int = 60
    default_enabled: bool = False
    enable_gradual_rollout: bool = True


class PlatformConfig:
    """
    Unified Platform Configuration Manager
    Provides centralized configuration with environment variable overrides
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_file: Optional path to YAML config file
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._loaded_at: Optional[datetime] = None

        # Initialize component configs
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.compliance = ComplianceConfig()
        self.performance = PerformanceConfig()
        self.feature_flags = FeatureFlagsConfig()

        self.load()

    def load(self):
        """Load configuration from file and environment"""
        # Load from file if provided
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file(self.config_file)

        # Override with environment variables
        self._load_from_env()

        self._loaded_at = datetime.utcnow()
        logger.info(f"Configuration loaded at {self._loaded_at}")

    def _load_from_file(self, config_file: str):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            if config:
                self._config.update(config)
                self._apply_config(config)
                logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Database
        self.database.host = os.getenv('DB_HOST', self.database.host)
        self.database.port = int(os.getenv('DB_PORT', self.database.port))
        self.database.name = os.getenv('DB_NAME', self.database.name)
        self.database.user = os.getenv('DB_USER', self.database.user)
        self.database.password = os.getenv('DB_PASSWORD', self.database.password)
        self.database.pool_size = int(os.getenv('DB_POOL_SIZE', self.database.pool_size))

        # Redis
        self.redis.host = os.getenv('REDIS_HOST', self.redis.host)
        self.redis.port = int(os.getenv('REDIS_PORT', self.redis.port))
        self.redis.password = os.getenv('REDIS_PASSWORD', self.redis.password)

        # API
        self.api.host = os.getenv('API_HOST', self.api.host)
        self.api.port = int(os.getenv('API_PORT', self.api.port))
        self.api.workers = int(os.getenv('API_WORKERS', self.api.workers))

        # Security
        self.security.jwt_secret = os.getenv('JWT_SECRET', self.security.jwt_secret)
        self.security.encryption_key = os.getenv('ENCRYPTION_KEY', self.security.encryption_key)
        self.security.api_key_header = os.getenv('API_KEY_HEADER', self.security.api_key_header)

        # Monitoring
        self.monitoring.log_level = os.getenv('LOG_LEVEL', self.monitoring.log_level)
        self.monitoring.jaeger_endpoint = os.getenv('JAEGER_ENDPOINT', self.monitoring.jaeger_endpoint)
        self.monitoring.sentry_dsn = os.getenv('SENTRY_DSN', self.monitoring.sentry_dsn)
        self.monitoring.datadog_api_key = os.getenv('DATADOG_API_KEY', self.monitoring.datadog_api_key)

        # Environment
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

    def _apply_config(self, config: Dict[str, Any]):
        """Apply configuration from dictionary"""
        if 'database' in config:
            for key, value in config['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)

        if 'redis' in config:
            for key, value in config['redis'].items():
                if hasattr(self.redis, key):
                    setattr(self.redis, key, value)

        if 'api' in config:
            for key, value in config['api'].items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)

        if 'security' in config:
            for key, value in config['security'].items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)

        if 'monitoring' in config:
            for key, value in config['monitoring'].items():
                if hasattr(self.monitoring, key):
                    setattr(self.monitoring, key, value)

        if 'compliance' in config:
            for key, value in config['compliance'].items():
                if hasattr(self.compliance, key):
                    setattr(self.compliance, key, value)

        if 'performance' in config:
            for key, value in config['performance'].items():
                if hasattr(self.performance, key):
                    setattr(self.performance, key, value)

    def reload(self):
        """Reload configuration"""
        logger.info("Reloading configuration")
        self.load()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'pool_size': self.database.pool_size,
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db,
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'workers': self.api.workers,
            },
            'security': {
                'enable_encryption': self.security.enable_encryption,
                'enable_audit': self.security.enable_audit,
                'enable_rate_limiting': self.security.enable_rate_limiting,
            },
            'monitoring': {
                'enable_metrics': self.monitoring.enable_metrics,
                'enable_tracing': self.monitoring.enable_tracing,
                'log_level': self.monitoring.log_level,
            },
            'compliance': {
                'enabled_modules': self.compliance.enabled_modules,
                'strict_mode': self.compliance.strict_mode,
            },
            'performance': {
                'enable_caching': self.performance.enable_caching,
                'enable_async': self.performance.enable_async,
            },
            'environment': self.environment,
            'loaded_at': self._loaded_at.isoformat() if self._loaded_at else None,
        }

    def validate(self) -> List[str]:
        """
        Validate configuration
        Returns list of validation errors
        """
        errors = []

        # Validate required security settings
        if not self.security.jwt_secret:
            errors.append("JWT_SECRET is required")

        if self.security.enable_encryption and not self.security.encryption_key:
            errors.append("ENCRYPTION_KEY is required when encryption is enabled")

        # Validate database config
        if not self.database.password:
            errors.append("Database password is required")

        # Validate performance settings
        if self.performance.max_workers < 1:
            errors.append("max_workers must be at least 1")

        if self.performance.queue_size < 1:
            errors.append("queue_size must be at least 1")

        return errors

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == 'production'

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == 'development'


# Global configuration instance
_config: Optional[PlatformConfig] = None


def get_config() -> PlatformConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        # Look for config file in standard locations
        config_file = None
        for path in [
            '/etc/loki/config.yml',
            '/home/user/loki-interceptor/configs/platform.yml',
            os.getenv('LOKI_CONFIG_FILE'),
        ]:
            if path and Path(path).exists():
                config_file = path
                break

        _config = PlatformConfig(config_file)

    return _config


def reset_config():
    """Reset global configuration (mainly for testing)"""
    global _config
    _config = None
