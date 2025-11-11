"""PIDA Whistleblowing Compliance"""
import re

class PIDAComplianceChecker:
    def __init__(self):
        self.legal_source = "Public Interest Disclosure Act 1998, ERA 1996 Part IVA"
        self.qualifying_disclosures = ['crime', 'legal_breach', 'miscarriage_justice', 
                                       'health_safety', 'environment', 'cover_up']
    
    def check(self, text: str) -> dict:
        found = sum(1 for disc in self.qualifying_disclosures 
                   if re.search(disc.replace('_', r'\s+'), text, re.I))
        has_protection = bool(re.search(r'(?:no|not).*detriment.*whistleblow', text, re.I))
        return {'status': 'PASS' if found >= 4 and has_protection else 'FAIL', 'coverage': f'{found}/6'}
