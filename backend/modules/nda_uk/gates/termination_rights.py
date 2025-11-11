import re


class TerminationRightsGate:
    def __init__(self):
        self.name = "termination_rights"
        self.severity = "medium"
        self.legal_source = "Contract Law"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for termination provisions
        termination_patterns = [
            r'terminat(?:e|ion|ed)',
            r'end\s+(?:this|the)\s+agreement',
            r'cancel(?:lation)?',
            r'bring.*to\s+an\s+end'
        ]

        has_termination = any(re.search(p, text, re.IGNORECASE) for p in termination_patterns)

        if not has_termination:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No termination provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding termination rights and procedures'
            }

        # Check for termination types
        termination_types = {
            'for_convenience': [
                r'(?:for|without)\s+(?:any\s+)?(?:reason|cause)',
                r'at\s+(?:will|any\s+time)',
                r'(?:either|any)\s+party\s+may\s+terminate'
            ],
            'for_cause': [
                r'(?:for|with)\s+cause',
                r'material\s+breach',
                r'breach.*(?:remedy|cure)',
                r'default'
            ],
            'by_notice': [
                r'(?:upon|by\s+giving).*notice',
                r'notice\s+of\s+termination',
                r'\d+\s+(?:days?|months?)\s*[\']?\s*notice'
            ],
            'automatic': [
                r'automatic(?:ally)?.*terminat',
                r'shall\s+(?:automatically\s+)?(?:terminate|end)',
                r'(?:upon|on).*(?:bankruptcy|insolvency|liquidation)'
            ],
            'insolvency': [
                r'(?:bankrupt|insolven|liquidation|administration|receivership)',
                r'winding[- ]up',
                r'cease\s+to\s+(?:trade|carry\s+on\s+business)'
            ]
        }

        found_types = {}
        for term_type, patterns in termination_types.items():
            found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
            found_types[term_type] = found

        # Check for notice period
        notice_period_patterns = [
            r'(\d+)\s+(?:days?|months?|weeks?)\s*[\']?\s*(?:notice|written\s+notice)',
            r'notice.*(\d+)\s+(?:day|month|week)'
        ]

        notice_matches = [re.search(p, text, re.IGNORECASE) for p in notice_period_patterns]
        notice_periods = [int(m.group(1)) for m in notice_matches if m]

        # Check for cure period
        cure_patterns = [
            r'(?:cure|remedy).*within\s+(\d+)',
            r'(\d+)\s+(?:days?|business\s+days?).*(?:cure|remedy|rectify)',
            r'fail(?:s|ed|ure).*(?:to\s+)?(?:cure|remedy).*(\d+)'
        ]

        has_cure_period = any(re.search(p, text, re.IGNORECASE) for p in cure_patterns)

        # Check for effects of termination
        effects_patterns = {
            'cessation_of_obligations': r'(?:cease|end|terminate).*obligations?',
            'payment_obligations': r'(?:pay|payment).*(?:upon|after|following).*termination',
            'accrued_rights': r'accrued\s+(?:rights|obligations)',
            'no_further_liability': r'(?:no|without)\s+(?:further|additional).*liability',
            'return_of_property': r'(?:return|destroy).*(?:property|materials|confidential)'
        }

        found_effects = {}
        for effect, pattern in effects_patterns.items():
            found_effects[effect] = bool(re.search(pattern, text, re.IGNORECASE))

        # Evaluate comprehensiveness
        types_count = sum(found_types.values())
        effects_count = sum(found_effects.values())

        score = types_count + effects_count
        if notice_periods:
            score += 1
        if has_cure_period:
            score += 1

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive termination provisions',
                'legal_source': self.legal_source,
                'termination_types': [k for k, v in found_types.items() if v],
                'notice_periods': notice_periods if notice_periods else None,
                'has_cure_period': has_cure_period
            }

        if score >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic termination provisions',
                'legal_source': self.legal_source,
                'termination_types': [k for k, v in found_types.items() if v],
                'suggestion': 'Consider adding termination for cause with cure period'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Termination provisions lack detail',
            'legal_source': self.legal_source,
            'termination_types': [k for k, v in found_types.items() if v],
            'suggestion': 'Add: termination for cause, notice period, cure period, effects of termination'
        }
