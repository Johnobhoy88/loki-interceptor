"""Equality Act 2010 Compliance Checker"""
import re

class EqualityActCompliance:
    def __init__(self):
        self.legal_source = "Equality Act 2010"
        self.protected_characteristics = [
            'age', 'disability', 'gender reassignment', 'marriage', 
            'pregnancy', 'race', 'religion', 'sex', 'sexual orientation'
        ]
    
    def check(self, text: str) -> dict:
        found = sum(1 for char in self.protected_characteristics 
                   if re.search(char.replace(' ', r'\s+'), text, re.I))
        return {
            'status': 'PASS' if found >= 7 else 'FAIL',
            'coverage': f'{found}/9',
            'legal_source': self.legal_source
        }
