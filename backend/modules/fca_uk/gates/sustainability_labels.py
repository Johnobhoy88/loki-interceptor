"""Sustainability Labels Gate - PS23/16 SDR"""
import re

class SustainabilityLabelsGate:
    def __init__(self):
        self.name = "sustainability_labels"
        self.severity = "critical"
        self.legal_source = "FCA PS23/16 (SDR and Investment Labels)"

    def _is_relevant(self, text):
        label_terms = ['sustainability focus', 'sustainability improvers', 'sustainability impact', 'sustainability mixed goals']
        return any(term in text.lower() for term in label_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        # If using FCA sustainability label, must have required disclosures
        required_disclosures = {
            'investment_policy': r'(?:investment|sustainability)\s+policy',
            'objectives': r'(?:objective|goal|aim)s?',
            'metrics': r'(?:metric|kpi|indicator|measure)',
            'reporting': r'(?:report|reporting|disclosure)',
            'methodology': r'methodology'
        }

        found = [disc for disc, pattern in required_disclosures.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 4:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'FCA sustainability label used without required disclosures',
                'legal_source': self.legal_source,
                'suggestion': 'Required: investment policy, objectives, metrics, reporting, methodology',
                'found': found
            }

        return {'status': 'PASS', 'message': 'Sustainability label properly supported', 'legal_source': self.legal_source}
