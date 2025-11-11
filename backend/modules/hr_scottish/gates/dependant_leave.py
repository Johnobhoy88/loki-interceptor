import re


class DependantLeaveGate:
    def __init__(self):
        self.name = "dependant_leave"
        self.severity = "medium"
        self.legal_source = "Employment Rights Act 1996 s.57A"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['dependant', 'emergency', 'time off', 'family', 'carer'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        dependant_patterns = [
            r'(?:time\s+off|leave).*dependant',
            r'emergency.*(?:leave|time\s+off)',
            r'dependant.*(?:care|emergency|illness)'
        ]

        has_dependant = any(re.search(p, text, re.IGNORECASE) for p in dependant_patterns)

        if not has_dependant:
            return {'status': 'N/A', 'message': 'No dependant leave provisions', 'legal_source': self.legal_source}

        elements = {
            'reasonable_time': r'reasonable\s+(?:time|amount|period)',
            'unpaid': r'unpaid',
            'emergency_only': r'emergency|unexpected|unforeseen',
            'who_is_dependant': r'dependant.*(?:spouse|partner|child|parent|household)',
            'qualifying_reasons': r'(?:illness|injury|birth|death|breakdown|disruption)',
            'notification': r'(?:inform|notify|tell).*(?:soon\s+as|reasonably\s+practicable|promptly)',
            'reason_and_duration': r'(?:reason|why).*(?:how\s+long|duration)',
            'day_one_right': r'(?:day\s+one|from.*start|all\s+employees)',
            'no_qualifying_period': r'no.*(?:qualifying|service).*(?:period|requirement)',
            'protection_from_detriment': r'(?:not|no).*detriment.*(?:dependant|emergency)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive dependant leave provisions ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic dependant leave provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Add: reasonable time, qualifying reasons, notification requirements, day one right, protection from detriment'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': f'Dependant leave provisions incomplete ({score}/10)',
            'legal_source': self.legal_source,
            'suggestion': 'Time off for dependants per ERA 1996 s.57A: reasonable time (unpaid), emergencies only, day one right (no qualifying period), notify ASAP with reason/duration, protection from detriment. Dependants: spouse, partner, child, parent, household member.'
        }
