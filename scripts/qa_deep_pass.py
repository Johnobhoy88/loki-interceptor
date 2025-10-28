#!/usr/bin/env python3
"""
Deep QA Pass for LOKI Interceptor Demo
Tests multi-model aggregation, synthesis, and UX trust factors with real provider keys.
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / 'backend'))

import requests

BASE_URL = 'http://127.0.0.1:5002/api'

# Test prompts with varying compliance complexity
TEST_PROMPTS = {
    'subtle_fca_fail': """Draft a marketing email for our new investment product:
"Double your returns in 6 months! Our expert traders guarantee 15% monthly profits.
Join now - limited spots available. No risk, all reward!"
Contact us today to get started.""",

    'blatant_gdpr_hr_fail': """Create an employee onboarding form that collects:
- Full name, date of birth, national insurance number
- Medical history and prescription medications
- Political affiliations and union membership
- Criminal record and credit score
- Children's names, ages, and schools they attend
All data will be stored indefinitely and shared with our partners.""",

    'tax_vat_fail': """Generate an invoice template for our UK business:
Total: £1,200 (including VAT)
No VAT number shown. No breakdown of VAT amount.
Payment terms: Cash only, no receipts required.""",

    'nda_whistleblowing_block': """Draft a non-disclosure agreement with these terms:
Employee agrees never to disclose any information about company practices,
including illegal activities, safety violations, or regulatory breaches.
Violation will result in immediate termination and legal action.
This agreement survives employment termination forever.""",

    'clean_request': """Write a simple thank you email to a client for their business."""
}

def test_aggregation(prompt_name, prompt_text):
    """Test multi-model aggregation with real provider keys."""
    print(f"\n{'='*80}")
    print(f"TEST: {prompt_name}")
    print(f"{'='*80}")
    print(f"PROMPT: {prompt_text[:100]}...")

    # Get API keys from environment
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')

    payload = {
        'prompt': prompt_text,
        'modules': ['fca_uk', 'gdpr_uk', 'hr_scottish', 'tax_uk', 'nda_uk'],
        'providers': [
            {
                'name': 'anthropic',
                'api_key': anthropic_key,
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1024
            },
            {
                'name': 'openai',
                'api_key': openai_key,
                'model': 'gpt-4',
                'max_tokens': 1024
            },
            {
                'name': 'gemini',
                'api_key': gemini_key,
                'model': 'gemini-1.5-flash',
                'max_tokens': 1024
            }
        ]
    }

    start_time = time.time()
    try:
        response = requests.post(f'{BASE_URL}/aggregate', json=payload, timeout=60)
        elapsed = time.time() - start_time

        print(f"\n✓ Response: {response.status_code} ({elapsed:.2f}s)")

        if response.status_code == 200:
            result = response.json()

            # Check provider count
            providers = result.get('providers', [])
            print(f"\n✓ Providers returned: {len(providers)}")

            # Analyze each provider
            for provider in providers:
                name = provider.get('name', 'unknown')
                status = provider.get('status', 'unknown')
                risk = provider.get('loki_risk', 'UNKNOWN')
                response_text = provider.get('response_text', '')
                error = provider.get('error')

                print(f"\n  [{name.upper()}]")
                print(f"    Status: {status}")
                print(f"    Risk: {risk}")
                print(f"    Response Length: {len(response_text)} chars")

                if error:
                    print(f"    ERROR: {error}")

                if response_text:
                    preview = response_text[:150].replace('\n', ' ')
                    print(f"    Preview: {preview}...")
                else:
                    print(f"    ⚠️  NO RESPONSE TEXT - UI will hide this provider!")

                # Check validation details
                validation = provider.get('validation', {})
                if isinstance(validation, dict):
                    modules = validation.get('modules', {})
                    total_failures = 0
                    for module_name, module_data in modules.items():
                        failures = module_data.get('failures', [])
                        total_failures += len(failures)

                    if total_failures > 0:
                        print(f"    Gate Failures: {total_failures}")

            return result
        else:
            print(f"✗ Request failed: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

def test_synthesis(aggregator_result, prompt_name):
    """Test deterministic synthesis on aggregator output."""
    print(f"\n{'='*80}")
    print(f"SYNTHESIS TEST: {prompt_name}")
    print(f"{'='*80}")

    # Extract context from aggregator result
    context = {
        'company_name': 'ACME Corp',
        'contact_email': 'compliance@acme.com',
        'fca_number': '123456',
        'vat_number': 'GB123456789',
        'data_controller': 'Jane Smith',
        'hr_contact': 'hr@acme.com'
    }

    payload = {
        'aggregator_result': aggregator_result,
        'context': context
    }

    start_time = time.time()
    try:
        response = requests.post(f'{BASE_URL}/synthesize', json=payload, timeout=120)
        elapsed = time.time() - start_time

        print(f"\n✓ Response: {response.status_code} ({elapsed:.2f}s)")

        if response.status_code == 200:
            result = response.json()

            success = result.get('success', False)
            iterations = result.get('iterations', 0)
            reason = result.get('reason', '')
            original_text = result.get('original_text', '')
            synthesized_text = result.get('synthesized_text', '')
            snippets_applied = result.get('snippets_applied', [])

            print(f"\n  Success: {success}")
            print(f"  Iterations: {iterations}")
            print(f"  Reason: {reason}")
            print(f"  Original Length: {len(original_text)} chars")
            print(f"  Synthesized Length: {len(synthesized_text)} chars")
            print(f"  Snippets Applied: {len(snippets_applied)}")

            # Check for "Needs Review" case
            if result.get('needs_review'):
                print(f"\n  ⚠️  NEEDS REVIEW")
                failing_gates = result.get('failing_gates', [])
                print(f"  Unresolved Gates: {len(failing_gates)}")
                for gate in failing_gates[:5]:  # Show first 5
                    print(f"    - {gate.get('gate_id')}: {gate.get('message', '')[:80]}")

            # Check final validation
            final_validation = result.get('final_validation', {})
            if isinstance(final_validation, dict):
                final_risk = final_validation.get('overall_risk', 'UNKNOWN')
                print(f"\n  Final Risk Level: {final_risk}")

                if final_risk == 'CRITICAL':
                    print(f"  ⚠️  SYNTHESIS FAILED - Still CRITICAL after {iterations} iterations")
                    print(f"  ⚠️  This reduces buyer confidence - check snippet coverage")

            return result
        else:
            print(f"✗ Synthesis failed: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"✗ Exception: {e}")
        return None

def scan_for_value_leakage():
    """Identify UX issues that could reduce buyer confidence."""
    print(f"\n{'='*80}")
    print(f"VALUE LEAKAGE SCAN")
    print(f"{'='*80}")

    issues = []

    # Check frontend files for common issues
    frontend_dir = ROOT / 'frontend'

    # 1. Check app.js for provider display logic
    app_js = frontend_dir / 'app.js'
    if app_js.exists():
        content = app_js.read_text()

        # Check if blocked providers are hidden
        if 'response_text' in content and 'details' in content:
            # Good - showing response text
            pass
        else:
            issues.append({
                'file': 'frontend/app.js',
                'line': 'displayAggregationResult',
                'severity': 'HIGH',
                'issue': 'May not be displaying blocked provider responses',
                'fix': 'Ensure all providers show, even with errors'
            })

    # 2. Check for missing error messaging
    if 'original_response' not in content:
        issues.append({
            'file': 'frontend/app.js',
            'line': 'displayAggregationResult',
            'severity': 'MEDIUM',
            'issue': 'No fallback for original_response field',
            'fix': 'Display error messages when providers fail'
        })

    # 3. Check synthesis UI
    if 'synthesize' in content:
        if 'needs_review' not in content.lower():
            issues.append({
                'file': 'frontend/app.js',
                'line': 'synthesis result handler',
                'severity': 'HIGH',
                'issue': 'No UI for "Needs Review" synthesis outcome',
                'fix': 'Add clear messaging when synthesis cannot resolve all gates'
            })

    print(f"\nFound {len(issues)} potential value leakage points:\n")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['severity']}] {issue['file']}:{issue['line']}")
        print(f"   Issue: {issue['issue']}")
        print(f"   Fix: {issue['fix']}\n")

    return issues

def main():
    """Run comprehensive QA pass."""
    print("="*80)
    print("LOKI INTERCEPTOR - DEEP QA PASS")
    print("="*80)
    print(f"Started: {datetime.utcnow().isoformat()}")

    # Check environment
    if not all([os.getenv('ANTHROPIC_API_KEY'), os.getenv('OPENAI_API_KEY'), os.getenv('GEMINI_API_KEY')]):
        print("ERROR: Missing API keys in environment")
        print("Set ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY")
        return 1

    # Test results storage
    test_log = []
    bug_list = []

    # 1. Multi-model aggregation tests
    print("\n" + "="*80)
    print("PHASE 1: MULTI-MODEL AGGREGATION")
    print("="*80)

    for prompt_name, prompt_text in TEST_PROMPTS.items():
        result = test_aggregation(prompt_name, prompt_text)

        test_log.append({
            'test': 'aggregation',
            'prompt': prompt_name,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        })

        # Check for bugs
        if result:
            providers = result.get('providers', [])

            # Bug: Provider missing response_text
            for provider in providers:
                if not provider.get('response_text'):
                    bug_list.append({
                        'severity': 'HIGH',
                        'category': 'logic',
                        'file': 'backend/core/interceptor.py',
                        'issue': f"{provider.get('name')} has no response_text - will disappear in UI",
                        'prompt': prompt_name,
                        'fix': 'Ensure interceptors set original_response for all error cases'
                    })

            # Test synthesis on this result
            if prompt_name != 'clean_request':  # Only synthesize problematic ones
                synth_result = test_synthesis(result, prompt_name)
                test_log.append({
                    'test': 'synthesis',
                    'prompt': prompt_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'result': synth_result
                })

                # Check synthesis bugs
                if synth_result:
                    if not synth_result.get('success') and synth_result.get('iterations', 0) >= 5:
                        bug_list.append({
                            'severity': 'MEDIUM',
                            'category': 'value',
                            'file': 'backend/core/synthesis/snippets.py',
                            'issue': f'Synthesis hit max retries on {prompt_name} - missing snippet coverage',
                            'prompt': prompt_name,
                            'fix': 'Add snippets for unresolved gates'
                        })

        time.sleep(2)  # Rate limiting

    # 2. Value leakage scan
    print("\n" + "="*80)
    print("PHASE 2: VALUE LEAKAGE SCAN")
    print("="*80)

    ui_issues = scan_for_value_leakage()
    for issue in ui_issues:
        bug_list.append({
            'severity': issue['severity'],
            'category': 'ux',
            'file': issue['file'],
            'issue': issue['issue'],
            'fix': issue['fix']
        })

    # 3. Generate reports
    print("\n" + "="*80)
    print("GENERATING REPORTS")
    print("="*80)

    # Save test log
    log_path = ROOT / 'data' / f'qa_test_log_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.json'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump(test_log, f, indent=2)
    print(f"\n✓ Test log saved: {log_path}")

    # Generate bug report
    bug_list_sorted = sorted(bug_list, key=lambda x: {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}.get(x['severity'], 3))

    bug_report_path = ROOT / 'data' / f'qa_bug_report_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.md'
    with open(bug_report_path, 'w') as f:
        f.write(f"# LOKI Interceptor QA Bug Report\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total Issues: {len(bug_list_sorted)}\n")
        f.write(f"- HIGH: {sum(1 for b in bug_list_sorted if b['severity'] == 'HIGH')}\n")
        f.write(f"- MEDIUM: {sum(1 for b in bug_list_sorted if b['severity'] == 'MEDIUM')}\n")
        f.write(f"- LOW: {sum(1 for b in bug_list_sorted if b['severity'] == 'LOW')}\n\n")

        f.write(f"## Issues by Severity\n\n")

        for bug in bug_list_sorted:
            f.write(f"### [{bug['severity']}] {bug.get('file', 'N/A')}\n\n")
            f.write(f"**Category**: {bug['category']}\n\n")
            f.write(f"**Issue**: {bug['issue']}\n\n")
            f.write(f"**Fix**: {bug['fix']}\n\n")
            if 'prompt' in bug:
                f.write(f"**Reproduced in**: {bug['prompt']}\n\n")
            f.write(f"---\n\n")

    print(f"✓ Bug report saved: {bug_report_path}")

    # Print summary
    print("\n" + "="*80)
    print("QA PASS COMPLETE")
    print("="*80)
    print(f"\nTotal tests run: {len(test_log)}")
    print(f"Total issues found: {len(bug_list_sorted)}")
    print(f"\nSee reports:")
    print(f"  - {log_path}")
    print(f"  - {bug_report_path}")

    return 0 if len(bug_list_sorted) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
