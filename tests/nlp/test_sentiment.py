"""
Tests for Sentiment Analyzer
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.core.nlp.sentiment import SentimentAnalyzer, ToneType, get_sentiment_analyzer


class TestSentimentAnalyzer(unittest.TestCase):
    """Test cases for SentimentAnalyzer"""

    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SentimentAnalyzer()

    def test_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.lexicons)

    def test_detect_misleading_language(self):
        """Test detection of misleading language"""
        misleading_text = "This is a guaranteed investment with risk-free returns."
        clean_text = "This investment carries capital risk."

        is_misleading, phrases = self.analyzer.detect_misleading_language(misleading_text)
        self.assertTrue(is_misleading)
        self.assertTrue(len(phrases) > 0)

        is_clean, _ = self.analyzer.detect_misleading_language(clean_text)
        self.assertFalse(is_clean)

    def test_detect_coercive_language(self):
        """Test detection of coercive language"""
        coercive_text = "You must act now immediately or you will miss this urgent opportunity."
        neutral_text = "This investment opportunity is available for your consideration."

        is_coercive, phrases = self.analyzer.detect_coercive_language(coercive_text)
        self.assertTrue(is_coercive)

        is_neutral, _ = self.analyzer.detect_coercive_language(neutral_text)
        self.assertFalse(is_neutral)

    def test_detect_overpromising(self):
        """Test detection of overpromising language"""
        overpromising_text = "The best investment with maximum returns and unbeatable performance."
        balanced_text = "Historical performance has been positive."

        is_overpromising, phrases = self.analyzer.detect_overpromising(overpromising_text)
        self.assertTrue(is_overpromising)

        is_balanced, _ = self.analyzer.detect_overpromising(balanced_text)
        self.assertFalse(is_balanced)

    def test_calculate_urgency_score(self):
        """Test urgency score calculation"""
        urgent_text = "Act now immediately! Time is running out! Don't delay!"
        calm_text = "Please consider this opportunity at your convenience."

        urgent_score = self.analyzer.calculate_urgency_score(urgent_text)
        calm_score = self.analyzer.calculate_urgency_score(calm_text)

        self.assertGreater(urgent_score, calm_score)
        self.assertGreaterEqual(urgent_score, 0.0)
        self.assertLessEqual(urgent_score, 1.0)

    def test_calculate_fear_score(self):
        """Test fear score calculation"""
        fearful_text = "You will lose out and miss this chance and regret it."
        neutral_text = "This is an investment opportunity."

        fear_score = self.analyzer.calculate_fear_score(fearful_text)
        neutral_score = self.analyzer.calculate_fear_score(neutral_text)

        self.assertGreater(fear_score, neutral_score)

    def test_calculate_hype_score(self):
        """Test hype score calculation"""
        hype_text = "Amazing! Incredible! Unbelievable opportunity! Once in a lifetime!"
        factual_text = "This investment has historical performance data."

        hype_score = self.analyzer.calculate_hype_score(hype_text)
        factual_score = self.analyzer.calculate_hype_score(factual_text)

        self.assertGreater(hype_score, factual_score)

    def test_determine_tone(self):
        """Test tone determination"""
        professional_text = "We provide clear and transparent information about our services."
        misleading_text = "Guaranteed profits with no risk whatsoever."

        professional_tone = self.analyzer.determine_tone(professional_text)
        misleading_tone = self.analyzer.determine_tone(misleading_text)

        self.assertIsInstance(professional_tone, ToneType)
        self.assertIsInstance(misleading_tone, ToneType)

    def test_analyze_compliant_tone(self):
        """Test analysis of compliant tone"""
        compliant_text = """
        Investment opportunity with potential returns. Capital is at risk.
        Past performance is not indicative of future results. Please read
        our risk warnings carefully before investing.
        """

        analysis = self.analyzer.analyze(compliant_text)

        self.assertIsNotNone(analysis)
        self.assertFalse(analysis.is_misleading)
        self.assertFalse(analysis.is_coercive)
        self.assertTrue(analysis.is_compliant_tone)

    def test_analyze_non_compliant_tone(self):
        """Test analysis of non-compliant tone"""
        non_compliant_text = """
        Guaranteed returns! Risk-free investment! Act now before it's too late!
        You can't lose with this amazing opportunity!
        """

        analysis = self.analyzer.analyze(non_compliant_text)

        self.assertIsNotNone(analysis)
        self.assertTrue(analysis.is_misleading or analysis.is_overpromising)
        self.assertFalse(analysis.is_compliant_tone)
        self.assertTrue(len(analysis.flagged_phrases) > 0)

    def test_suggestions_generation(self):
        """Test that suggestions are generated"""
        text = "Guaranteed profits! Act now! Amazing returns!"

        analysis = self.analyzer.analyze(text)

        self.assertIsInstance(analysis.suggestions, list)
        self.assertTrue(len(analysis.suggestions) > 0)

    def test_fca_compliance_check(self):
        """Test FCA compliance tone check"""
        compliant = "Investment carries risk. Past performance not indicative."
        non_compliant = "Guaranteed profits with no risk!"

        is_compliant1, issues1 = self.analyzer.is_fca_compliant_tone(compliant)
        is_compliant2, issues2 = self.analyzer.is_fca_compliant_tone(non_compliant)

        self.assertTrue(is_compliant1)
        self.assertEqual(len(issues1), 0)

        self.assertFalse(is_compliant2)
        self.assertGreater(len(issues2), 0)

    def test_polarity_calculation(self):
        """Test polarity score calculation"""
        positive_text = "Excellent service with great benefits and positive outcomes."
        negative_text = "Poor performance with significant risks and potential losses."

        positive_score = self.analyzer.calculate_polarity(positive_text)
        negative_score = self.analyzer.calculate_polarity(negative_text)

        self.assertGreater(positive_score, negative_score)
        self.assertGreaterEqual(positive_score, -1.0)
        self.assertLessEqual(positive_score, 1.0)

    def test_singleton_pattern(self):
        """Test singleton accessor"""
        analyzer1 = get_sentiment_analyzer()
        analyzer2 = get_sentiment_analyzer()

        self.assertIs(analyzer1, analyzer2)


if __name__ == '__main__':
    unittest.main()
