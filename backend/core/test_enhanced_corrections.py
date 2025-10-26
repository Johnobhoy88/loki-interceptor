"""
Comprehensive Test Suite for Enhanced Correction System
Tests all new patterns across all modules
"""
import sys
sys.path.insert(0, '/home/user/loki-interceptor/backend/core')

from corrector import DocumentCorrector

def test_fca_corrections():
    """Test FCA UK corrections"""
    print("\n" + "="*70)
    print("TEST 1: FCA UK CORRECTIONS")
    print("="*70)

    text = """
    Investment Opportunity

    You must purchase this product for guaranteed risk-free returns.
    High returns with no risk! This is suitable for you.
    """

    validation_results = {
        'validation': {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'cross_cutting_rules': {'status': 'FAIL', 'severity': 'critical'},
                        'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'},
                        'no_implicit_advice': {'status': 'FAIL', 'severity': 'critical'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    print(f"✓ Corrections applied: {result['correction_count']}")
    print(f"✓ Strategies used: {', '.join(result['strategies_applied'])}")
    print(f"✓ Validation: {'PASS' if result['validation']['valid'] else 'FAIL'}")

    # Check specific changes
    if 'must purchase' not in result['corrected']:
        print("✓ Removed coercive language")
    if 'not financial advice' in result['corrected'].lower():
        print("✓ Added advice disclaimer")

    return result['correction_count'] > 0

def test_gdpr_corrections():
    """Test GDPR UK corrections"""
    print("\n" + "="*70)
    print("TEST 2: GDPR UK CORRECTIONS")
    print("="*70)

    text = """
    Privacy Policy

    By using this website, you automatically agree to our data collection.
    We process your personal data for various purposes.
    """

    validation_results = {
        'validation': {
            'modules': {
                'gdpr_uk': {
                    'gates': {
                        'consent': {'status': 'FAIL', 'severity': 'critical'},
                        'lawful_basis': {'status': 'FAIL', 'severity': 'critical'},
                        'rights': {'status': 'WARNING', 'severity': 'high'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    print(f"✓ Corrections applied: {result['correction_count']}")
    print(f"✓ Unchanged: {result['unchanged']}")

    # Check specific changes
    if 'automatically agree' not in result['corrected']:
        print("✓ Removed forced consent")
    if 'explicit consent' in result['corrected'].lower():
        print("✓ Added proper consent language")

    return result['correction_count'] > 0

def test_tax_corrections():
    """Test Tax UK corrections"""
    print("\n" + "="*70)
    print("TEST 3: TAX UK CORRECTIONS")
    print("="*70)

    text = """
    VAT Information

    The VAT registration threshold is £85,000.
    You need to register with LLC.
    """

    validation_results = {
        'validation': {
            'modules': {
                'tax_uk': {
                    'gates': {
                        'vat_threshold': {'status': 'FAIL', 'severity': 'medium'},
                        'legal_entity_name': {'status': 'FAIL', 'severity': 'high'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    print(f"✓ Corrections applied: {result['correction_count']}")
    print(f"✓ VAT threshold updated: {'£90,000' in result['corrected']}")
    print(f"✓ LLC corrected: {'LLC' not in result['corrected']}")

    return result['correction_count'] > 0

def test_nda_corrections():
    """Test NDA UK corrections"""
    print("\n" + "="*70)
    print("TEST 4: NDA UK CORRECTIONS")
    print("="*70)

    text = """
    Non-Disclosure Agreement

    This agreement covers confidential information in perpetuity.
    """

    validation_results = {
        'validation': {
            'modules': {
                'nda_uk': {
                    'gates': {
                        'duration_reasonableness': {'status': 'FAIL', 'severity': 'medium'},
                        'protected_whistleblowing': {'status': 'FAIL', 'severity': 'critical'},
                        'consideration': {'status': 'FAIL', 'severity': 'critical'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    print(f"✓ Corrections applied: {result['correction_count']}")
    print(f"✓ Duration fixed: {'perpetuity' not in result['corrected']}")

    return result['correction_count'] > 0

def test_hr_corrections():
    """Test HR Scottish corrections"""
    print("\n" + "="*70)
    print("TEST 5: HR SCOTTISH CORRECTIONS")
    print("="*70)

    text = """
    Disciplinary Notice

    This is your final warning. You may not bring a lawyer.
    You must attend alone.
    """

    validation_results = {
        'validation': {
            'modules': {
                'hr_scottish': {
                    'gates': {
                        'accompaniment': {'status': 'FAIL', 'severity': 'critical'},
                        'informal_threats': {'status': 'FAIL', 'severity': 'high'}
                    }
                }
            }
        }
    }

    corrector = DocumentCorrector()
    result = corrector.correct_document(text, validation_results)

    print(f"✓ Corrections applied: {result['correction_count']}")
    print(f"✓ Lawyer restriction removed: {'may not bring a lawyer' not in result['corrected'].lower()}")

    return result['correction_count'] > 0

def test_multi_level():
    """Test multi-level correction"""
    print("\n" + "="*70)
    print("TEST 6: MULTI-LEVEL CORRECTION")
    print("="*70)

    text = "Investment with guaranteed returns of 10%. VAT is £85,000."

    validation_results = {
        'validation': {
            'modules': {
                'fca_uk': {
                    'gates': {
                        'fair_clear_not_misleading': {'status': 'FAIL', 'severity': 'critical'}
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
    result = corrector.correct_document(
        text,
        validation_results,
        advanced_options={'multi_level': True}
    )

    print(f"✓ Multi-level: {result.get('multi_level', False)}")
    print(f"✓ Corrections: {result['correction_count']}")
    print(f"✓ Deterministic: {result['determinism']['repeatable']}")

    return result['correction_count'] > 0

def main():
    """Run all tests"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*15 + "ENHANCED CORRECTION SYSTEM TEST SUITE" + " "*16 + "║")
    print("╚" + "═"*68 + "╝")

    tests = [
        ("FCA UK", test_fca_corrections),
        ("GDPR UK", test_gdpr_corrections),
        ("Tax UK", test_tax_corrections),
        ("NDA UK", test_nda_corrections),
        ("HR Scottish", test_hr_corrections),
        ("Multi-Level", test_multi_level)
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} FAILED: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, p in results if p)
    total = len(results)

    for name, passed_test in results:
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status:10} {name}")

    print("="*70)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - ENHANCED SYSTEM OPERATIONAL")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        return 1

if __name__ == '__main__':
    exit(main())
