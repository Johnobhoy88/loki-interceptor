import re


class FlexibleWorkingRequestGate:
    def __init__(self):
        self.name = "flexible_working_request"
        self.severity = "high"
        self.legal_source = "Employment Rights Act 1996 s.80F, Flexible Working Regulations 2014, Employment Relations (Flexible Working) Act 2023"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['flexible', 'working', 'hours', 'request', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        flexible_patterns = [
            r'flexible\s+working',
            r'request.*(?:change|alter|vary).*(?:hours|pattern|location)',
            r'work(?:ing)?\s+(?:arrangement|pattern)'
        ]

        has_flexible = any(re.search(p, text, re.IGNORECASE) for p in flexible_patterns)

        if not has_flexible:
            return {'status': 'N/A', 'message': 'No flexible working provisions', 'legal_source': self.legal_source}

        elements = {
            'day_one_right': r'(?:day\s+one|from\s+(?:commencement|start))|all\s+employees',
            'written_request': r'written\s+request|in\s+writing',
            'decision_period': r'(?:2|two)\s+months?|within.*(?:decision|respond)',
            'permitted_reasons': r'(?:business\s+reason|reject|refuse).*(?:burden|cost|quality|performance)',
            'appeal_right': r'appeal',
            'single_application': r'(?:one|1|once).*(?:12\s+months?|year)',
            'meeting': r'(?:discuss|meeting).*request',
            'written_decision': r'written.*(?:decision|outcome|response)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive flexible working provisions ({score}/8) - ERA 2023 compliant',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Incomplete flexible working provisions ({score}/8)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v],
                'suggestion': 'Employment Relations (Flexible Working) Act 2023: Day one right, 2-month decision, written reasons'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Inadequate flexible working procedure',
            'legal_source': self.legal_source,
            'penalty': 'Up to 8 weeks pay for failure to handle request properly',
            'suggestion': 'Add: Day one right (2023 Act), written request, 2-month decision period, 8 permitted business reasons, appeal right'
        }
