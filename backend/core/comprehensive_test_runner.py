"""
Comprehensive LOKI Correction System Test Suite
Tests pattern coverage, determinism, performance, and integration
"""
import sys
import time
import hashlib
import json
sys.path.insert(0, '/home/user/loki-interceptor/backend/core')

from corrector import DocumentCorrector
from correction_patterns import CorrectionPatternRegistry

# ===========================================
# TEST 1: Pattern Coverage Verification
# ===========================================

def test_pattern_coverage():
    """Verify all 107 patterns are present"""
    print("\n" + "="*70)
    print("TEST 1: PATTERN COVERAGE VERIFICATION")
    print("="*70)

    registry = CorrectionPatternRegistry()

    # Count regex patterns
    regex_count = sum(len(patterns) for patterns in registry.regex_patterns.values())

    # Count template patterns
    template_count = sum(len(templates) for templates in registry.templates.values())

    # Count structural rules
    structural_count = sum(len(rules) for rules in registry.structural_rules.values())

    total = regex_count + template_count + structural_count

    print(f"Regex patterns: {regex_count}")
    print(f"Template patterns: {template_count}")
    print(f"Structural rules: {structural_count}")
    print(f"Total patterns: {total}")

    # Check module coverage
    modules = {
        'FCA UK': ['risk_benefit', 'risk_warning', 'fair_clear', 'cross_cutting', 'finfluencer'],
        'GDPR UK': ['consent', 'cookies'],
        'Tax UK': ['vat_threshold', 'legal_entity_name', 'hmrc_scam'],
        'NDA UK': ['duration'],
        'HR Scottish': ['accompaniment_restrictions', 'suspension', 'informal_threats']
    }

    print("\nModule Coverage:")
    for module, expected_patterns in modules.items():
        found = [p for p in expected_patterns if p in registry.regex_patterns or p in registry.templates]
        print(f"  {module}: {len(found)}/{len(expected_patterns)} patterns found")

    # Verify expected total
    expected_total = 107  # 26 regex + 80 templates + 1 structural
    status = "✓ PASS" if total == expected_total else f"✗ FAIL (expected {expected_total})"
    print(f"\nPattern Count: {status}")

    return {
        'passed': total == expected_total,
        'regex': regex_count,
        'templates': template_count,
        'structural': structural_count,
        'total': total
    }

# ===========================================
# TEST 2: Determinism Testing
# ===========================================

def test_determinism():
    """Test that corrections are deterministic (same input = same output)"""
    print("\n" + "="*70)
    print("TEST 2: DETERMINISM TESTING")
    print("="*70)

    text = """
    Investment Opportunity

    Guaranteed returns of 10% with no risk! This is suitable for you.
    By using our service, you agree to share your data.
    VAT threshold is £85,000.
    """

    validation_results = {
        'validation': {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'}
                    }
                },
                'gdpr_uk': {
                    'gates': {
                        'consent': {'status': 'FAIL', 'severity': 'critical'}
                    }
                },
                'tax_uk': {
                    'gates': {
                        'vat_threshold': {'status': 'FAIL', 'severity': 'medium'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()

    # Run correction 3 times
    results = []
    hashes = []

    for i in range(3):
        result = corrector.correct_document(text, validation_results)
        corrected_text = result['corrected']

        # Generate hash of corrected text
        text_hash = hashlib.sha256(corrected_text.encode()).hexdigest()
        hashes.append(text_hash)
        results.append(result)

        print(f"\nRun {i+1}:")
        print(f"  Corrections: {result['correction_count']}")
        print(f"  Hash: {text_hash[:16]}...")

    # Check if all hashes are identical
    all_identical = len(set(hashes)) == 1

    print(f"\nAll outputs identical: {all_identical}")
    print(f"Hash consistency: {'✓ PASS' if all_identical else '✗ FAIL'}")

    if all_identical:
        print(f"Determinism verified: SHA-256 = {hashes[0][:32]}...")

    return {
        'passed': all_identical,
        'runs': 3,
        'hashes': hashes,
        'identical': all_identical
    }

# ===========================================
# TEST 3: Performance Testing
# ===========================================

def test_performance():
    """Test correction speed on different document sizes"""
    print("\n" + "="*70)
    print("TEST 3: PERFORMANCE TESTING")
    print("="*70)

    corrector = DocumentCorrector()

    # Small document (500 chars)
    small_text = """
    Investment Product
    Guaranteed returns with no risk! You must purchase now.
    By using this website, you agree to data collection.
    """ * 2

    # Medium document (5000 chars)
    medium_text = small_text * 10

    # Large document (50000 chars)
    large_text = medium_text * 10

    validation_results = {
        'validation': {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'},
                        'cross_cutting_rules': {'status': 'FAIL', 'severity': 'critical'}
                    }
                },
                'gdpr_uk': {
                    'gates': {
                        'consent': {'status': 'FAIL', 'severity': 'critical'}
                    }
                }
            }
        }
    }

    results = {}

    for size, text in [('small', small_text), ('medium', medium_text), ('large', large_text)]:
        start = time.time()
        result = corrector.correct_document(text, validation_results)
        elapsed = time.time() - start

        results[size] = {
            'elapsed': elapsed,
            'chars': len(text),
            'corrections': result['correction_count'],
            'chars_per_sec': len(text) / elapsed if elapsed > 0 else 0
        }

        print(f"\n{size.upper()} Document:")
        print(f"  Size: {len(text):,} characters")
        print(f"  Time: {elapsed:.4f} seconds")
        print(f"  Corrections: {result['correction_count']}")
        print(f"  Speed: {results[size]['chars_per_sec']:,.0f} chars/sec")

    # Performance threshold: should process at least 10,000 chars/sec
    passed = all(r['chars_per_sec'] > 10000 for r in results.values())

    print(f"\nPerformance: {'✓ PASS' if passed else '✗ FAIL'} (>10k chars/sec)")

    return {
        'passed': passed,
        'results': results
    }

# ===========================================
# TEST 4: Specific Pattern Tests
# ===========================================

def test_specific_patterns():
    """Test specific correction patterns from each module"""
    print("\n" + "="*70)
    print("TEST 4: SPECIFIC PATTERN VERIFICATION")
    print("="*70)

    corrector = DocumentCorrector()

    test_cases = [
        {
            'name': 'FCA - Guaranteed Returns',
            'text': 'Guaranteed returns of 10%',
            'validation': {
                'validation': {
                    'modules': {
                        'fca_uk': {
                            'gates': {
                                'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'guaranteed returns' not in r['corrected'].lower()
        },
        {
            'name': 'FCA - Risk Free',
            'text': 'Risk-free investment opportunity',
            'validation': {
                'validation': {
                    'modules': {
                        'fca_uk': {
                            'gates': {
                                'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'risk-free' not in r['corrected'].lower()
        },
        {
            'name': 'GDPR - Forced Consent',
            'text': 'By using this website, you automatically agree',
            'validation': {
                'validation': {
                    'modules': {
                        'gdpr_uk': {
                            'gates': {
                                'consent': {'status': 'FAIL', 'severity': 'critical'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'automatically agree' not in r['corrected'].lower()
        },
        {
            'name': 'Tax UK - VAT Threshold',
            'text': 'VAT threshold is £85,000',
            'validation': {
                'validation': {
                    'modules': {
                        'tax_uk': {
                            'gates': {
                                'vat_threshold': {'status': 'FAIL', 'severity': 'medium'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: '£90,000' in r['corrected']
        },
        {
            'name': 'Tax UK - LLC to Limited',
            'text': 'Register with ABC LLC',
            'validation': {
                'validation': {
                    'modules': {
                        'tax_uk': {
                            'gates': {
                                'legal_entity_name': {'status': 'FAIL', 'severity': 'high'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'LLC' not in r['corrected']
        },
        {
            'name': 'NDA UK - Perpetuity',
            'text': 'This agreement covers information in perpetuity',
            'validation': {
                'validation': {
                    'modules': {
                        'nda_uk': {
                            'gates': {
                                'duration_reasonableness': {'status': 'FAIL', 'severity': 'medium'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'perpetuity' not in r['corrected'].lower()
        },
        {
            'name': 'HR Scottish - Lawyer Restriction',
            'text': 'You may not bring a lawyer',
            'validation': {
                'validation': {
                    'modules': {
                        'hr_scottish': {
                            'gates': {
                                'accompaniment': {'status': 'FAIL', 'severity': 'critical'}
                            }
                        }
                    }
                }
            },
            'check': lambda r: 'may not bring a lawyer' not in r['corrected'].lower()
        }
    ]

    passed_tests = 0
    total_tests = len(test_cases)

    for test in test_cases:
        result = corrector.correct_document(test['text'], test['validation'])
        passed = test['check'](result)

        status = "✓" if passed else "✗"
        print(f"{status} {test['name']}: {'PASS' if passed else 'FAIL'}")

        if passed:
            passed_tests += 1

    print(f"\nSpecific Patterns: {passed_tests}/{total_tests} passed")

    return {
        'passed': passed_tests == total_tests,
        'total': total_tests,
        'passed_count': passed_tests
    }

# ===========================================
# TEST 5: Integration Test
# ===========================================

def test_integration():
    """Test integration with validation engine"""
    print("\n" + "="*70)
    print("TEST 5: INTEGRATION TESTING")
    print("="*70)

    try:
        # Test that corrector can work with validation results
        # (No need to import ValidationEngine as it's handled separately)
        corrector = DocumentCorrector()
        print("✓ DocumentCorrector instantiated successfully")

        text = "Guaranteed returns! By using this site, you agree to everything."

        validation_results = {
            'validation': {
                'modules': {
                    'fca_uk': {
                        'gates': {
                            'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'}
                        }
                    }
                }
            }
        }

        result = corrector.correct_document(text, validation_results)

        print(f"✓ Corrector processed validation results")
        print(f"✓ Applied {result['correction_count']} corrections")
        print(f"✓ Final validation: {result['validation']['valid']}")

        # Check result structure
        required_keys = ['corrected', 'original', 'correction_count', 'validation',
                        'determinism', 'strategies_applied']

        has_all_keys = all(key in result for key in required_keys)

        print(f"✓ Result has all required keys: {has_all_keys}")

        return {
            'passed': has_all_keys and result['correction_count'] > 0,
            'corrections': result['correction_count'],
            'valid': result['validation']['valid']
        }

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return {'passed': False, 'error': str(e)}

# ===========================================
# Main Test Runner
# ===========================================

def main():
    """Run all comprehensive tests"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*12 + "COMPREHENSIVE LOKI CORRECTION SYSTEM TESTS" + " "*15 + "║")
    print("╚" + "═"*68 + "╝")

    test_results = {}

    # Run all tests
    test_results['pattern_coverage'] = test_pattern_coverage()
    test_results['determinism'] = test_determinism()
    test_results['performance'] = test_performance()
    test_results['specific_patterns'] = test_specific_patterns()
    test_results['integration'] = test_integration()

    # Summary
    print("\n" + "="*70)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*70)

    tests = [
        ('Pattern Coverage', test_results['pattern_coverage']['passed']),
        ('Determinism', test_results['determinism']['passed']),
        ('Performance', test_results['performance']['passed']),
        ('Specific Patterns', test_results['specific_patterns']['passed']),
        ('Integration', test_results['integration']['passed'])
    ]

    passed = sum(1 for _, p in tests if p)
    total = len(tests)

    for name, passed_test in tests:
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status:10} {name}")

    print("="*70)
    print(f"TOTAL: {passed}/{total} test categories passed ({passed/total*100:.1f}%)")
    print("="*70)

    # Save results to JSON
    with open('/home/user/loki-interceptor/backend/core/test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)

    print("\nResults saved to: test_results.json")

    if passed == total:
        print("\n✓ ALL COMPREHENSIVE TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        return 0, test_results
    else:
        print(f"\n✗ {total - passed} test categories failed")
        return 1, test_results

if __name__ == '__main__':
    exit_code, results = main()
    sys.exit(exit_code)
