"""Flexible Working Rights Validator - ERA 2023 compliant"""
import re

class FlexibleWorkingRightsValidator:
    def __init__(self):
        self.legal_source = "Employment Rights Act 1996 s.80F, Employment Relations (Flexible Working) Act 2023"
    
    def validate(self, text: str) -> dict:
        checks = {
            'day_one_right': bool(re.search(r'(?:day\s+one|from\s+start|all\s+employees)', text, re.I)),
            'two_requests_per_year': bool(re.search(r'(?:two|2).*(?:request|application).*year', text, re.I)),
            'two_month_decision': bool(re.search(r'(?:two|2)\s+month.*(?:decision|respond)', text, re.I)),
            'eight_business_reasons': bool(re.search(r'business\s+reason|burden.*cost', text, re.I)),
            'appeal_right': bool(re.search(r'appeal', text, re.I))
        }
        score = sum(checks.values())
        return {
            'status': 'PASS' if score >= 4 else 'FAIL',
            'score': score,
            'checks': checks,
            'legal_source': self.legal_source
        }
