"""Enhanced Due Diligence Gate - MLR 2017 & FCA"""
import re

class EnhancedDueDiligenceGate:
    def __init__(self):
        self.name = "enhanced_due_diligence"
        self.severity = "high"
        self.legal_source = "MLR 2017 & FCA AML Requirements"

    def _is_relevant(self, text):
        aml_terms = ['due diligence', 'edd', 'enhanced due diligence', 'kyc', 'know your customer', 'aml']
        return any(term in text.lower() for term in aml_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        edd_triggers = [
            r'(?:pep|politically\s+exposed)',
            r'high[- ]risk',
            r'(?:offshore|overseas)',
            r'complex\s+(?:structure|ownership)',
            r'unusual\s+(?:transaction|activity)'
        ]

        has_edd_trigger = any(re.search(trigger, text, re.IGNORECASE) for trigger in edd_triggers)

        if has_edd_trigger:
            edd_measures = [
                r'enhanced\s+(?:due\s+diligence|checks|monitoring)',
                r'source\s+of\s+(?:funds|wealth)',
                r'additional\s+(?:verification|documentation)',
                r'ongoing\s+monitoring'
            ]

            has_edd_measures = any(re.search(measure, text, re.IGNORECASE) for measure in edd_measures)

            if not has_edd_measures:
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': 'EDD trigger detected without enhanced measures',
                    'legal_source': self.legal_source,
                    'suggestion': 'EDD required: source of wealth/funds, additional verification, ongoing monitoring'
                }

        return {'status': 'PASS', 'message': 'Due diligence requirements adequate', 'legal_source': self.legal_source}
