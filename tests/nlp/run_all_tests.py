#!/usr/bin/env python3
"""
NLP Test Runner
Run all NLP module tests and generate report
"""

import unittest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import test modules
from test_semantic_matcher import TestSemanticMatcher
from test_entity_recognizer import TestEntityRecognizer
from test_readability import TestReadabilityScorer
from test_sentiment import TestSentimentAnalyzer


def run_nlp_tests():
    """Run all NLP tests and generate report"""

    print("=" * 70)
    print("LOKI INTERCEPTOR - NLP MODULE TEST SUITE")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticMatcher))
    suite.addTests(loader.loadTestsFromTestCase(TestEntityRecognizer))
    suite.addTests(loader.loadTestsFromTestCase(TestReadabilityScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestSentimentAnalyzer))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_nlp_tests()
    sys.exit(exit_code)
