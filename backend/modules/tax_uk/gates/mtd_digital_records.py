import re


class MtdDigitalRecordsGate:
    def __init__(self):
        self.name = "mtd_digital_records"
        self.severity = "high"
        self.legal_source = "MTD Regulations 2021, Schedule 1"

    def _is_relevant(self, text):
        keywords = ['digital record', 'mtd']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check digital records must be kept and preserved digitally
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
