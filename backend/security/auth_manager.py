"""
API Key Management and Secure Credential Storage

Enterprise security features:
- Automatic API key rotation
- Secure credential encryption
- Key expiration and revocation
- Audit trail for key usage
- Multi-environment key management
- Secret scanning prevention
"""

import os
import secrets
import hashlib
import hmac
import json
import base64
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class KeyStatus(Enum):
    """API key status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ROTATED = "rotated"
    PENDING = "pending"


class RotationPolicy(Enum):
    """Key rotation policies."""
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    MANUAL = "manual"


@dataclass
class APIKey:
    """
    API key entity.

    Attributes:
        key_id: Unique key identifier
        key_hash: Hashed key (never store plain key!)
        name: Human-readable name
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        last_used: Last usage timestamp
        status: Key status
        scopes: Allowed permissions
        rotation_policy: Rotation policy
        metadata: Additional metadata
    """
    key_id: str
    key_hash: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    status: KeyStatus
    scopes: List[str]
    rotation_policy: RotationPolicy
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (safe for API responses)."""
        return {
            'key_id': self.key_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'status': self.status.value,
            'scopes': self.scopes,
            'rotation_policy': self.rotation_policy.value,
            'days_until_expiration': self._days_until_expiration(),
        }

    def _days_until_expiration(self) -> Optional[int]:
        """Calculate days until expiration."""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def is_expired(self) -> bool:
        """Check if key is expired."""
        if self.status in [KeyStatus.EXPIRED, KeyStatus.REVOKED]:
            return True
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    def needs_rotation(self) -> bool:
        """Check if key needs rotation based on policy."""
        if self.rotation_policy == RotationPolicy.NEVER:
            return False
        if self.rotation_policy == RotationPolicy.MANUAL:
            return False

        rotation_intervals = {
            RotationPolicy.DAILY: 1,
            RotationPolicy.WEEKLY: 7,
            RotationPolicy.MONTHLY: 30,
            RotationPolicy.QUARTERLY: 90,
        }

        interval = rotation_intervals.get(self.rotation_policy)
        if not interval:
            return False

        age = (datetime.utcnow() - self.created_at).days
        return age >= interval


class SecureCredentialStore:
    """
    Secure credential storage with encryption.

    Uses Fernet (symmetric encryption) to store sensitive data.
    """

    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize credential store.

        Args:
            master_key: Master encryption key (generated if not provided)
        """
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = self._generate_master_key()

        self.fernet = Fernet(self._derive_key(self.master_key))

    def _generate_master_key(self) -> bytes:
        """Generate a secure master key."""
        return Fernet.generate_key()

    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: Master password
            salt: Salt for key derivation

        Returns:
            Derived key suitable for Fernet
        """
        if salt is None:
            salt = b'loki_interceptor_v1'  # Static salt for deterministic key

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data.

        Args:
            data: Plain text data

        Returns:
            Encrypted data (base64 encoded)
        """
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Plain text data
        """
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode('utf-8')

    def store_credential(
        self,
        key: str,
        value: str,
        storage_backend: Optional[Dict] = None,
    ) -> bool:
        """
        Store encrypted credential.

        Args:
            key: Credential key/name
            value: Credential value (will be encrypted)
            storage_backend: Storage dict (in-memory if not provided)

        Returns:
            True if successful
        """
        encrypted_value = self.encrypt(value)

        if storage_backend is not None:
            storage_backend[key] = encrypted_value
        else:
            # Store in environment variable (not recommended for production)
            os.environ[f"ENCRYPTED_{key}"] = encrypted_value

        return True

    def retrieve_credential(
        self,
        key: str,
        storage_backend: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        Retrieve and decrypt credential.

        Args:
            key: Credential key/name
            storage_backend: Storage dict

        Returns:
            Decrypted credential value or None
        """
        encrypted_value = None

        if storage_backend is not None:
            encrypted_value = storage_backend.get(key)
        else:
            encrypted_value = os.environ.get(f"ENCRYPTED_{key}")

        if not encrypted_value:
            return None

        try:
            return self.decrypt(encrypted_value)
        except Exception:
            return None


@dataclass
class APIKeyRotationPolicy:
    """
    API key rotation policy configuration.

    Attributes:
        enabled: Whether automatic rotation is enabled
        interval_days: Rotation interval in days
        grace_period_days: Grace period before old key is revoked
        notify_days_before: Send notification N days before rotation
        auto_rotate: Automatically rotate or require manual approval
    """
    enabled: bool = True
    interval_days: int = 90
    grace_period_days: int = 7
    notify_days_before: int = 14
    auto_rotate: bool = False


class APIKeyManager:
    """
    API key lifecycle management.

    Features:
    - Key generation with cryptographically secure random
    - Automatic rotation based on policy
    - Key revocation and expiration
    - Usage tracking
    - Scope-based permissions
    """

    KEY_PREFIX = "loki_"
    KEY_LENGTH = 32  # Characters in random part
    HASH_ALGORITHM = "sha256"

    def __init__(
        self,
        credential_store: Optional[SecureCredentialStore] = None,
        storage_backend: Optional[Dict] = None,
    ):
        """
        Initialize API key manager.

        Args:
            credential_store: Secure credential store
            storage_backend: Storage for keys (in-memory dict or database)
        """
        self.credential_store = credential_store or SecureCredentialStore()
        self.storage = storage_backend or {}
        self.usage_log: List[Dict[str, Any]] = []

    def generate_key(
        self,
        name: str,
        scopes: List[str],
        expires_in_days: Optional[int] = 365,
        rotation_policy: RotationPolicy = RotationPolicy.QUARTERLY,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, APIKey]:
        """
        Generate new API key.

        Args:
            name: Human-readable key name
            scopes: Permission scopes
            expires_in_days: Expiration period (None for no expiration)
            rotation_policy: Rotation policy
            metadata: Additional metadata

        Returns:
            Tuple of (plain_text_key, APIKey_object)
        """
        # Generate random key
        random_part = secrets.token_urlsafe(self.KEY_LENGTH)
        plain_key = f"{self.KEY_PREFIX}{random_part}"

        # Hash key for storage
        key_hash = self._hash_key(plain_key)

        # Generate key ID
        key_id = secrets.token_hex(16)

        # Calculate expiration
        now = datetime.utcnow()
        expires_at = now + timedelta(days=expires_in_days) if expires_in_days else None

        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=now,
            expires_at=expires_at,
            last_used=None,
            status=KeyStatus.ACTIVE,
            scopes=scopes,
            rotation_policy=rotation_policy,
            metadata=metadata or {}
        )

        # Store hashed key
        self.storage[key_hash] = api_key

        # Log generation
        self._log_event('key_generated', key_id, {'name': name})

        return plain_key, api_key

    def validate_key(
        self,
        plain_key: str,
        required_scopes: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[APIKey], Optional[str]]:
        """
        Validate API key.

        Args:
            plain_key: Plain text API key
            required_scopes: Required permission scopes

        Returns:
            Tuple of (is_valid, APIKey_object, error_message)
        """
        # Hash the provided key
        key_hash = self._hash_key(plain_key)

        # Retrieve stored key
        api_key = self.storage.get(key_hash)

        if not api_key:
            return False, None, "Invalid API key"

        # Check status
        if api_key.status != KeyStatus.ACTIVE:
            return False, api_key, f"Key is {api_key.status.value}"

        # Check expiration
        if api_key.is_expired():
            api_key.status = KeyStatus.EXPIRED
            return False, api_key, "Key has expired"

        # Check scopes
        if required_scopes:
            missing_scopes = set(required_scopes) - set(api_key.scopes)
            if missing_scopes:
                return False, api_key, f"Missing scopes: {', '.join(missing_scopes)}"

        # Update last used
        api_key.last_used = datetime.utcnow()

        # Log usage
        self._log_event('key_used', api_key.key_id, {})

        return True, api_key, None

    def rotate_key(
        self,
        old_key_id: str,
        grace_period_days: int = 7,
    ) -> Tuple[Optional[str], Optional[APIKey]]:
        """
        Rotate API key.

        Args:
            old_key_id: ID of key to rotate
            grace_period_days: Days before old key is revoked

        Returns:
            Tuple of (new_plain_key, new_APIKey) or (None, None) if not found
        """
        # Find old key
        old_key = None
        for api_key in self.storage.values():
            if api_key.key_id == old_key_id:
                old_key = api_key
                break

        if not old_key:
            return None, None

        # Generate new key with same properties
        new_plain_key, new_key = self.generate_key(
            name=f"{old_key.name} (rotated)",
            scopes=old_key.scopes,
            expires_in_days=365,
            rotation_policy=old_key.rotation_policy,
            metadata={
                **old_key.metadata,
                'rotated_from': old_key_id,
                'rotation_date': datetime.utcnow().isoformat()
            }
        )

        # Mark old key as rotated with grace period
        old_key.status = KeyStatus.ROTATED
        old_key.expires_at = datetime.utcnow() + timedelta(days=grace_period_days)

        # Log rotation
        self._log_event('key_rotated', old_key_id, {
            'new_key_id': new_key.key_id,
            'grace_period_days': grace_period_days
        })

        return new_plain_key, new_key

    def revoke_key(self, key_id: str, reason: Optional[str] = None) -> bool:
        """
        Revoke API key.

        Args:
            key_id: Key ID to revoke
            reason: Revocation reason

        Returns:
            True if successful, False if not found
        """
        for api_key in self.storage.values():
            if api_key.key_id == key_id:
                api_key.status = KeyStatus.REVOKED

                # Log revocation
                self._log_event('key_revoked', key_id, {'reason': reason or 'manual'})

                return True

        return False

    def list_keys(
        self,
        status_filter: Optional[KeyStatus] = None,
    ) -> List[APIKey]:
        """
        List all API keys.

        Args:
            status_filter: Filter by status

        Returns:
            List of APIKey objects
        """
        keys = list(self.storage.values())

        if status_filter:
            keys = [k for k in keys if k.status == status_filter]

        return keys

    def check_rotation_needed(self) -> List[APIKey]:
        """
        Check which keys need rotation.

        Returns:
            List of keys that need rotation
        """
        needs_rotation = []

        for api_key in self.storage.values():
            if api_key.status == KeyStatus.ACTIVE and api_key.needs_rotation():
                needs_rotation.append(api_key)

        return needs_rotation

    def auto_rotate_keys(self, grace_period_days: int = 7) -> List[Tuple[str, APIKey]]:
        """
        Automatically rotate keys that need rotation.

        Args:
            grace_period_days: Grace period for old keys

        Returns:
            List of (new_plain_key, new_APIKey) tuples
        """
        rotated_keys = []

        for api_key in self.check_rotation_needed():
            new_key = self.rotate_key(api_key.key_id, grace_period_days)
            if new_key[0]:
                rotated_keys.append(new_key)

        return rotated_keys

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API key usage statistics.

        Returns:
            Usage statistics dictionary
        """
        total_keys = len(self.storage)
        active_keys = len([k for k in self.storage.values() if k.status == KeyStatus.ACTIVE])
        expired_keys = len([k for k in self.storage.values() if k.is_expired()])
        needs_rotation = len(self.check_rotation_needed())

        return {
            'total_keys': total_keys,
            'active_keys': active_keys,
            'expired_keys': expired_keys,
            'needs_rotation': needs_rotation,
            'recent_usage': len([e for e in self.usage_log[-100:] if e['event'] == 'key_used']),
        }

    def _hash_key(self, plain_key: str) -> str:
        """
        Hash API key for storage.

        Uses HMAC-SHA256 for additional security.
        """
        # Use HMAC for additional security
        hmac_obj = hmac.new(
            b'loki_api_key_secret',
            plain_key.encode(),
            hashlib.sha256
        )
        return hmac_obj.hexdigest()

    def _log_event(self, event: str, key_id: str, details: Dict[str, Any]):
        """Log key-related event."""
        self.usage_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'key_id': key_id,
            'details': details
        })

        # Keep only last 1000 events
        if len(self.usage_log) > 1000:
            self.usage_log = self.usage_log[-1000:]


def scan_for_exposed_keys(text: str) -> List[str]:
    """
    Scan text for potentially exposed API keys.

    Args:
        text: Text to scan

    Returns:
        List of potential API keys found
    """
    patterns = [
        r'loki_[A-Za-z0-9_-]{32,}',
        r'sk-ant-[A-Za-z0-9_-]{32,}',
        r'sk-[A-Za-z0-9]{32,}',
        r'AIza[A-Za-z0-9_-]{35}',
    ]

    found_keys = []
    for pattern in patterns:
        import re
        matches = re.findall(pattern, text)
        found_keys.extend(matches)

    return found_keys
