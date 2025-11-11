"""
Feature Flags System
Dynamic feature toggling with gradual rollout support
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import redis

logger = logging.getLogger(__name__)


class RolloutStrategy(Enum):
    """Feature rollout strategies"""
    ALL = "all"  # All users
    NONE = "none"  # No users
    PERCENTAGE = "percentage"  # Percentage-based
    USERS = "users"  # Specific users
    GROUPS = "groups"  # Specific groups
    GRADUAL = "gradual"  # Time-based gradual rollout


@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    enabled: bool = False
    description: str = ""
    strategy: RolloutStrategy = RolloutStrategy.ALL
    percentage: int = 0  # 0-100
    users: Set[str] = field(default_factory=set)
    groups: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'description': self.description,
            'strategy': self.strategy.value,
            'percentage': self.percentage,
            'users': list(self.users),
            'groups': list(self.groups),
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureFlag':
        """Create from dictionary"""
        return cls(
            name=data['name'],
            enabled=data.get('enabled', False),
            description=data.get('description', ''),
            strategy=RolloutStrategy(data.get('strategy', 'all')),
            percentage=data.get('percentage', 0),
            users=set(data.get('users', [])),
            groups=set(data.get('groups', [])),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.utcnow(),
        )


class FeatureFlags:
    """
    Feature Flags Management System
    Provides dynamic feature toggling with various rollout strategies
    """

    def __init__(self, config, redis_client: Optional[redis.Redis] = None):
        """
        Initialize feature flags system

        Args:
            config: PlatformConfig instance
            redis_client: Optional Redis client for persistence
        """
        self.config = config
        self.redis_client = redis_client
        self.flags: Dict[str, FeatureFlag] = {}
        self._cache_key_prefix = "loki:feature_flags:"

        # Load flags from storage
        self._load_flags()

        # Register default flags
        self._register_default_flags()

    def _register_default_flags(self):
        """Register default platform feature flags"""
        default_flags = {
            # Core features
            'async_processing': FeatureFlag(
                name='async_processing',
                enabled=True,
                description='Enable async request processing',
                strategy=RolloutStrategy.ALL
            ),
            'caching': FeatureFlag(
                name='caching',
                enabled=True,
                description='Enable response caching',
                strategy=RolloutStrategy.ALL
            ),
            'compression': FeatureFlag(
                name='compression',
                enabled=True,
                description='Enable response compression',
                strategy=RolloutStrategy.ALL
            ),

            # Advanced features
            'advanced_analytics': FeatureFlag(
                name='advanced_analytics',
                enabled=False,
                description='Enable advanced analytics and insights',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=50
            ),
            'ai_suggestions': FeatureFlag(
                name='ai_suggestions',
                enabled=False,
                description='Enable AI-powered suggestions',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=25
            ),
            'real_time_monitoring': FeatureFlag(
                name='real_time_monitoring',
                enabled=True,
                description='Enable real-time system monitoring',
                strategy=RolloutStrategy.ALL
            ),

            # Compliance features
            'fca_advanced': FeatureFlag(
                name='fca_advanced',
                enabled=True,
                description='Enable advanced FCA compliance checks',
                strategy=RolloutStrategy.ALL
            ),
            'gdpr_advanced': FeatureFlag(
                name='gdpr_advanced',
                enabled=True,
                description='Enable advanced GDPR compliance checks',
                strategy=RolloutStrategy.ALL
            ),
            'tax_compliance': FeatureFlag(
                name='tax_compliance',
                enabled=True,
                description='Enable tax compliance checks',
                strategy=RolloutStrategy.ALL
            ),

            # Performance features
            'circuit_breaker': FeatureFlag(
                name='circuit_breaker',
                enabled=True,
                description='Enable circuit breaker pattern',
                strategy=RolloutStrategy.ALL
            ),
            'rate_limiting': FeatureFlag(
                name='rate_limiting',
                enabled=True,
                description='Enable rate limiting',
                strategy=RolloutStrategy.ALL
            ),
            'request_batching': FeatureFlag(
                name='request_batching',
                enabled=False,
                description='Enable request batching',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=30
            ),

            # Security features
            'enhanced_encryption': FeatureFlag(
                name='enhanced_encryption',
                enabled=True,
                description='Enable enhanced data encryption',
                strategy=RolloutStrategy.ALL
            ),
            'audit_logging': FeatureFlag(
                name='audit_logging',
                enabled=True,
                description='Enable detailed audit logging',
                strategy=RolloutStrategy.ALL
            ),
            'mfa_enforcement': FeatureFlag(
                name='mfa_enforcement',
                enabled=False,
                description='Enforce multi-factor authentication',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=10
            ),

            # Beta features
            'beta_ui': FeatureFlag(
                name='beta_ui',
                enabled=False,
                description='Enable beta UI features',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=5
            ),
            'experimental_corrector': FeatureFlag(
                name='experimental_corrector',
                enabled=False,
                description='Enable experimental correction algorithms',
                strategy=RolloutStrategy.PERCENTAGE,
                percentage=10
            ),
        }

        for name, flag in default_flags.items():
            if name not in self.flags:
                self.flags[name] = flag
                self._save_flag(flag)

    def _load_flags(self):
        """Load flags from Redis storage"""
        if not self.redis_client:
            return

        try:
            pattern = f"{self._cache_key_prefix}*"
            keys = self.redis_client.keys(pattern)

            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    flag_data = json.loads(data)
                    flag = FeatureFlag.from_dict(flag_data)
                    self.flags[flag.name] = flag

            logger.info(f"Loaded {len(self.flags)} feature flags from storage")
        except Exception as e:
            logger.error(f"Error loading feature flags: {e}")

    def _save_flag(self, flag: FeatureFlag):
        """Save flag to Redis storage"""
        if not self.redis_client:
            return

        try:
            key = f"{self._cache_key_prefix}{flag.name}"
            data = json.dumps(flag.to_dict())
            self.redis_client.set(key, data)
        except Exception as e:
            logger.error(f"Error saving feature flag {flag.name}: {e}")

    def create_flag(
        self,
        name: str,
        enabled: bool = False,
        description: str = "",
        strategy: RolloutStrategy = RolloutStrategy.ALL,
        **kwargs
    ) -> FeatureFlag:
        """
        Create a new feature flag

        Args:
            name: Flag name
            enabled: Initial enabled state
            description: Flag description
            strategy: Rollout strategy
            **kwargs: Additional flag parameters

        Returns:
            Created FeatureFlag
        """
        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            description=description,
            strategy=strategy,
            **kwargs
        )

        self.flags[name] = flag
        self._save_flag(flag)

        logger.info(f"Created feature flag: {name}")
        return flag

    def update_flag(
        self,
        name: str,
        enabled: Optional[bool] = None,
        strategy: Optional[RolloutStrategy] = None,
        percentage: Optional[int] = None,
        **kwargs
    ) -> Optional[FeatureFlag]:
        """
        Update an existing feature flag

        Args:
            name: Flag name
            enabled: New enabled state
            strategy: New rollout strategy
            percentage: New percentage (for percentage strategy)
            **kwargs: Additional parameters to update

        Returns:
            Updated FeatureFlag or None if not found
        """
        if name not in self.flags:
            logger.warning(f"Feature flag not found: {name}")
            return None

        flag = self.flags[name]

        if enabled is not None:
            flag.enabled = enabled

        if strategy is not None:
            flag.strategy = strategy

        if percentage is not None:
            flag.percentage = max(0, min(100, percentage))

        for key, value in kwargs.items():
            if hasattr(flag, key):
                setattr(flag, key, value)

        flag.updated_at = datetime.utcnow()
        self._save_flag(flag)

        logger.info(f"Updated feature flag: {name}")
        return flag

    def delete_flag(self, name: str) -> bool:
        """
        Delete a feature flag

        Args:
            name: Flag name

        Returns:
            True if deleted, False if not found
        """
        if name not in self.flags:
            return False

        del self.flags[name]

        if self.redis_client:
            try:
                key = f"{self._cache_key_prefix}{name}"
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Error deleting feature flag {name}: {e}")

        logger.info(f"Deleted feature flag: {name}")
        return True

    def is_enabled(
        self,
        name: str,
        user_id: Optional[str] = None,
        group: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """
        Check if a feature is enabled for a user/group

        Args:
            name: Flag name
            user_id: Optional user ID
            group: Optional group name
            default: Default value if flag not found

        Returns:
            True if feature is enabled
        """
        if name not in self.flags:
            return default

        flag = self.flags[name]

        if not flag.enabled:
            return False

        # Check strategy
        if flag.strategy == RolloutStrategy.ALL:
            return True

        if flag.strategy == RolloutStrategy.NONE:
            return False

        if flag.strategy == RolloutStrategy.USERS:
            return user_id in flag.users if user_id else False

        if flag.strategy == RolloutStrategy.GROUPS:
            return group in flag.groups if group else False

        if flag.strategy == RolloutStrategy.PERCENTAGE:
            if user_id:
                # Deterministic percentage-based rollout
                hash_value = int(hashlib.md5(f"{name}:{user_id}".encode()).hexdigest(), 16)
                return (hash_value % 100) < flag.percentage
            return False

        return default

    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get a feature flag by name"""
        return self.flags.get(name)

    def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags"""
        return dict(self.flags)

    def get_enabled_flags(self, user_id: Optional[str] = None, group: Optional[str] = None) -> List[str]:
        """
        Get list of enabled flags for a user/group

        Args:
            user_id: Optional user ID
            group: Optional group name

        Returns:
            List of enabled flag names
        """
        return [
            name for name in self.flags.keys()
            if self.is_enabled(name, user_id, group)
        ]

    def add_user_to_flag(self, flag_name: str, user_id: str) -> bool:
        """Add user to a flag's user list"""
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]
        flag.users.add(user_id)
        flag.updated_at = datetime.utcnow()
        self._save_flag(flag)

        return True

    def remove_user_from_flag(self, flag_name: str, user_id: str) -> bool:
        """Remove user from a flag's user list"""
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]
        if user_id in flag.users:
            flag.users.remove(user_id)
            flag.updated_at = datetime.utcnow()
            self._save_flag(flag)

        return True

    def add_group_to_flag(self, flag_name: str, group: str) -> bool:
        """Add group to a flag's group list"""
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]
        flag.groups.add(group)
        flag.updated_at = datetime.utcnow()
        self._save_flag(flag)

        return True

    def remove_group_from_flag(self, flag_name: str, group: str) -> bool:
        """Remove group from a flag's group list"""
        if flag_name not in self.flags:
            return False

        flag = self.flags[flag_name]
        if group in flag.groups:
            flag.groups.remove(group)
            flag.updated_at = datetime.utcnow()
            self._save_flag(flag)

        return True

    def export_flags(self) -> Dict[str, Any]:
        """Export all flags as dictionary"""
        return {
            name: flag.to_dict()
            for name, flag in self.flags.items()
        }

    def import_flags(self, flags_data: Dict[str, Any]):
        """
        Import flags from dictionary

        Args:
            flags_data: Dictionary of flag data
        """
        for name, data in flags_data.items():
            try:
                flag = FeatureFlag.from_dict(data)
                self.flags[name] = flag
                self._save_flag(flag)
            except Exception as e:
                logger.error(f"Error importing flag {name}: {e}")

        logger.info(f"Imported {len(flags_data)} feature flags")

    def get_stats(self) -> Dict[str, Any]:
        """Get feature flag statistics"""
        total = len(self.flags)
        enabled = sum(1 for f in self.flags.values() if f.enabled)

        strategy_counts = {}
        for flag in self.flags.values():
            strategy = flag.strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'by_strategy': strategy_counts,
        }
