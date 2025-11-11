"""
Context Window Management Module

Manages AI model context windows to optimize:
- Token usage
- Relevant context inclusion
- Memory management
- Context priority
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ContextStrategy(str, Enum):
    """Strategy for managing context window"""
    SLIDING_WINDOW = "sliding_window"  # Keep most recent context
    PRIORITY_BASED = "priority_based"  # Keep high-priority context
    RELEVANCE_BASED = "relevance_based"  # Keep relevant context
    HYBRID = "hybrid"  # Combine strategies


@dataclass
class ContextItem:
    """Item in context window"""
    content: str
    priority: float  # 0-1, higher = more important
    relevance_score: float  # 0-1 relevance to current task
    tokens: int
    created_at: str
    is_system: bool = False  # System vs user context
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def get_importance_score(self) -> float:
        """Calculate overall importance"""
        # Weighted combination of priority and relevance
        return self.priority * 0.6 + self.relevance_score * 0.4


class ContextWindowManager:
    """
    Manages AI context windows for optimal token usage and response quality

    Features:
    - Multiple context management strategies
    - Token-aware context selection
    - Priority management
    - Context summarization
    """

    def __init__(
        self,
        max_tokens: int = 8192,
        strategy: ContextStrategy = ContextStrategy.HYBRID
    ):
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.context_window: List[ContextItem] = []
        self.history: List[str] = []
        self.token_estimator = TokenEstimator()

    def add_context(
        self,
        content: str,
        priority: float = 0.5,
        relevance_score: float = 0.5,
        is_system: bool = False,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add context to window

        Args:
            content: Context content
            priority: Importance (0-1)
            relevance_score: Relevance to task (0-1)
            is_system: Whether this is system context
            metadata: Additional metadata

        Returns:
            True if added, False if window full and couldn't fit
        """
        tokens = self.token_estimator.estimate(content)

        item = ContextItem(
            content=content,
            priority=priority,
            relevance_score=relevance_score,
            tokens=tokens,
            created_at=datetime.utcnow().isoformat(),
            is_system=is_system,
            metadata=metadata or {}
        )

        current_tokens = sum(item.tokens for item in self.context_window)

        # If adding would exceed limit, evict items
        if current_tokens + tokens > self.max_tokens:
            self._evict_items(current_tokens + tokens - self.max_tokens)

        self.context_window.append(item)
        self.history.append(f"Added context: {len(content)} chars")

        return True

    def get_current_context(self) -> str:
        """Get formatted current context"""
        if not self.context_window:
            return ""

        context_parts = []

        # Separate system and user context
        system_items = [i for i in self.context_window if i.is_system]
        user_items = [i for i in self.context_window if not i.is_system]

        # Add system context first
        if system_items:
            context_parts.append("[SYSTEM CONTEXT]")
            for item in system_items:
                context_parts.append(item.content)

        # Add user context
        if user_items:
            context_parts.append("\n[USER CONTEXT]")
            for item in user_items:
                context_parts.append(item.content)

        return "\n".join(context_parts)

    def get_context_summary(self) -> Dict:
        """Get summary of current context"""
        total_tokens = sum(item.tokens for item in self.context_window)
        avg_priority = sum(item.priority for item in self.context_window) / len(self.context_window) if self.context_window else 0
        avg_relevance = sum(item.relevance_score for item in self.context_window) / len(self.context_window) if self.context_window else 0

        return {
            "items": len(self.context_window),
            "total_tokens": total_tokens,
            "token_capacity": self.max_tokens,
            "utilization": total_tokens / self.max_tokens if self.max_tokens > 0 else 0,
            "average_priority": avg_priority,
            "average_relevance": avg_relevance,
            "system_items": sum(1 for i in self.context_window if i.is_system),
            "user_items": sum(1 for i in self.context_window if not i.is_system)
        }

    def clear(self):
        """Clear all context"""
        self.context_window.clear()
        self.history.append("Context window cleared")

    def remove_item(self, index: int) -> bool:
        """Remove specific context item"""
        if 0 <= index < len(self.context_window):
            removed = self.context_window.pop(index)
            self.history.append(f"Removed context: {len(removed.content)} chars")
            return True
        return False

    def reorder_by_importance(self):
        """Reorder context by importance score"""
        self.context_window.sort(
            key=lambda x: x.get_importance_score(),
            reverse=True
        )

    def _evict_items(self, tokens_needed: int):
        """Evict context items to make room"""
        if self.strategy == ContextStrategy.SLIDING_WINDOW:
            self._evict_oldest(tokens_needed)

        elif self.strategy == ContextStrategy.PRIORITY_BASED:
            self._evict_lowest_priority(tokens_needed)

        elif self.strategy == ContextStrategy.RELEVANCE_BASED:
            self._evict_lowest_relevance(tokens_needed)

        else:  # HYBRID
            # Keep high priority items, remove low relevance
            self._evict_lowest_importance(tokens_needed)

    def _evict_oldest(self, tokens_needed: int):
        """Evict oldest items first"""
        self.context_window.sort(key=lambda x: x.created_at)

        while tokens_needed > 0 and self.context_window:
            item = self.context_window.pop(0)
            tokens_needed -= item.tokens
            self.history.append(f"Evicted (oldest): {len(item.content)} chars")

    def _evict_lowest_priority(self, tokens_needed: int):
        """Evict lowest priority items first"""
        self.context_window.sort(key=lambda x: x.priority)

        while tokens_needed > 0 and self.context_window:
            item = self.context_window.pop(0)
            tokens_needed -= item.tokens
            self.history.append(f"Evicted (low priority): {len(item.content)} chars")

    def _evict_lowest_relevance(self, tokens_needed: int):
        """Evict lowest relevance items first"""
        self.context_window.sort(key=lambda x: x.relevance_score)

        while tokens_needed > 0 and self.context_window:
            item = self.context_window.pop(0)
            tokens_needed -= item.tokens
            self.history.append(f"Evicted (low relevance): {len(item.content)} chars")

    def _evict_lowest_importance(self, tokens_needed: int):
        """Evict lowest overall importance items"""
        self.context_window.sort(key=lambda x: x.get_importance_score())

        while tokens_needed > 0 and self.context_window:
            item = self.context_window.pop(0)
            tokens_needed -= item.tokens
            self.history.append(f"Evicted (low importance): {len(item.content)} chars")

    def summarize_context(self) -> str:
        """Generate summary of current context"""
        if not self.context_window:
            return "No context available"

        summary_parts = [
            f"Context Summary ({len(self.context_window)} items):",
            f"Total Tokens: {sum(item.tokens for item in self.context_window)}/{self.max_tokens}",
            "Items:"
        ]

        for idx, item in enumerate(self.context_window, 1):
            preview = item.content[:50] + "..." if len(item.content) > 50 else item.content
            summary_parts.append(
                f"  {idx}. [{item.tokens} tokens] Priority: {item.priority:.2f}, "
                f"Relevance: {item.relevance_score:.2f} - {preview}"
            )

        return "\n".join(summary_parts)

    def get_statistics(self) -> Dict:
        """Get context management statistics"""
        return {
            "context_items": len(self.context_window),
            "total_tokens": sum(item.tokens for item in self.context_window),
            "max_tokens": self.max_tokens,
            "utilization_percent": (
                sum(item.tokens for item in self.context_window) / self.max_tokens * 100
                if self.max_tokens > 0 else 0
            ),
            "actions_taken": len(self.history),
            "strategy": self.strategy.value
        }


class TokenEstimator:
    """Estimates token counts for context items"""

    def estimate(self, text: str) -> int:
        """Estimate tokens in text"""
        # Average: ~4 chars per token for English
        return max(1, len(text) // 4)
