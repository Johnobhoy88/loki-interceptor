"""
Tests for Readability Scorer
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.nlp.readability import ReadabilityScorer, get_readability_scorer


class TestReadabilityScorer(unittest.TestCase):
    """Test cases for ReadabilityScorer"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = ReadabilityScorer()

        self.simple_text = "The cat sat on the mat. It was a sunny day. Birds were singing."

        self.complex_text = """
        Notwithstanding the aforementioned considerations, the implementation of
        sophisticated methodologies necessitates comprehensive evaluation of
        multifaceted parameters to facilitate optimal outcomes.
        """

    def test_initialization(self):
        """Test scorer initializes correctly"""
        self.assertIsNotNone(self.scorer)
        self.assertIsNotNone(self.scorer.dale_chall_words)
        self.assertIsNotNone(self.scorer.legal_jargon)

    def test_count_syllables(self):
        """Test syllable counting"""
        self.assertEqual(self.scorer.count_syllables("cat"), 1)
        self.assertEqual(self.scorer.count_syllables("running"), 2)
        self.assertEqual(self.scorer.count_syllables("beautiful"), 3)
        self.assertEqual(self.scorer.count_syllables("communication"), 5)

    def test_split_sentences(self):
        """Test sentence splitting"""
        text = "This is sentence one. This is sentence two! Is this sentence three?"

        sentences = self.scorer.split_sentences(text)
        self.assertEqual(len(sentences), 3)

    def test_tokenize_words(self):
        """Test word tokenization"""
        text = "The quick brown fox jumps over the lazy dog."

        words = self.scorer.tokenize_words(text)
        self.assertEqual(len(words), 9)

    def test_flesch_reading_ease(self):
        """Test Flesch Reading Ease calculation"""
        score = self.scorer.flesch_reading_ease(
            total_words=100,
            total_sentences=5,
            total_syllables=150
        )

        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 120)

    def test_flesch_kincaid_grade(self):
        """Test Flesch-Kincaid Grade calculation"""
        grade = self.scorer.flesch_kincaid_grade(
            total_words=100,
            total_sentences=5,
            total_syllables=150
        )

        self.assertIsInstance(grade, float)
        self.assertGreaterEqual(grade, 0)

    def test_gunning_fog_index(self):
        """Test Gunning Fog Index calculation"""
        fog = self.scorer.gunning_fog_index(
            total_words=100,
            total_sentences=5,
            complex_words=15
        )

        self.assertIsInstance(fog, float)
        self.assertGreaterEqual(fog, 0)

    def test_count_passive_voice(self):
        """Test passive voice detection"""
        passive_text = "The document was written by the team. The policy is being reviewed."
        active_text = "The team wrote the document. We review the policy."

        passive_count = self.scorer.count_passive_voice(passive_text)
        active_count = self.scorer.count_passive_voice(active_text)

        self.assertGreater(passive_count, active_count)

    def test_count_legal_jargon(self):
        """Test legal jargon counting"""
        jargon_text = "Notwithstanding the aforementioned provisions herein, pursuant to..."
        plain_text = "Despite the provisions mentioned earlier, according to..."

        jargon_count = self.scorer.count_legal_jargon(jargon_text)
        plain_count = self.scorer.count_legal_jargon(plain_text)

        self.assertGreater(jargon_count, plain_count)

    def test_analyze_simple_text(self):
        """Test analysis of simple text"""
        scores = self.scorer.analyze(self.simple_text)

        self.assertIsNotNone(scores)
        self.assertGreater(scores.flesch_reading_ease, 60)  # Should be fairly easy
        self.assertLess(scores.flesch_kincaid_grade, 8)  # Low grade level

    def test_analyze_complex_text(self):
        """Test analysis of complex text"""
        scores = self.scorer.analyze(self.complex_text)

        self.assertIsNotNone(scores)
        self.assertLess(scores.flesch_reading_ease, 50)  # Should be difficult
        self.assertGreater(scores.flesch_kincaid_grade, 10)  # High grade level

    def test_suggestions_generation(self):
        """Test that suggestions are generated"""
        scores = self.scorer.analyze(self.complex_text)

        self.assertIsInstance(scores.suggestions, list)
        self.assertTrue(len(scores.suggestions) > 0)

    def test_all_metrics_present(self):
        """Test that all readability metrics are calculated"""
        scores = self.scorer.analyze(self.simple_text)

        self.assertIsNotNone(scores.flesch_reading_ease)
        self.assertIsNotNone(scores.flesch_kincaid_grade)
        self.assertIsNotNone(scores.gunning_fog)
        self.assertIsNotNone(scores.smog_index)
        self.assertIsNotNone(scores.coleman_liau_index)
        self.assertIsNotNone(scores.automated_readability_index)
        self.assertIsNotNone(scores.dale_chall_score)

    def test_counts_present(self):
        """Test that all counts are calculated"""
        scores = self.scorer.analyze(self.simple_text)

        self.assertGreater(scores.sentence_count, 0)
        self.assertGreater(scores.word_count, 0)
        self.assertGreater(scores.syllable_count, 0)
        self.assertGreaterEqual(scores.complex_word_count, 0)

    def test_singleton_pattern(self):
        """Test singleton accessor"""
        scorer1 = get_readability_scorer()
        scorer2 = get_readability_scorer()

        self.assertIs(scorer1, scorer2)


if __name__ == '__main__':
    unittest.main()
