import re


class MeetingDetailsGate:
    def __init__(self):
        self.name = "meeting_details"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting', 'invite']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary meeting notice',
                'legal_source': self.legal_source
            }

        has_date = bool(re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", text, re.IGNORECASE))
        has_time = bool(re.search(r"\b(?:\d{1,2}:[0-5]\d|\d{1,2}\s?(?:am|pm))\b", text, re.IGNORECASE))
        has_location = any(w in text.lower() for w in ['location', 'venue', 'address', 'meeting room', 'place'])

        if has_date and has_time and has_location:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Date, time and location provided', 'legal_source': self.legal_source}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'Missing date, time or location for the meeting', 'legal_source': self.legal_source}
