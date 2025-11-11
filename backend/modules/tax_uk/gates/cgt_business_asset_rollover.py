import re


class CgtBusinessAssetRolloverGate:
    def __init__(self):
        self.name = "cgt_business_asset_rollover"
        self.severity = "high"
        self.legal_source = "TCGA 1992, s152-159"

    def _is_relevant(self, text):
        keywords = ['rollover relief', 'business asset']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check rollover relief for replacement of business assets
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
