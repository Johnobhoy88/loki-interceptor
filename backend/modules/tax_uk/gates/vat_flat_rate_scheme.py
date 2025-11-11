import re
from decimal import Decimal


class VatFlatRateSchemeGate:
    def __init__(self):
        self.name = "vat_flat_rate_scheme"
        self.severity = "medium"
        self.legal_source = "HMRC Notice 733: Flat Rate Scheme for small businesses"

    def _is_relevant(self, text):
        return any(kw in (text or '').lower() for kw in ['flat rate', 'frs', 'simplified vat'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable - document does not mention Flat Rate Scheme'}

        text_lower = text.lower()
        issues = []

        # Check turnover limit (£150,000)
        if re.search(r'£\s*(\d{1,3}(?:,?\d{3})*)', text):
            amounts = re.findall(r'£\s*(\d{1,3}(?:,?\d{3})*)', text)
            for amount_str in amounts:
                amount = int(amount_str.replace(',', ''))
                if amount > 150000 and 'flat rate' in text_lower:
                    issues.append('Flat Rate Scheme only available for turnover up to £150,000')

        # Check for limited cost trader (16.5% rate)
        if '16.5%' in text or 'limited cost trader' in text_lower:
            if not re.search(r'(?:2%|£1,?000)', text_lower):
                issues.append('Limited Cost Trader rate (16.5%) applies if goods cost less than 2% of turnover or £1,000/year')

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'medium',
                'message': '; '.join(issues),
                'legal_source': self.legal_source,
                'suggestion': 'Verify Flat Rate Scheme eligibility and rates per HMRC Notice 733'
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'Flat Rate Scheme information valid'}
