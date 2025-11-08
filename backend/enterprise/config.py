"""
Configuration management for LOKI Enterprise.

Loads configuration from environment variables with sensible defaults.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load from environment variables."""
        return cls(
            url=os.getenv('DATABASE_URL', 'postgresql://localhost:5432/loki_db'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
        )


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str
    max_connections: int = 50
    decode_responses: bool = True

    @classmethod
    def from_env(cls) -> 'RedisConfig':
        """Load from environment variables."""
        return cls(
            url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
            max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', '50')),
            decode_responses=os.getenv('REDIS_DECODE_RESPONSES', 'true').lower() == 'true',
        )


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    api_secret_key: str = None
    session_expire_hours: int = 24
    csrf_token_expire_seconds: int = 3600
    max_request_age_seconds: int = 300

    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Load from environment variables."""
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret:
            raise ValueError("JWT_SECRET_KEY environment variable is required")

        return cls(
            jwt_secret_key=jwt_secret,
            jwt_algorithm=os.getenv('JWT_ALGORITHM', 'HS256'),
            access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30')),
            refresh_token_expire_days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7')),
            api_secret_key=os.getenv('API_SECRET_KEY', jwt_secret),
            session_expire_hours=int(os.getenv('SESSION_EXPIRE_HOURS', '24')),
            csrf_token_expire_seconds=int(os.getenv('CSRF_TOKEN_EXPIRE_SECONDS', '3600')),
            max_request_age_seconds=int(os.getenv('MAX_REQUEST_AGE_SECONDS', '300')),
        )


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    enabled: bool = True
    strategy: str = 'sliding_window'

    # Tier-based limits (requests per hour)
    free_tier_limit: int = 100
    starter_tier_limit: int = 1000
    professional_tier_limit: int = 10000
    enterprise_tier_limit: int = 100000

    @classmethod
    def from_env(cls) -> 'RateLimitConfig':
        """Load from environment variables."""
        return cls(
            enabled=os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true',
            strategy=os.getenv('RATE_LIMIT_STRATEGY', 'sliding_window'),
            free_tier_limit=int(os.getenv('RATE_LIMIT_FREE', '100')),
            starter_tier_limit=int(os.getenv('RATE_LIMIT_STARTER', '1000')),
            professional_tier_limit=int(os.getenv('RATE_LIMIT_PROFESSIONAL', '10000')),
            enterprise_tier_limit=int(os.getenv('RATE_LIMIT_ENTERPRISE', '100000')),
        )


@dataclass
class AuditConfig:
    """Audit logging configuration."""
    enabled: bool = True
    retention_days: int = 365
    log_to_console: bool = True
    log_to_file: bool = True
    log_file_path: str = '/var/log/loki/audit.log'

    @classmethod
    def from_env(cls) -> 'AuditConfig':
        """Load from environment variables."""
        return cls(
            enabled=os.getenv('AUDIT_ENABLED', 'true').lower() == 'true',
            retention_days=int(os.getenv('AUDIT_RETENTION_DAYS', '365')),
            log_to_console=os.getenv('AUDIT_LOG_CONSOLE', 'true').lower() == 'true',
            log_to_file=os.getenv('AUDIT_LOG_FILE', 'true').lower() == 'true',
            log_file_path=os.getenv('AUDIT_LOG_PATH', '/var/log/loki/audit.log'),
        )


@dataclass
class OAuth2Config:
    """OAuth2 provider configuration."""
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'OAuth2Config':
        """Load from environment variables."""
        return cls(
            google_client_id=os.getenv('GOOGLE_CLIENT_ID'),
            google_client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            microsoft_client_id=os.getenv('MICROSOFT_CLIENT_ID'),
            microsoft_client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
            github_client_id=os.getenv('GITHUB_CLIENT_ID'),
            github_client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        )


@dataclass
class EnterpriseConfig:
    """Complete enterprise configuration."""
    environment: str
    debug: bool
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    rate_limit: RateLimitConfig
    audit: AuditConfig
    oauth2: OAuth2Config

    @classmethod
    def from_env(cls) -> 'EnterpriseConfig':
        """Load complete configuration from environment."""
        return cls(
            environment=os.getenv('ENVIRONMENT', 'development'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            database=DatabaseConfig.from_env(),
            redis=RedisConfig.from_env(),
            security=SecurityConfig.from_env(),
            rate_limit=RateLimitConfig.from_env(),
            audit=AuditConfig.from_env(),
            oauth2=OAuth2Config.from_env(),
        )

    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == 'production'

    def validate(self) -> None:
        """Validate configuration."""
        errors = []

        # Check required settings
        if not self.security.jwt_secret_key:
            errors.append("JWT_SECRET_KEY is required")

        if self.is_production():
            if self.debug:
                errors.append("DEBUG mode should be disabled in production")

            if 'localhost' in self.database.url:
                errors.append("Production should not use localhost database")

            if len(self.security.jwt_secret_key) < 32:
                errors.append("JWT_SECRET_KEY should be at least 32 characters in production")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Global configuration instance
config: Optional[EnterpriseConfig] = None


def load_config() -> EnterpriseConfig:
    """
    Load and validate configuration.

    Returns:
        EnterpriseConfig instance

    Raises:
        ValueError: If configuration is invalid
    """
    global config

    if config is None:
        config = EnterpriseConfig.from_env()
        config.validate()

    return config


def get_config() -> EnterpriseConfig:
    """
    Get current configuration (load if not already loaded).

    Returns:
        EnterpriseConfig instance
    """
    if config is None:
        return load_config()
    return config


# Example .env file template
ENV_TEMPLATE = """
# LOKI Enterprise Configuration
# Copy this to .env and fill in your values

# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/loki_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_DECODE_RESPONSES=true

# Security
JWT_SECRET_KEY=your-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
API_SECRET_KEY=your-api-secret-key
SESSION_EXPIRE_HOURS=24
CSRF_TOKEN_EXPIRE_SECONDS=3600
MAX_REQUEST_AGE_SECONDS=300

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STRATEGY=sliding_window
RATE_LIMIT_FREE=100
RATE_LIMIT_STARTER=1000
RATE_LIMIT_PROFESSIONAL=10000
RATE_LIMIT_ENTERPRISE=100000

# Audit Logging
AUDIT_ENABLED=true
AUDIT_RETENTION_DAYS=365
AUDIT_LOG_CONSOLE=true
AUDIT_LOG_FILE=true
AUDIT_LOG_PATH=/var/log/loki/audit.log

# OAuth2 (Optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
"""


if __name__ == '__main__':
    # Generate .env template
    print("LOKI Enterprise Configuration Template")
    print("=" * 50)
    print(ENV_TEMPLATE)

    # Try to load and validate config
    try:
        cfg = load_config()
        print("\nConfiguration loaded successfully!")
        print(f"Environment: {cfg.environment}")
        print(f"Database: {cfg.database.url}")
        print(f"Redis: {cfg.redis.url}")
    except Exception as e:
        print(f"\nConfiguration error: {e}")
        print("\nPlease create a .env file with the required settings.")
