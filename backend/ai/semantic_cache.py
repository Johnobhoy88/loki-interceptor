"""
Semantic Caching Module

Provides intelligent caching based on semantic similarity:
- Similarity-based matching
- Vector embeddings (simple)
- Cache invalidation strategies
- TTL management
"""

import hashlib
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class CacheStrategy(str, Enum):
    """Cache strategy for semantic matching"""
    EXACT = "exact"  # Exact match only
    FUZZY = "fuzzy"  # Fuzzy matching with similarity threshold
    SEMANTIC = "semantic"  # Full semantic similarity
    HYBRID = "hybrid"  # Combine multiple strategies


@dataclass
class CacheEntry:
    """Entry in semantic cache"""
    key: str
    prompt: str
    response: str
    embedding: Optional[List[float]] = None
    similarity_score: float = 1.0
    created_at: str = None
    expires_at: str = None
    hit_count: int = 0
    metadata: Dict = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.utcnow()

    def record_hit(self):
        """Record a cache hit"""
        self.hit_count += 1

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class SemanticCache:
    """
    Intelligent semantic cache for AI responses

    Features:
    - Multiple matching strategies
    - Simple embedding support
    - TTL and expiration
    - Hit rate tracking
    - Cache statistics
    """

    def __init__(self, strategy: CacheStrategy = CacheStrategy.HYBRID, max_size: int = 10000):
        self.strategy = strategy
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_log: List[Dict] = []
        self.embedder = SimpleEmbedder()

    def get(
        self,
        prompt: str,
        similarity_threshold: float = 0.85,
        use_semantic: bool = True
    ) -> Optional[Tuple[str, CacheEntry]]:
        """
        Retrieve cached response for similar prompt

        Args:
            prompt: Query prompt
            similarity_threshold: Minimum similarity for match (0-1)
            use_semantic: Whether to use semantic matching

        Returns:
            Tuple of (response, cache_entry) or None if not found
        """
        if self.strategy == CacheStrategy.EXACT:
            return self._get_exact(prompt)

        elif self.strategy == CacheStrategy.FUZZY:
            return self._get_fuzzy(prompt, similarity_threshold)

        elif self.strategy == CacheStrategy.SEMANTIC:
            if use_semantic:
                return self._get_semantic(prompt, similarity_threshold)
            else:
                return self._get_fuzzy(prompt, similarity_threshold)

        else:  # HYBRID
            # Try exact first
            result = self._get_exact(prompt)
            if result:
                return result

            # Try fuzzy
            result = self._get_fuzzy(prompt, similarity_threshold * 0.95)
            if result:
                return result

            # Try semantic
            if use_semantic:
                return self._get_semantic(prompt, similarity_threshold)

            return None

    def set(
        self,
        prompt: str,
        response: str,
        ttl_minutes: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> CacheEntry:
        """
        Store response in cache

        Args:
            prompt: The prompt
            response: The response
            ttl_minutes: Time to live in minutes (None = no expiration)
            metadata: Additional metadata

        Returns:
            CacheEntry that was stored
        """
        # Manage cache size
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        # Generate key
        key = self._generate_key(prompt)

        # Calculate expiration
        expires_at = None
        if ttl_minutes:
            expires_at = (datetime.utcnow() + timedelta(minutes=ttl_minutes)).isoformat()

        # Generate embedding if using semantic
        embedding = None
        if self.strategy in [CacheStrategy.SEMANTIC, CacheStrategy.HYBRID]:
            embedding = self.embedder.embed(prompt)

        # Create entry
        entry = CacheEntry(
            key=key,
            prompt=prompt,
            response=response,
            embedding=embedding,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            metadata=metadata or {}
        )

        self.cache[key] = entry
        return entry

    def _get_exact(self, prompt: str) -> Optional[Tuple[str, CacheEntry]]:
        """Get exact match from cache"""
        key = self._generate_key(prompt)

        if key not in self.cache:
            self._log_access(prompt, "miss", "exact")
            return None

        entry = self.cache[key]

        if entry.is_expired():
            del self.cache[key]
            self._log_access(prompt, "miss", "exact")
            return None

        entry.record_hit()
        self._log_access(prompt, "hit", "exact")
        return entry.response, entry

    def _get_fuzzy(
        self,
        prompt: str,
        threshold: float = 0.85
    ) -> Optional[Tuple[str, CacheEntry]]:
        """Get best fuzzy match from cache"""
        best_match = None
        best_score = threshold

        for entry in self.cache.values():
            if entry.is_expired():
                continue

            similarity = self._fuzzy_similarity(prompt, entry.prompt)

            if similarity > best_score:
                best_score = similarity
                best_match = entry

        if best_match is None:
            self._log_access(prompt, "miss", "fuzzy")
            return None

        best_match.record_hit()
        best_match.similarity_score = best_score
        self._log_access(prompt, "hit", "fuzzy", best_score)

        return best_match.response, best_match

    def _get_semantic(
        self,
        prompt: str,
        threshold: float = 0.85
    ) -> Optional[Tuple[str, CacheEntry]]:
        """Get best semantic match using embeddings"""
        prompt_embedding = self.embedder.embed(prompt)
        best_match = None
        best_score = threshold

        for entry in self.cache.values():
            if entry.is_expired() or entry.embedding is None:
                continue

            similarity = self._cosine_similarity(prompt_embedding, entry.embedding)

            if similarity > best_score:
                best_score = similarity
                best_match = entry

        if best_match is None:
            self._log_access(prompt, "miss", "semantic")
            return None

        best_match.record_hit()
        best_match.similarity_score = best_score
        self._log_access(prompt, "hit", "semantic", best_score)

        return best_match.response, best_match

    def delete(self, prompt: str):
        """Delete entry from cache"""
        key = self._generate_key(prompt)
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear entire cache"""
        self.cache.clear()

    def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return

        # Find entry with least hits (simple LRU approximation)
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].hit_count)
        del self.cache[lru_key]

    def _generate_key(self, prompt: str) -> str:
        """Generate cache key from prompt"""
        return hashlib.sha256(prompt.encode()).hexdigest()

    def _fuzzy_similarity(self, s1: str, s2: str) -> float:
        """Calculate fuzzy similarity between strings"""
        # Simple Jaccard similarity
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        if not v1 or not v2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = sum(a ** 2 for a in v1) ** 0.5
        mag2 = sum(b ** 2 for b in v2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _log_access(
        self,
        prompt: str,
        result: str,
        strategy: str,
        similarity: float = 1.0
    ):
        """Log cache access"""
        self.access_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "prompt_hash": hashlib.md5(prompt.encode()).hexdigest(),
            "result": result,
            "strategy": strategy,
            "similarity": similarity
        })

        # Keep access log bounded
        if len(self.access_log) > 10000:
            self.access_log = self.access_log[-5000:]

    def get_statistics(self) -> Dict:
        """Get cache statistics"""
        if not self.access_log:
            return {}

        hits = sum(1 for entry in self.access_log if entry['result'] == 'hit')
        misses = sum(1 for entry in self.access_log if entry['result'] == 'miss')
        total = hits + misses

        avg_similarity = (
            sum(entry['similarity'] for entry in self.access_log if entry['result'] == 'hit') /
            hits if hits > 0 else 0
        )

        return {
            "cache_size": len(self.cache),
            "total_accesses": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate": hits / total if total > 0 else 0,
            "average_similarity": avg_similarity,
            "strategies_used": list(set(e['strategy'] for e in self.access_log))
        }


class SimpleEmbedder:
    """Simple embedding generator for semantic similarity"""

    def embed(self, text: str) -> List[float]:
        """
        Generate simple embedding for text

        In production, use proper embedding models (e.g., from HuggingFace)
        This is a naive implementation for demonstration
        """
        # Simple character-based embedding
        # Normalize text
        text = text.lower()

        # Create feature vector based on character frequencies
        vector = [0.0] * 256

        for char in text:
            idx = ord(char) % 256
            vector[idx] += 1.0

        # Normalize
        magnitude = sum(v ** 2 for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector
