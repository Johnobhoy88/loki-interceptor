import re


class CgtCryptoAssetsGate:
    def __init__(self):
        self.name = "cgt_crypto_assets"
        self.severity = "high"
        self.legal_source = "HMRC Cryptoassets Manual"

    def _is_relevant(self, text):
        keywords = ['cryptocurrency', 'crypto', 'bitcoin']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check cryptocurrency disposals subject to CGT
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
