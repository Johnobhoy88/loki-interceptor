"""Reasonable Adjustments Validator"""
import re

class ReasonableAdjustmentsValidator:
    def __init__(self):
        self.legal_source = "Equality Act 2010 ss.20-22"
    
    def validate(self, text: str) -> dict:
        elements = {
            'anticipatory_duty': bool(re.search(r'anticipatory|proactive', text, re.I)),
            'individual_assessment': bool(re.search(r'individual.*assessment', text, re.I)),
            'consultation': bool(re.search(r'consult.*employee', text, re.I)),
            'examples': bool(re.search(r'example|such\s+as', text, re.I))
        }
        return {'status': 'PASS' if sum(elements.values()) >= 3 else 'FAIL', 'elements': elements}
