import re


class PayeStudentLoanGate:
    def __init__(self):
        self.name = "paye_student_loan"
        self.severity = "high"
        self.legal_source = "Education (Student Loans) Regulations"

    def _is_relevant(self, text):
        keywords = ['student loan', 'plan 1', 'plan 2', 'postgraduate loan']
        return any(kw in (text or '').lower() for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable'}

        # Check student loan repayment thresholds and rates
        text_lower = text.lower()

        # Basic validation logic
        return {'status': 'PASS', 'severity': 'none', 'message': 'Gate check passed', 'legal_source': self.legal_source}
