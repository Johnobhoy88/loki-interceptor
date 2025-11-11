import re
from decimal import Decimal


class CtRateValidationGate:
    def __init__(self):
        self.name = "ct_rate_validation"
        self.severity = "high"
        self.legal_source = "Corporation Tax Act 2010, s4; Finance Act 2024"

    def _is_relevant(self, text):
        return any(kw in (text or '').lower() for kw in ['corporation tax', 'ct rate', 'company tax'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A'}

        text_lower = text.lower()
        issues = []

        # Find CT rate mentions (2024/25: 19% and 25%)
        rate_pattern = r'(?:corporation\s+tax|ct).*?(\d+(?:\.\d+)?)\s*%'
        for match in re.finditer(rate_pattern, text_lower):
            rate_str = match.group(1)
            try:
                rate = Decimal(rate_str)
                if rate not in [Decimal('19'), Decimal('25')]:
                    issues.append(f'Invalid CT rate: {rate}%. Valid rates: 19% (£50k-£250k), 25% (£250k+)')
            except:
                pass

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': '; '.join(issues),
                'legal_source': self.legal_source,
                'suggestion': '2024/25: Small profits rate 19% (up to £50k), Main rate 25% (over £250k), Marginal relief applies between'
            }

        return {'status': 'PASS'}
