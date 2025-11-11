import re


class MaternityRightsGate:
    def __init__(self):
        self.name = "maternity_rights"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 ss.71-75, Maternity and Parental Leave Regulations 1999"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['maternity', 'pregnant', 'pregnancy', 'leave', 'parental'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        # Check for maternity leave provisions
        maternity_patterns = [
            r'maternity\s+leave',
            r'pregnant(?:cy)?',
            r'(?:ordinary|additional)\s+maternity'
        ]

        has_maternity = any(re.search(p, text, re.IGNORECASE) for p in maternity_patterns)

        if not has_maternity:
            return {'status': 'N/A', 'message': 'No maternity provisions', 'legal_source': self.legal_source}

        elements = {
            '52_weeks': r'52\s+weeks?|one\s+year',
            'notification_15_weeks': r'15\s+weeks?.*(?:before|notice)',
            'smp': r'statutory\s+maternity\s+pay|SMP',
            'return_rights': r'right\s+to\s+return|return.*(?:same|similar)\s+(?:job|role)',
            'ante_natal': r'ante[- ]?natal|antenatal',
            'protection_dismissal': r'(?:not|unfair).*dismiss.*(?:pregnancy|maternity)',
            'risk_assessment': r'risk\s+assessment.*pregnant',
            'keeping_in_touch': r'(?:KIT|keeping\s+in\s+touch)\s+days?'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 5:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive maternity provisions ({score}/8)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Incomplete maternity provisions ({score}/8)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v],
                'suggestion': 'Must include: 52 weeks leave, SMP, return rights, protection from dismissal'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate maternity rights - high discrimination risk',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited compensation for pregnancy discrimination',
            'suggestion': 'Add: 52 weeks leave (26 OML + 26 AML), SMP, notification (15 weeks before EWC), return rights, anti-natal care, protection from dismissal'
        }
