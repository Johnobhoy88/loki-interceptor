"""Settlement Agreement Compliance"""
import re

class SettlementAgreementCompliance:
    def __init__(self):
        self.legal_source = "Employment Rights Act 1996 s.203"
    
    def validate(self, text: str) -> dict:
        requirements = {
            'in_writing': bool(re.search(r'in\s+writing', text, re.I)),
            'independent_adviser': bool(re.search(r'independent.*adviser', text, re.I)),
            'adviser_insurance': bool(re.search(r'insurance', text, re.I)),
            'particular_complaint': bool(re.search(r'particular.*complaint', text, re.I)),
            'adviser_certificate': bool(re.search(r'certif', text, re.I))
        }
        return {'status': 'PASS' if sum(requirements.values()) >= 4 else 'FAIL', 'requirements': requirements}
