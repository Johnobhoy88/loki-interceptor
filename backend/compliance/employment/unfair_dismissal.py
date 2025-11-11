"""Unfair Dismissal Protection Checker"""
import re

class UnfairDismissalProtection:
    def __init__(self):
        self.legal_source = "Employment Rights Act 1996 ss.94-98, ACAS Code of Practice"
        self.fair_reasons = ['capability', 'conduct', 'redundancy', 'statutory_bar', 'SOSR']
        self.automatically_unfair = ['pregnancy', 'whistleblowing', 'trade_union', 'health_safety']
    
    def check(self, text: str) -> dict:
        has_fair_procedure = all([
            re.search(r'investigat', text, re.I),
            re.search(r'meeting|hearing', text, re.I),
            re.search(r'appeal', text, re.I),
            re.search(r'ACAS', text, re.I)
        ])
        protects_auto_unfair = any(re.search(r'(?:not|never).*dismiss.*' + reason, text, re.I) 
                                   for reason in self.automatically_unfair)
        return {
            'status': 'PASS' if has_fair_procedure and protects_auto_unfair else 'FAIL',
            'fair_procedure': has_fair_procedure,
            'protects_auto_unfair': protects_auto_unfair,
            'legal_source': self.legal_source
        }
