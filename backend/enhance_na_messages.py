#!/usr/bin/env python3
"""
Script to enhance all gates with helpful N/A messages
"""

GATE_NA_MESSAGES = {
    'complaint_route_clock': 'Not applicable - document does not contain complaint handling procedures',
    'fos_signposting': 'Not applicable - document does not discuss complaint procedures (FOS signposting required in complaint contexts)',
    'distribution_controls': 'Not applicable - document does not describe intermediary or third-party distribution arrangements',
    'personal_dealing': 'Not applicable - document does not address employee or staff personal trading/dealing',
    'record_keeping': 'Not applicable - document does not discuss record retention or documentation policies',
    'inducements_referrals': 'Not applicable - document does not mention commissions, referrals, or inducement arrangements',
    'third_party_banks': 'Not applicable - document does not reference third-party banking arrangements',
    'reasonable_adjustments': 'Not applicable - document does not address disability, accessibility, or customer support accommodations',
    'vulnerability_identification': 'Not applicable - document does not contain vulnerability indicators or customer support context',
    'outcomes_coverage': 'Not applicable - document is not a full product/service communication requiring Consumer Duty outcomes',
    'cross_cutting_rules': 'Not applicable - document is too short or does not involve substantial product/customer decisions',
    'no_implicit_advice': 'Not applicable - document does not contain recommendation or advisory language',
    'promotions_approval': 'Not applicable - document is not a financial promotion or lacks promotional content',
    'finfluencer_controls': 'Not applicable - document does not reference social media or influencer marketing',
    'target_market_definition': 'Not applicable - document does not discuss product design or target markets',
    'defined_roles': 'Not applicable - document does not describe processes, procedures, or accountability structures',
    'comprehension_aids': 'Not applicable - document does not contain complex financial information requiring comprehension aids',
    'conflicts_declaration': 'Not applicable - document does not provide advice or recommendations requiring conflict disclosure',
    'client_money_segregation': 'Not applicable - document does not mention holding or handling client money',
    'fair_clear_not_misleading': 'Not applicable - document is not promotional or does not make financial claims',
    'risk_benefit_balance': 'Not applicable - document does not present product benefits or features',
    'fair_value': 'Not applicable - document does not discuss pricing or fees',
    'fair_value_assessment_ref': 'Not applicable - document does not discuss pricing or product value',
    'support_journey': 'Not applicable - document does not describe customer support, cancellation, or service processes',
    'target_audience': 'Not applicable - document is not a financial promotion or does not specify audience',
}

print("N/A Message Enhancement Guide")
print("=" * 70)
print()
print("Add these enhanced N/A returns to each gate's _is_relevant check:")
print()

for gate_name, message in sorted(GATE_NA_MESSAGES.items()):
    print(f"{gate_name}:")
    print(f"    return {{")
    print(f"        'status': 'N/A',")
    print(f"        'message': '{message}',")
    print(f"        'legal_source': self.legal_source")
    print(f"    }}")
    print()
