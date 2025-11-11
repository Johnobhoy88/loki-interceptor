"""
Employment Rights Act 2023 Compliance Checker
Validates compliance with Employment Rights Act 2023 provisions
"""

import re
from typing import Dict, List, Any


class EmploymentRightsAct2023Checker:
    """
    Validates compliance with Employment Rights Act 2023

    Key provisions:
    - Day-one flexible working rights (s.1)
    - Enhanced parental leave protections
    - Neonatal care leave
    - Carer's leave (1 week unpaid per year)
    - Tips and gratuities protections
    - Fire and rehire restrictions
    """

    def __init__(self):
        self.legal_source = "Employment Rights Act 2023"
        self.provisions = {
            'flexible_working_day_one': {
                'patterns': [
                    r'(?:day\s+one|from\s+(?:commencement|start)).*flexible\s+working',
                    r'all\s+employees.*flexible\s+working.*request',
                    r'flexible\s+working.*(?:immediate|no\s+qualifying)'
                ],
                'severity': 'high',
                'requirement': 'Flexible working request right from day one (no 26-week qualifying period)'
            },
            'carers_leave': {
                'patterns': [
                    r'carer(?:\'s)?.*leave',
                    r'(?:one|1)\s+week.*(?:carer|caring|dependant)',
                    r'unpaid.*carer'
                ],
                'severity': 'high',
                'requirement': '1 week unpaid carer\'s leave per year (day one right)'
            },
            'neonatal_care': {
                'patterns': [
                    r'neonatal.*leave',
                    r'(?:12|twelve)\s+weeks?.*(?:neonatal|NICU|special\s+care)'
                ],
                'severity': 'medium',
                'requirement': '12 weeks neonatal care leave for each parent'
            },
            'tips_protection': {
                'patterns': [
                    r'tips?.*(?:gratuities|service\s+charge)',
                    r'(?:retain|keep).*(?:tips?|gratuities)',
                    r'(?:fair|reasonable).*(?:distribution|allocation).*tips?'
                ],
                'severity': 'medium',
                'requirement': 'All tips must be passed to workers, fair allocation'
            },
            'fire_and_rehire': {
                'patterns': [
                    r'fire\s+and\s+rehire',
                    r'dismiss.*re[- ]?engage',
                    r'(?:unilateral|imposed).*variation'
                ],
                'severity': 'critical',
                'requirement': 'Restrictions on dismissal to impose contract variations'
            },
            'pregnancy_redundancy': {
                'patterns': [
                    r'(?:pregnancy|maternity).*redundancy',
                    r'suitable\s+alternative.*(?:pregnancy|maternity)',
                    r'priority.*(?:pregnant|maternity\s+leave)'
                ],
                'severity': 'critical',
                'requirement': 'Enhanced protection from redundancy during pregnancy/maternity'
            }
        }

    def check(self, text: str, document_type: str = None) -> Dict[str, Any]:
        """
        Check document for ERA 2023 compliance

        Args:
            text: Document text to check
            document_type: Type of document (optional)

        Returns:
            Dict with compliance results
        """
        results = {
            'compliant': True,
            'legal_source': self.legal_source,
            'provisions_found': [],
            'provisions_missing': [],
            'warnings': [],
            'failures': [],
            'score': 0
        }

        for provision_name, provision_data in self.provisions.items():
            patterns = provision_data['patterns']
            found = any(re.search(p, text, re.IGNORECASE) for p in patterns)

            if found:
                results['provisions_found'].append({
                    'provision': provision_name,
                    'requirement': provision_data['requirement'],
                    'severity': provision_data['severity']
                })
                results['score'] += 1
            else:
                results['provisions_missing'].append({
                    'provision': provision_name,
                    'requirement': provision_data['requirement'],
                    'severity': provision_data['severity']
                })

                if provision_data['severity'] == 'critical':
                    results['failures'].append(f"{provision_name}: {provision_data['requirement']}")
                    results['compliant'] = False
                elif provision_data['severity'] == 'high':
                    results['warnings'].append(f"{provision_name}: {provision_data['requirement']}")

        # Calculate compliance percentage
        total_provisions = len(self.provisions)
        results['compliance_percentage'] = (results['score'] / total_provisions) * 100

        # Overall status
        if results['compliance_percentage'] >= 80:
            results['status'] = 'PASS'
        elif results['compliance_percentage'] >= 50:
            results['status'] = 'WARNING'
        else:
            results['status'] = 'FAIL'

        return results

    def get_recommendations(self, check_result: Dict[str, Any]) -> List[str]:
        """Get recommendations based on check results"""
        recommendations = []

        for missing in check_result['provisions_missing']:
            if missing['severity'] in ['critical', 'high']:
                recommendations.append(
                    f"Add {missing['provision']}: {missing['requirement']} "
                    f"(Employment Rights Act 2023)"
                )

        return recommendations
