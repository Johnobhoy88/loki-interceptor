import re


class SanctionGraduationGate:
    def __init__(self):
        self.name = "sanction_graduation"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary sanction for first offense',
                'legal_source': self.legal_source
            }

        patterns = [r'outcomes? may include', r'written warning', r'final written warning', r'dismissal']
        hits = sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))
        if hits >= 2:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Graduated sanctions referenced (warnings through dismissal)', 'legal_source': self.legal_source}
        return {'status': 'FAIL', 'severity': 'high', 'message': 'No reference to graduated sanctions (warnings, dismissal)', 'legal_source': self.legal_source}
