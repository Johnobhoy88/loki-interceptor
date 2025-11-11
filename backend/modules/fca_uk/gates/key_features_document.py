"""Key Features Document Requirements Gate - COBS 13 & 14"""
import re

class KeyFeaturesDocumentGate:
    def __init__(self):
        self.name = "key_features_document"
        self.severity = "high"
        self.legal_source = "FCA COBS 13 & 14 (Key Features)"

    def _is_relevant(self, text):
        return 'key feature' in text.lower() or 'kfd' in text.lower()

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        required_sections = {
            'aims': r'(?:aims?|objectives?)',
            'commitments': r'commitment',
            'risks': r'risk',
            'questions': r'question',
            'charges': r'(?:charge|cost|fee)'
        }

        found = [sec for sec, pattern in required_sections.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 4:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': f'Key features document incomplete ({len(found)}/5 sections)',
                'legal_source': self.legal_source,
                'suggestion': 'KFD must include: aims, commitments, risks, questions & answers, charges',
                'missing': [s for s in required_sections.keys() if s not in found]
            }

        return {'status': 'PASS', 'message': 'Key features document complete', 'legal_source': self.legal_source}
