import re


class WorkingTimeRegulationsGate:
    def __init__(self):
        self.name = "working_time_regulations"
        self.severity = "high"
        self.legal_source = "Working Time Regulations 1998"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['working time', 'hours', 'rest', 'break', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        elements = {
            '48_hour_week': r'48\s+hours?.*week|average.*week',
            'opt_out': r'opt[- ]out',
            'rest_breaks': r'(?:rest\s+)?break.*20\s+minutes?|20[- ]minute\s+break',
            'daily_rest': r'11\s+(?:consecutive\s+)?hours?.*(?:rest|between)',
            'weekly_rest': r'24\s+hours?.*(?:rest|week)|weekly\s+rest',
            'night_workers': r'night\s+work(?:er|ing)?',
            'record_keeping': r'record.*(?:working\s+time|hours\s+worked)',
            'young_workers': r'young\s+work(?:er|ing)?|under\s+18'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive Working Time Regulations coverage ({score}/8)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Working Time Regulations incomplete ({score}/8)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:4],
                'suggestion': 'Add: 48-hour week, rest breaks (20 mins), daily rest (11 hours), weekly rest (24 hours)'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Inadequate Working Time Regulations compliance',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited fine; HSE enforcement action',
            'suggestion': 'Must comply with WTR 1998: 48-hour week (unless opt-out), 20-min breaks, 11-hour daily rest, 24-hour weekly rest'
        }
