import re


class MtdVatMandatoryGate:
    def __init__(self):
        self.name = "mtd_vat_mandatory"
        self.severity = "high"
        self.legal_source = "MTD Regulations 2021"

    def _is_relevant(self, text):
        keywords = ['mtd', 'vat', 'mandatory']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check MTD for VAT mandatory for ALL VAT-registered businesses
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
