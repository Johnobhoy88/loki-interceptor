import re


class SurvivalProvisionsGate:
    def __init__(self):
        self.name = "survival_provisions"
        self.severity = "medium"
        self.legal_source = "Contract Law"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract', 'nda'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for survival clause
        survival_patterns = [
            r'surviv(?:e|al|es).*(?:termination|expir)',
            r'(?:remain|continue)\s+in\s+(?:force|effect).*(?:after|following|termination)',
            r'notwithstanding.*(?:termination|expir)',
            r'beyond.*(?:termination|expir)'
        ]

        has_survival = any(re.search(p, text, re.IGNORECASE) for p in survival_patterns)

        if not has_survival:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No survival provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Add survival clause specifying which provisions continue after termination',
                'risk': 'Uncertainty about post-termination obligations (confidentiality, IP, indemnity)'
            }

        # Check for specific surviving provisions
        surviving_provisions = {
            'confidentiality': r'confidential',
            'intellectual_property': r'intellectual\s+property|IP',
            'indemnity': r'indemni',
            'limitation_of_liability': r'limitation.*liability',
            'warranties': r'warrant',
            'audit_rights': r'audit',
            'data_protection': r'(?:data\s+protection|GDPR)',
            'dispute_resolution': r'(?:dispute|arbitration|jurisdiction)'
        }

        found_surviving = {}
        for provision, pattern in surviving_provisions.items():
            # Check if provision exists and is mentioned in survival context
            if re.search(pattern, text, re.IGNORECASE):
                found_surviving[provision] = True

        # Check for indefinite vs. time-limited survival
        indefinite_patterns = [
            r'(?:indefinitely|perpetually|without\s+limit)',
            r'surviv.*(?:indefinitely|in\s+perpetuity)'
        ]

        is_indefinite = any(re.search(p, text, re.IGNORECASE) for p in indefinite_patterns)

        # Check for time-limited survival
        time_patterns = [
            r'surviv.*(?:for|period\s+of)\s+(\d+)\s+(?:year|month)',
            r'(\d+)\s+(?:year|month).*(?:after|following).*(?:termination|expir)'
        ]

        has_time_limit = any(re.search(p, text, re.IGNORECASE) for p in time_patterns)

        # Check for return/destruction obligations on termination
        return_destruction_patterns = [
            r'(?:return|destroy|delete).*(?:confidential|material|information)',
            r'(?:upon|on).*termination.*(?:return|destroy)',
            r'certification.*(?:destruction|deletion)'
        ]

        has_return_obligations = any(re.search(p, text, re.IGNORECASE) for p in return_destruction_patterns)

        surviving_count = len(found_surviving)

        if surviving_count >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive survival provisions ({surviving_count} provisions)',
                'legal_source': self.legal_source,
                'surviving_provisions': list(found_surviving.keys()),
                'indefinite': is_indefinite,
                'time_limited': has_time_limit
            }

        if surviving_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic survival provisions ({surviving_count} provisions)',
                'legal_source': self.legal_source,
                'surviving_provisions': list(found_surviving.keys()),
                'suggestion': 'Consider specifying survival of: indemnity, IP, limitation of liability'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Survival clause exists but lacks specificity',
            'legal_source': self.legal_source,
            'suggestion': 'Specify which provisions survive: confidentiality, IP, indemnities, warranties, dispute resolution'
        }
