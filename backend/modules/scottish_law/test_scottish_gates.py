"""
Test Suite for Scottish Law Compliance Gates

Tests all 5 Scottish-specific compliance gates with comprehensive test cases
demonstrating detection of Scots law differences.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scottish_law.gates.scottish_employment import ScottishEmploymentGate
from scottish_law.gates.scottish_contracts import ScottishContractsGate
from scottish_law.gates.scottish_data_protection import ScottishDataProtectionGate
from scottish_law.gates.scottish_property import ScottishPropertyGate
from scottish_law.gates.scottish_corporate import ScottishCorporateGate


def test_gate(gate, test_cases, gate_name):
    """Test a gate with provided test cases"""
    print(f"\n{'='*80}")
    print(f"Testing: {gate_name}")
    print(f"{'='*80}")

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        result = gate.check(test_case['text'], 'contract')

        print(f"Status: {result['status']}")
        print(f"Message: {result.get('message', 'N/A')}")

        if 'issues' in result:
            print(f"\nIssues Detected ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"  - {issue}")

        if 'corrections' in result:
            print(f"\nCorrections/Suggestions ({len(result['corrections'])}):")
            for correction in result['corrections']:
                print(f"  Type: {correction['type']}")
                print(f"  Suggestion: {correction['suggestion']}")
                if 'correction' in correction:
                    print(f"  Correction: {correction['correction']}")
                print(f"  Citation: {correction['citation']}")
                print()


def run_all_tests():
    """Run all Scottish law gate tests"""
    print("\n" + "="*80)
    print("SCOTTISH LAW COMPLIANCE GATES - COMPREHENSIVE TEST SUITE")
    print("="*80)

    # Test 1: Scottish Employment Gate
    employment_gate = ScottishEmploymentGate()
    employment_tests = [
        {
            'name': 'Scottish employment with 6-year limitation (FAIL)',
            'text': 'This employment contract is governed by Scots law. Claims must be brought within six years of the breach.'
        },
        {
            'name': 'Employment Tribunal without Scotland specification (FAIL)',
            'text': 'This Scottish employment contract disputes may be referred to the Employment Tribunal.'
        },
        {
            'name': 'ACAS without Scotland specification (WARNING)',
            'text': 'Scottish employees should contact ACAS for early conciliation before tribunal claims.'
        },
        {
            'name': 'Correct Scottish employment reference (PASS)',
            'text': 'Employment Tribunal Scotland handles claims. ACAS Scotland provides early conciliation. Claims have a 5-year prescription period under Scots law.'
        }
    ]
    test_gate(employment_gate, employment_tests, "Scottish Employment Gate")

    # Test 2: Scottish Contracts Gate
    contracts_gate = ScottishContractsGate()
    contracts_tests = [
        {
            'name': 'Scottish contract with consideration clause (FAIL)',
            'text': 'This Agreement is governed by Scots law. In consideration of £1 and other valuable consideration, the parties agree to the following terms.'
        },
        {
            'name': 'Subject to contract in Scotland (FAIL)',
            'text': 'This agreement is subject to contract and governed by the law of Scotland and Scots law applies.'
        },
        {
            'name': 'English Third Party Rights Act in Scottish contract (FAIL)',
            'text': 'This contract is governed by Scots law. Third parties may enforce rights under the Contracts (Rights of Third Parties) Act 1999.'
        },
        {
            'name': 'Proper Scottish contract with consensus in idem (PASS)',
            'text': 'This Agreement is governed by Scots law. The parties have reached consensus in idem. Third party rights are governed by jus quaesitum tertio and the Contract (Third Party Rights) (Scotland) Act 2017.'
        }
    ]
    test_gate(contracts_gate, contracts_tests, "Scottish Contracts Gate")

    # Test 3: Scottish Data Protection Gate
    data_protection_gate = ScottishDataProtectionGate()
    data_protection_tests = [
        {
            'name': 'Scottish public authority with UK FOI Act (FAIL)',
            'text': 'This Scottish council complies with the Freedom of Information Act 2000 and reports to the ICO for FOI matters.'
        },
        {
            'name': 'Correct Scottish FOI reference (PASS)',
            'text': 'Scottish public authorities must comply with the Freedom of Information (Scotland) Act 2002 and are overseen by the Scottish Information Commissioner for FOI matters.'
        },
        {
            'name': 'Scottish public body without records management plan (WARNING)',
            'text': 'This Scottish Government agency is a Scottish public authority that processes personal data under UK GDPR.'
        }
    ]
    test_gate(data_protection_gate, data_protection_tests, "Scottish Data Protection Gate")

    # Test 4: Scottish Property Gate
    property_gate = ScottishPropertyGate()
    property_tests = [
        {
            'name': 'Freehold property in Scotland (FAIL)',
            'text': 'This freehold property in Scotland is registered with the Land Registry and subject to Scots law.'
        },
        {
            'name': 'English AST in Scottish context (FAIL)',
            'text': 'This Assured Shorthold Tenancy agreement is for a residential property in Edinburgh, Scotland.'
        },
        {
            'name': 'Section 21 eviction in Scotland (FAIL)',
            'text': 'The Scottish landlord issued a Section 21 notice to evict the tenant from the property.'
        },
        {
            'name': 'Exchange of contracts in Scotland (FAIL)',
            'text': 'Upon exchange of contracts, the sale of this Scottish property will be complete under Scots law.'
        },
        {
            'name': 'Correct Scottish property terminology (PASS)',
            'text': 'This heritable property in Scotland is registered with Registers of Scotland. The Private Residential Tenancy is governed by Scots law and the Private Housing (Tenancies) (Scotland) Act 2016.'
        }
    ]
    test_gate(property_gate, property_tests, "Scottish Property Gate")

    # Test 5: Scottish Corporate Gate
    corporate_gate = ScottishCorporateGate()
    corporate_tests = [
        {
            'name': 'Scottish charity with Charity Commission reference (FAIL)',
            'text': 'This Scottish charity is registered with the Charity Commission in Scotland. Charity Number: 123456.'
        },
        {
            'name': 'Correct Scottish charity reference (PASS)',
            'text': 'This Scottish charity is registered with OSCR (Office of the Scottish Charity Regulator). Scottish Charity Number: SC012345.'
        },
        {
            'name': 'Scottish Limited Partnership (WARNING)',
            'text': 'This Scottish Limited Partnership operates in Scotland under Scots law and is registered with Companies House.'
        },
        {
            'name': 'SCIO reference (PASS)',
            'text': 'This SCIO (Scottish Charitable Incorporated Organisation) is registered with OSCR in Scotland.'
        }
    ]
    test_gate(corporate_gate, corporate_tests, "Scottish Corporate Gate")

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)


def print_summary():
    """Print summary of Scottish law gates"""
    print("\n" + "="*80)
    print("SCOTTISH LAW COMPLIANCE GATES - SUMMARY")
    print("="*80)

    print("""
1. SCOTTISH EMPLOYMENT GATE
   Key Detections:
   - 5-year prescription period (not 6-year limitation)
   - Employment Tribunal Scotland (not generic ET)
   - ACAS Scotland specification
   - Scots employment contract formation
   - Early conciliation requirements

2. SCOTTISH CONTRACTS GATE
   Key Detections:
   - Consideration clauses (not required in Scots law)
   - "Subject to contract" warnings (may not prevent binding contract)
   - Consensus in idem vs offer and acceptance
   - Jus quaesitum tertio (third-party rights)
   - English Third Party Rights Act 1999 (not applicable)
   - Deed execution (not required in Scotland)

3. SCOTTISH DATA PROTECTION GATE
   Key Detections:
   - Scottish Information Commissioner for FOI matters
   - FOI (Scotland) Act 2002 vs UK FOIA 2000
   - Public Records (Scotland) Act 2011
   - Environmental Information (Scotland) Regulations 2004
   - Records Management Plans (Scottish public authorities)
   - National Records of Scotland

4. SCOTTISH PROPERTY GATE
   Key Detections:
   - "Freehold" terminology (should be "heritable property")
   - "Leasehold" terminology differences
   - Registers of Scotland (not Land Registry)
   - Private Residential Tenancy (not AST)
   - Section 21 eviction (not applicable in Scotland)
   - Conclusion of missives (not exchange of contracts)
   - Home Report requirements
   - Scottish deposit protection schemes

5. SCOTTISH CORPORATE GATE
   Key Detections:
   - OSCR (not Charity Commission) for charities
   - Scottish Charity Numbers (SC prefix)
   - SCIO (Scottish Charitable Incorporated Organisation)
   - Scottish Limited Partnerships
   - Scottish partnerships (separate legal personality)
   - Companies House Scotland procedures
   - Scottish insolvency procedures
    """)

    print("="*80)


if __name__ == '__main__':
    print_summary()
    run_all_tests()

    print("\n\nTo run individual gate tests:")
    print("  from scottish_law.gates.scottish_employment import ScottishEmploymentGate")
    print("  gate = ScottishEmploymentGate()")
    print("  result = gate.check('Your text here', 'contract')")
