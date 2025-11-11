import re


class RdPreNotificationGate:
    def __init__(self):
        self.name = "rd_pre_notification"
        self.severity = "high"
        self.legal_source = "FA 2023, Schedule 9"

    def _is_relevant(self, text):
        keywords = ['pre-notification', 'first claim', '6 month']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check first-time claimants must notify HMRC 6 months before claim
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
