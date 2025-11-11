"""
Tests for Semantic Matcher
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.nlp.semantic_matcher import SemanticMatcher, get_semantic_matcher


class TestSemanticMatcher(unittest.TestCase):
    """Test cases for SemanticMatcher"""

    def setUp(self):
        """Set up test fixtures"""
        self.matcher = SemanticMatcher()

    def test_initialization(self):
        """Test matcher initializes correctly"""
        self.assertIsNotNone(self.matcher)
        self.assertEqual(self.matcher.model_name, 'all-MiniLM-L6-v2')

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        import numpy as np
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])

        similarity = self.matcher.cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=2)

        vec3 = np.array([0.0, 1.0, 0.0])
        similarity2 = self.matcher.cosine_similarity(vec1, vec3)
        self.assertAlmostEqual(similarity2, 0.0, places=2)

    def test_find_similar_patterns(self):
        """Test finding similar patterns"""
        query = "investment with guaranteed returns"
        candidates = [
            "guaranteed profit investment",
            "risk-free investment opportunity",
            "capital at risk disclosure",
            "past performance warning"
        ]

        similar = self.matcher.find_similar_patterns(query, candidates, threshold=0.3)
        self.assertIsInstance(similar, list)
        self.assertTrue(len(similar) > 0)

        # Check format
        for pattern, score in similar:
            self.assertIsInstance(pattern, str)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

    def test_is_semantically_equivalent(self):
        """Test semantic equivalence detection"""
        text1 = "The value of investments can fall as well as rise"
        text2 = "Investment values may go up or down"

        # These should be semantically similar
        is_equivalent = self.matcher.is_semantically_equivalent(text1, text2, threshold=0.5)
        self.assertIsInstance(is_equivalent, bool)

    def test_find_paraphrases(self):
        """Test paraphrase detection"""
        text = "capital at risk"
        corpus = [
            "your money may be lost",
            "investment carries risk",
            "you could lose your investment",
            "sunny weather forecast"
        ]

        paraphrases = self.matcher.find_paraphrases(text, corpus, threshold=0.3)
        self.assertIsInstance(paraphrases, list)

    def test_cache_management(self):
        """Test cache operations"""
        # Clear cache
        self.matcher.clear_cache()

        # Get cache info
        info = self.matcher.get_cache_info()
        self.assertIn('hits', info)
        self.assertIn('misses', info)
        self.assertIn('size', info)

    def test_singleton_pattern(self):
        """Test singleton accessor"""
        matcher1 = get_semantic_matcher()
        matcher2 = get_semantic_matcher()

        self.assertIs(matcher1, matcher2)


if __name__ == '__main__':
    unittest.main()
