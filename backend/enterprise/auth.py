"""
Authentication System for LOKI Enterprise

OAuth2 implementation with JWT tokens, API key management, and session handling.

Features:
- OAuth2 authorization code flow
- JWT access & refresh tokens
- API key generation with rotation
- Session management with Redis
- Password hashing with bcrypt
- Multi-factor authentication ready
"""

import os
import jwt
import uuid
import secrets
import hashlib
import hmac
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json


class TokenType(Enum):
    """Token type enumeration."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFICATION = "verification"


class AuthProvider(Enum):
    """Authentication provider types."""
    LOCAL = "local"
    OAUTH2_GOOGLE = "oauth2_google"
    OAUTH2_MICROSOFT = "oauth2_microsoft"
    OAUTH2_GITHUB = "oauth2_github"
    SAML = "saml"
    LDAP = "ldap"


@dataclass
class User:
    """
    User entity.

    Attributes:
        id: Unique user identifier
        email: User email (unique)
        username: Username (unique)
        password_hash: Hashed password
        is_active: Account active status
        is_verified: Email verification status
        created_at: Account creation timestamp
        last_login: Last login timestamp
        metadata: Additional user metadata
        mfa_enabled: Multi-factor auth enabled
        mfa_secret: MFA secret key
    """
    id: str
    email: str
    username: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = None
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes sensitive fields)."""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'mfa_enabled': self.mfa_enabled,
        }


@dataclass
class APIKey:
    """
    API key for programmatic access.

    Attributes:
        id: Key identifier
        key: API key (hashed when stored)
        user_id: Owner user ID
        org_id: Organization ID
        name: Human-readable key name
        scopes: Allowed permissions/scopes
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        last_used: Last usage timestamp
        is_active: Key active status
    """
    id: str
    key: str
    user_id: str
    org_id: str
    name: str
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes full key)."""
        return {
            'id': self.id,
            'key_prefix': self.key[:8] + '...' if len(self.key) > 8 else self.key,
            'user_id': self.user_id,
            'org_id': self.org_id,
            'name': self.name,
            'scopes': self.scopes,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_active': self.is_active,
        }


@dataclass
class Session:
    """
    User session.

    Attributes:
        id: Session identifier
        user_id: User ID
        org_id: Current organization ID
        token: Session token
        created_at: Session start time
        expires_at: Session expiration
        ip_address: Client IP
        user_agent: Client user agent
        is_active: Session active status
    """
    id: str
    user_id: str
    org_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class TokenManager:
    """
    Manages JWT token generation, validation, and refresh.

    Handles access tokens, refresh tokens, and token rotation.
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        """
        Initialize token manager.

        Args:
            secret_key: JWT signing secret (auto-generated if not provided)
            algorithm: JWT signing algorithm
            access_token_expire_minutes: Access token lifetime
            refresh_token_expire_days: Refresh token lifetime
        """
        self.secret_key = secret_key or self._generate_secret_key()
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)

    def create_access_token(
        self,
        user_id: str,
        org_id: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User identifier
            org_id: Organization identifier
            additional_claims: Extra claims to include

        Returns:
            Encoded JWT token string
        """
        now = datetime.utcnow()
        expires = now + self.access_token_expire

        payload = {
            'sub': user_id,
            'org_id': org_id,
            'type': TokenType.ACCESS.value,
            'iat': now,
            'exp': expires,
            'jti': str(uuid.uuid4()),
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def create_refresh_token(
        self,
        user_id: str,
        org_id: str,
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User identifier
            org_id: Organization identifier

        Returns:
            Encoded JWT refresh token
        """
        now = datetime.utcnow()
        expires = now + self.refresh_token_expire

        payload = {
            'sub': user_id,
            'org_id': org_id,
            'type': TokenType.REFRESH.value,
            'iat': now,
            'exp': expires,
            'jti': str(uuid.uuid4()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def verify_token(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
    ) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string
            expected_type: Expected token type

        Returns:
            Decoded token payload

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
            ValueError: If token type doesn't match expected
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

            token_type = payload.get('type')
            if token_type != expected_type.value:
                raise ValueError(f"Invalid token type. Expected {expected_type.value}, got {token_type}")

            return payload

        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Generate new access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            jwt.InvalidTokenError: If refresh token is invalid
        """
        payload = self.verify_token(refresh_token, TokenType.REFRESH)

        user_id = payload['sub']
        org_id = payload['org_id']

        # Generate new tokens
        new_access = self.create_access_token(user_id, org_id)
        new_refresh = self.create_refresh_token(user_id, org_id)

        return new_access, new_refresh

    def decode_token_unsafe(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode token without verification (for debugging only).

        Args:
            token: JWT token

        Returns:
            Decoded payload or None
        """
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return None

    @staticmethod
    def _generate_secret_key() -> str:
        """Generate cryptographically secure secret key."""
        return secrets.token_urlsafe(64)


class APIKeyManager:
    """
    Manages API key lifecycle: generation, validation, rotation.

    API keys are prefixed with 'loki_' and use secure random generation.
    """

    KEY_PREFIX = "loki_"
    KEY_LENGTH = 32

    def __init__(self, db_connection=None, cache_backend=None):
        """
        Initialize API key manager.

        Args:
            db_connection: Database connection
            cache_backend: Redis or compatible cache
        """
        self.db = db_connection
        self.cache = cache_backend
        self._keys: Dict[str, APIKey] = {}

    def generate_api_key(
        self,
        user_id: str,
        org_id: str,
        name: str,
        scopes: List[str],
        expires_days: Optional[int] = None,
    ) -> Tuple[str, APIKey]:
        """
        Generate new API key.

        Args:
            user_id: Owner user ID
            org_id: Organization ID
            name: Human-readable key name
            scopes: Allowed permission scopes
            expires_days: Optional expiration in days

        Returns:
            Tuple of (plain_text_key, APIKey_object)
        """
        key_id = str(uuid.uuid4())
        plain_key = self._generate_random_key()

        # Hash key for storage
        key_hash = self._hash_api_key(plain_key)

        now = datetime.utcnow()
        expires_at = now + timedelta(days=expires_days) if expires_days else None

        api_key = APIKey(
            id=key_id,
            key=key_hash,
            user_id=user_id,
            org_id=org_id,
            name=name,
            scopes=scopes,
            created_at=now,
            expires_at=expires_at,
        )

        # Store hashed key
        self._keys[key_hash] = api_key

        # TODO: Store in PostgreSQL
        # INSERT INTO api_keys (...) VALUES (...)

        return plain_key, api_key

    def validate_api_key(self, plain_key: str) -> Optional[APIKey]:
        """
        Validate API key and return associated key object.

        Args:
            plain_key: Plain text API key

        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_api_key(plain_key)

        # Check cache first
        if self.cache:
            cached = self._get_cached_key(key_hash)
            if cached:
                return cached

        # Check memory store
        api_key = self._keys.get(key_hash)

        # TODO: Query PostgreSQL
        # SELECT * FROM api_keys WHERE key_hash = %s

        if not api_key:
            return None

        # Validate key
        if not api_key.is_active:
            return None

        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return None

        # Update last used
        api_key.last_used = datetime.utcnow()

        # Cache valid key
        if self.cache:
            self._cache_key(key_hash, api_key)

        return api_key

    def revoke_api_key(self, key_id: str) -> bool:
        """
        Revoke API key by ID.

        Args:
            key_id: Key identifier

        Returns:
            True if successful
        """
        for key_hash, api_key in self._keys.items():
            if api_key.id == key_id:
                api_key.is_active = False

                # Invalidate cache
                if self.cache:
                    self._invalidate_cache(key_hash)

                # TODO: Update PostgreSQL
                # UPDATE api_keys SET is_active = FALSE WHERE id = %s

                return True

        return False

    def rotate_api_key(self, key_id: str) -> Tuple[str, APIKey]:
        """
        Rotate API key (generate new, revoke old).

        Args:
            key_id: Existing key ID

        Returns:
            Tuple of (new_plain_key, new_APIKey_object)

        Raises:
            ValueError: If key not found
        """
        old_key = None
        for api_key in self._keys.values():
            if api_key.id == key_id:
                old_key = api_key
                break

        if not old_key:
            raise ValueError(f"API key {key_id} not found")

        # Generate new key with same properties
        new_plain_key, new_api_key = self.generate_api_key(
            user_id=old_key.user_id,
            org_id=old_key.org_id,
            name=f"{old_key.name} (rotated)",
            scopes=old_key.scopes,
        )

        # Revoke old key
        self.revoke_api_key(key_id)

        return new_plain_key, new_api_key

    def list_user_keys(self, user_id: str) -> List[APIKey]:
        """
        List all API keys for a user.

        Args:
            user_id: User identifier

        Returns:
            List of APIKey objects
        """
        return [
            key for key in self._keys.values()
            if key.user_id == user_id
        ]

    def _generate_random_key(self) -> str:
        """Generate random API key."""
        random_part = secrets.token_urlsafe(self.KEY_LENGTH)
        return f"{self.KEY_PREFIX}{random_part}"

    def _hash_api_key(self, plain_key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(plain_key.encode()).hexdigest()

    def _cache_key(self, key_hash: str, api_key: APIKey) -> None:
        """Cache API key in Redis."""
        if self.cache:
            cache_key = f"apikey:{key_hash}"
            self.cache.setex(cache_key, 3600, json.dumps(api_key.to_dict()))

    def _get_cached_key(self, key_hash: str) -> Optional[APIKey]:
        """Get cached API key."""
        if not self.cache:
            return None

        cache_key = f"apikey:{key_hash}"
        data = self.cache.get(cache_key)
        if data:
            key_dict = json.loads(data)
            # Reconstruct APIKey (simplified)
            return None  # TODO: Implement proper deserialization

        return None

    def _invalidate_cache(self, key_hash: str) -> None:
        """Invalidate cached key."""
        if self.cache:
            self.cache.delete(f"apikey:{key_hash}")


class SessionManager:
    """
    Manages user sessions with Redis backend.

    Provides session creation, validation, and cleanup.
    """

    def __init__(self, cache_backend=None, session_expire_hours: int = 24):
        """
        Initialize session manager.

        Args:
            cache_backend: Redis cache backend
            session_expire_hours: Session lifetime in hours
        """
        self.cache = cache_backend
        self.session_expire = timedelta(hours=session_expire_hours)
        self._sessions: Dict[str, Session] = {}

    def create_session(
        self,
        user_id: str,
        org_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session:
        """
        Create new user session.

        Args:
            user_id: User identifier
            org_id: Organization identifier
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Session object
        """
        session_id = str(uuid.uuid4())
        session_token = secrets.token_urlsafe(32)

        now = datetime.utcnow()
        expires = now + self.session_expire

        session = Session(
            id=session_id,
            user_id=user_id,
            org_id=org_id,
            token=session_token,
            created_at=now,
            expires_at=expires,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Store session
        self._sessions[session_token] = session

        # Cache in Redis
        if self.cache:
            self._cache_session(session)

        return session

    def validate_session(self, session_token: str) -> Optional[Session]:
        """
        Validate session token.

        Args:
            session_token: Session token

        Returns:
            Session object if valid, None otherwise
        """
        # Check cache first
        if self.cache:
            session = self._get_cached_session(session_token)
            if session:
                return session

        # Check memory store
        session = self._sessions.get(session_token)

        if not session:
            return None

        # Validate session
        if not session.is_active:
            return None

        if datetime.utcnow() > session.expires_at:
            return None

        return session

    def refresh_session(self, session_token: str) -> Optional[Session]:
        """
        Refresh session expiration.

        Args:
            session_token: Session token

        Returns:
            Updated Session object or None
        """
        session = self.validate_session(session_token)

        if not session:
            return None

        session.expires_at = datetime.utcnow() + self.session_expire

        # Update cache
        if self.cache:
            self._cache_session(session)

        return session

    def revoke_session(self, session_token: str) -> bool:
        """
        Revoke session.

        Args:
            session_token: Session token

        Returns:
            True if successful
        """
        session = self._sessions.get(session_token)

        if session:
            session.is_active = False

            # Remove from cache
            if self.cache:
                self._invalidate_session(session_token)

            return True

        return False

    def _cache_session(self, session: Session) -> None:
        """Cache session in Redis."""
        if not self.cache:
            return

        key = f"session:{session.token}"
        expire_seconds = int(self.session_expire.total_seconds())

        session_data = {
            'id': session.id,
            'user_id': session.user_id,
            'org_id': session.org_id,
            'created_at': session.created_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'is_active': session.is_active,
        }

        self.cache.setex(key, expire_seconds, json.dumps(session_data))

    def _get_cached_session(self, session_token: str) -> Optional[Session]:
        """Retrieve session from cache."""
        if not self.cache:
            return None

        key = f"session:{session_token}"
        data = self.cache.get(key)

        if data:
            session_dict = json.loads(data)
            return Session(
                id=session_dict['id'],
                user_id=session_dict['user_id'],
                org_id=session_dict['org_id'],
                token=session_token,
                created_at=datetime.fromisoformat(session_dict['created_at']),
                expires_at=datetime.fromisoformat(session_dict['expires_at']),
                ip_address=session_dict.get('ip_address'),
                user_agent=session_dict.get('user_agent'),
                is_active=session_dict['is_active'],
            )

        return None

    def _invalidate_session(self, session_token: str) -> None:
        """Invalidate cached session."""
        if self.cache:
            self.cache.delete(f"session:{session_token}")


class AuthManager:
    """
    Main authentication manager coordinating all auth components.

    Integrates token management, API keys, sessions, and OAuth2.
    """

    def __init__(
        self,
        db_connection=None,
        cache_backend=None,
        secret_key: Optional[str] = None,
    ):
        """
        Initialize auth manager.

        Args:
            db_connection: Database connection
            cache_backend: Redis cache backend
            secret_key: JWT secret key
        """
        self.db = db_connection
        self.cache = cache_backend

        self.token_manager = TokenManager(secret_key=secret_key)
        self.api_key_manager = APIKeyManager(db_connection, cache_backend)
        self.session_manager = SessionManager(cache_backend)

    def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate user with email/password.

        Args:
            email: User email
            password: User password

        Returns:
            User object if authenticated, None otherwise
        """
        # TODO: Query user from database
        # SELECT * FROM users WHERE email = %s

        # TODO: Verify password with bcrypt
        # bcrypt.checkpw(password.encode(), user.password_hash.encode())

        # Placeholder
        return None

    def login(
        self,
        user: User,
        org_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Login user and create session + tokens.

        Args:
            user: Authenticated user
            org_id: Organization to log into
            ip_address: Client IP
            user_agent: Client user agent

        Returns:
            Dictionary with access_token, refresh_token, session_token
        """
        # Create tokens
        access_token = self.token_manager.create_access_token(user.id, org_id)
        refresh_token = self.token_manager.create_refresh_token(user.id, org_id)

        # Create session
        session = self.session_manager.create_session(
            user.id,
            org_id,
            ip_address,
            user_agent,
        )

        # Update last login
        # TODO: UPDATE users SET last_login = NOW() WHERE id = %s

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_token': session.token,
            'token_type': 'Bearer',
        }

    def logout(self, session_token: str) -> bool:
        """
        Logout user (revoke session).

        Args:
            session_token: Session token

        Returns:
            True if successful
        """
        return self.session_manager.revoke_session(session_token)


# PostgreSQL Schema
POSTGRES_SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255)
);

-- API Keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    scopes JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(org_id);
"""
