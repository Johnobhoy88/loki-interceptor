"""TUPE Transfer Validator"""
import re

class TUPETransferValidator:
    def __init__(self):
        self.legal_source = "TUPE Regulations 2006"
    
    def validate(self, text: str) -> dict:
        checks = {
            'automatic_transfer': bool(re.search(r'automatic.*transfer', text, re.I)),
            'terms_protected': bool(re.search(r'terms.*protect', text, re.I)),
            'consultation': bool(re.search(r'(?:inform|consult).*employee', text, re.I)),
            'ELI': bool(re.search(r'ELI|employee\s+liability\s+information', text, re.I))
        }
        return {'status': 'PASS' if sum(checks.values()) >= 3 else 'FAIL', 'checks': checks}
