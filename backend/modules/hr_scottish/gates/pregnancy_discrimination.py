import re


class PregnancyDiscriminationGate:
    def __init__(self):
        self.name = "pregnancy_discrimination"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010 s.18, Employment Rights Act 1996 s.99"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['pregnancy', 'pregnant', 'maternity', 'ante-natal', 'dismissal', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        pregnancy_patterns = [
            r'pregnan(?:cy|t)',
            r'maternity',
            r'ante[- ]natal|antenatal'
        ]

        mentions_pregnancy = any(re.search(p, text, re.IGNORECASE) for p in pregnancy_patterns)

        if not mentions_pregnancy:
            return {'status': 'N/A', 'message': 'No pregnancy/maternity provisions', 'legal_source': self.legal_source}

        protection_elements = {
            'no_unfavorable_treatment': r'(?:not|never).*(?:unfavourable|unfavorable|detriment|disadvantage).*pregnan',
            'ante_natal_care': r'ante[- ]?natal.*(?:care|appointment)',
            'risk_assessment': r'(?:risk|health|safety)\s+assessment.*pregnan',
            'suitable_alternative_work': r'(?:suitable|alternative)\s+(?:work|role|employment)',
            'suspension_on_full_pay': r'(?:suspend|suspension).*(?:full\s+pay|maintain.*pay)',
            'maternity_leave_rights': r'maternity\s+leave.*(?:entitled|right)',
            'protection_from_dismissal': r'(?:automatic(?:ally)?\s+unfair|not.*dismiss).*(?:pregnan|maternity)',
            'return_to_work': r'(?:right\s+to\s+)?return.*(?:same|similar)\s+(?:job|role)',
            'contact_during_leave': r'(?:KIT|keeping\s+in\s+touch)\s+days?|contact.*(?:during|maternity\s+leave)',
            'breastfeeding': r'(?:breast[- ]?feed|express.*milk).*(?:facilities|break|accommodation)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in protection_elements.items()}
        score = sum(found.values())

        # Check for prohibited actions
        prohibited_actions = [
            r'(?:dismiss|terminate).*(?:due\s+to|because\s+of|reason\s+of).*pregnan',
            r'(?:select|choose).*redundancy.*pregnan',
            r'(?:reduce|cut).*(?:pay|hours).*pregnan',
            r'(?:demote|move).*less\s+favourable.*pregnan'
        ]

        has_prohibited = any(re.search(p, text, re.IGNORECASE) for p in prohibited_actions)

        if has_prohibited:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Prohibited pregnancy discrimination detected',
                'legal_source': 'Equality Act 2010 s.18, ERA 1996 s.99',
                'penalty': 'Unlimited compensation; automatic unfair dismissal',
                'suggestion': 'Cannot: dismiss, select for redundancy, reduce pay/benefits, or subject to detriment due to pregnancy/maternity'
            }

        # Check for protected period definition
        protected_period_patterns = [
            r'protected\s+period',
            r'pregnancy.*(?:until|end\s+of).*maternity\s+leave',
            r'2\s+weeks?.*(?:after|following).*(?:birth|childbirth)'
        ]

        defines_protected_period = any(re.search(p, text, re.IGNORECASE) for p in protected_period_patterns)

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive pregnancy protection ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Pregnancy protection incomplete ({score}/10)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:5],
                'suggestion': 'Add: protection from unfavorable treatment, ante-natal care time off, risk assessment, suitable alternative work, protection from dismissal'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate pregnancy discrimination protection',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited compensation for pregnancy discrimination (no service requirement)',
            'suggestion': 'Must protect against unfavorable treatment during protected period (pregnancy until end of maternity leave + 2 weeks). Include: ante-natal care, risk assessment, suitable work, no dismissal, return rights'
        }
