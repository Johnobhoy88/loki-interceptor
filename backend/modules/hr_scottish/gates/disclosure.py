import re


class DisclosureGate:
    def __init__(self):
        self.name = "disclosure_of_documents"
        self.severity = "critical"
        self.legal_source = "ACAS Code of Practice, Paragraph 9"
        self.relevance_keywords = ['disciplinary', 'hearing', 'meeting']

    def _is_relevant(self, text):
        t = (text or '').lower()
        return 'disciplinary' in t and any(k in t for k in self.relevance_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary investigation or hearing notice',
                'legal_source': self.legal_source
            }

        patterns = [r'document(s|ation)', r'bundle', r'evidence', r'witness statements?', r'investigation report', r'provided (?:in advance|before the hearing)']
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Disclosure of documents referenced', 'legal_source': self.legal_source}
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'No reference to disclosure of documents prior to the hearing',
            'legal_source': self.legal_source,
            'suggestion': 'Confirm the evidence and documents will be provided in advance of the hearing.'
        }
