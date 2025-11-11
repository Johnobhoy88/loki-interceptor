"""
Semantic Matcher - Advanced semantic similarity matching using sentence transformers
Enables finding similar patterns even when exact wording differs
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """
    Semantic similarity matching using sentence embeddings
    Finds semantically similar text patterns for intelligent correction suggestions
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_size: int = 1000):
        """
        Initialize semantic matcher with sentence transformer model

        Args:
            model_name: HuggingFace model name (default: lightweight MiniLM)
            cache_size: LRU cache size for embeddings
        """
        self.model_name = model_name
        self.model = None
        self.cache_size = cache_size
        self._embedding_cache = {}
        self._initialize_model()

    def _initialize_model(self):
        """Lazy load the sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded semantic model: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Semantic matching disabled.")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load semantic model: {e}")
            self.model = None

    @lru_cache(maxsize=1000)
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text with caching

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as numpy array
        """
        if self.model is None:
            # Fallback to simple word overlap if model not available
            return np.array([hash(word) % 100 for word in text.lower().split()[:10]])

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return np.zeros(384)  # Default MiniLM dimension

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(max(0.0, min(1.0, similarity)))
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0

    def find_similar_patterns(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.7,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find semantically similar patterns from candidates

        Args:
            query: Query text to match
            candidates: List of candidate patterns
            threshold: Minimum similarity threshold (0-1)
            top_k: Maximum number of results to return

        Returns:
            List of (pattern, similarity_score) tuples, sorted by similarity
        """
        if not candidates:
            return []

        query_embedding = self._get_embedding(query)

        similarities = []
        for candidate in candidates:
            candidate_embedding = self._get_embedding(candidate)
            similarity = self.cosine_similarity(query_embedding, candidate_embedding)

            if similarity >= threshold:
                similarities.append((candidate, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def match_correction_patterns(
        self,
        text: str,
        pattern_library: Dict[str, List[str]],
        threshold: float = 0.75
    ) -> List[Dict]:
        """
        Match text against pattern library using semantic similarity

        Args:
            text: Text to analyze
            pattern_library: Dict of {category: [patterns]}
            threshold: Similarity threshold

        Returns:
            List of matched patterns with metadata
        """
        matches = []

        for category, patterns in pattern_library.items():
            similar = self.find_similar_patterns(text, patterns, threshold)

            for pattern, score in similar:
                matches.append({
                    'category': category,
                    'pattern': pattern,
                    'similarity': score,
                    'match_type': 'semantic'
                })

        return matches

    def batch_similarity(
        self,
        queries: List[str],
        candidates: List[str]
    ) -> np.ndarray:
        """
        Calculate similarity matrix for batch of queries vs candidates
        More efficient than individual comparisons

        Args:
            queries: List of query texts
            candidates: List of candidate texts

        Returns:
            Similarity matrix (queries x candidates)
        """
        if self.model is None:
            # Simple fallback
            matrix = np.zeros((len(queries), len(candidates)))
            for i, q in enumerate(queries):
                q_words = set(q.lower().split())
                for j, c in enumerate(candidates):
                    c_words = set(c.lower().split())
                    if q_words and c_words:
                        matrix[i, j] = len(q_words & c_words) / max(len(q_words), len(c_words))
            return matrix

        try:
            query_embeddings = self.model.encode(queries, convert_to_numpy=True)
            candidate_embeddings = self.model.encode(candidates, convert_to_numpy=True)

            # Compute cosine similarity matrix
            similarity_matrix = np.dot(query_embeddings, candidate_embeddings.T)

            # Normalize
            query_norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
            candidate_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
            similarity_matrix = similarity_matrix / (query_norms @ candidate_norms.T)

            return similarity_matrix
        except Exception as e:
            logger.error(f"Batch similarity error: {e}")
            return np.zeros((len(queries), len(candidates)))

    def is_semantically_equivalent(
        self,
        text1: str,
        text2: str,
        threshold: float = 0.85
    ) -> bool:
        """
        Check if two texts are semantically equivalent

        Args:
            text1: First text
            text2: Second text
            threshold: High threshold for equivalence (default 0.85)

        Returns:
            True if texts are semantically equivalent
        """
        embedding1 = self._get_embedding(text1)
        embedding2 = self._get_embedding(text2)
        similarity = self.cosine_similarity(embedding1, embedding2)

        return similarity >= threshold

    def find_paraphrases(
        self,
        text: str,
        corpus: List[str],
        threshold: float = 0.8
    ) -> List[Tuple[str, float]]:
        """
        Find paraphrases (semantically similar but differently worded)

        Args:
            text: Text to find paraphrases for
            corpus: Corpus to search
            threshold: Similarity threshold

        Returns:
            List of (paraphrase, similarity) tuples
        """
        return self.find_similar_patterns(text, corpus, threshold=threshold, top_k=10)

    def clear_cache(self):
        """Clear embedding cache to free memory"""
        self._embedding_cache.clear()
        self._get_embedding.cache_clear()
        logger.info("Semantic matcher cache cleared")

    def get_cache_info(self) -> Dict:
        """Get cache statistics"""
        cache_info = self._get_embedding.cache_info()
        return {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'size': cache_info.currsize,
            'maxsize': cache_info.maxsize
        }


# Singleton instance for efficient reuse
_semantic_matcher_instance = None

def get_semantic_matcher() -> SemanticMatcher:
    """Get singleton semantic matcher instance"""
    global _semantic_matcher_instance
    if _semantic_matcher_instance is None:
        _semantic_matcher_instance = SemanticMatcher()
    return _semantic_matcher_instance
