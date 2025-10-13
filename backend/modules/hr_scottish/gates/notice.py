import re


class NoticePeriodGate:
    def __init__(self):
        self.name = "notice_period"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary and Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting', 'invite', 'invited']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in ['hearing', 'meeting', 'invite', 'invited'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary notice or warning',
                'legal_source': self.legal_source
            }

        # Look for date/time indicators suggesting notice was provided
        has_date = bool(re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", text, re.IGNORECASE))
        has_time = bool(re.search(r"\b(?:\d{1,2}:[0-5]\d|\d{1,2}\s?(?:am|pm))\b", text, re.IGNORECASE))
        if has_date or has_time:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Meeting date/time provided', 'legal_source': self.legal_source}
        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'No clear meeting date/time provided',
            'legal_source': self.legal_source,
            'suggestion': 'State the date, time and location to provide reasonable notice.'
        }
