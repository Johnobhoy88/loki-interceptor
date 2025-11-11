import re


class VatPartialExemptionGate:
    def __init__(self):
        self.name = "vat_partial_exemption"
        self.severity = "high"
        self.legal_source = "VAT Act 1994, s26; HMRC Notice 706: Partial Exemption"

    def _is_relevant(self, text):
        return any(kw in (text or '').lower() for kw in ['partial exemption', 'exempt supply', 'taxable supply'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable - document does not mention partial exemption'}

        text_lower = text.lower()
        issues = []

        # Check for de minimis limit (£7,500 per year or £625 per month)
        if 'de minimis' in text_lower or 'exempt input' in text_lower:
            if not re.search(r'£7,?500|£625', text_lower):
                issues.append('De minimis limits: £7,500/year and £625/month exempt input tax')

        # Check for standard method mention
        if 'partial exemption' in text_lower:
            if not re.search(r'standard method|special method|recovery rate', text_lower):
                issues.append('Should specify partial exemption method (standard or special)')

        if issues:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': '; '.join(issues),
                'legal_source': self.legal_source
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'Partial exemption information valid'}
