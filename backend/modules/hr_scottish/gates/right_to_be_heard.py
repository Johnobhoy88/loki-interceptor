import re


class RightToBeHeardGate:
    def __init__(self):
        self.name = "right_to_be_heard"
        self.severity = "critical"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve disciplinary decision-making',
                'legal_source': self.legal_source
            }

        patterns = [r'opportunit(y|ies) to respond', r'present (?:your )?evidence', r'call witnesses', r'ask questions']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Employee’s opportunity to be heard is stated', 'legal_source': self.legal_source}
        return {'status': 'FAIL', 'severity': 'critical', 'message': 'No clear opportunity stated to present evidence or respond', 'legal_source': self.legal_source}
