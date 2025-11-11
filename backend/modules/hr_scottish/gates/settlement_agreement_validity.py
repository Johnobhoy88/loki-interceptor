import re


class SettlementAgreementValidityGate:
    def __init__(self):
        self.name = "settlement_agreement_validity"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 s.203, Settlement Agreement Regulations 2013"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['settlement', 'compromise', 'termination', 'exit', 'waive'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        settlement_patterns = [
            r'settlement\s+agreement',
            r'compromise\s+agreement',
            r'waive.*(?:right|claim)'
        ]

        is_settlement = any(re.search(p, text, re.IGNORECASE) for p in settlement_patterns)

        if not is_settlement:
            return {'status': 'N/A', 'message': 'Not a settlement agreement', 'legal_source': self.legal_source}

        # Check for statutory requirements (s.203 ERA 1996)
        statutory_requirements = {
            'in_writing': r'in\s+writing|written\s+agreement',
            'particular_complaint': r'(?:particular|specific).*(?:complaint|proceeding)|relate.*(?:complaint|claim)',
            'independent_adviser': r'independent.*(?:legal\s+)?advi(?:sor|ser)|relevant\s+independent\s+adviser',
            'adviser_identified': r'(?:name|identified).*adviser',
            'adviser_insurance': r'(?:professional\s+indemnity\s+)?insurance.*(?:force|in\s+place)',
            'advice_received': r'(?:receiv|obtain).*(?:independent\s+)?(?:legal\s+)?advice',
            'adviser_certificate': r'(?:certificate|certif(?:y|ies)).*adviser',
            'conditions_satisfied': r'condition(?:s)?.*(?:satisfi|met|complied)'
        }

        found_requirements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in statutory_requirements.items()}
        requirement_score = sum(found_requirements.values())

        # Check for appropriate adviser categories
        adviser_categories = [
            r'(?:qualified\s+)?solicitor',
            r'barrister',
            r'(?:legal\s+)?executive.*fellow.*(?:CILEX|Chartered\s+Institute)',
            r'trade\s+union.*(?:officer|official)',
            r'advice\s+(?:centre|agency).*worker'
        ]

        has_appropriate_adviser = any(re.search(p, text, re.IGNORECASE) for p in adviser_categories)

        # Check for prohibited waivers
        prohibited_waivers = {
            'personal_injury': r'(?:waive|exclude).*personal\s+injury',
            'acas_rights': r'(?:waive|exclude).*(?:ACAS|conciliation)',
            'future_rights': r'(?:waive|exclude).*future.*(?:right|claim)',
            'pension_rights': r'(?:waive|exclude).*pension'
        }

        has_prohibited = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in prohibited_waivers.items()}

        if any(has_prohibited.values()):
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Prohibited waivers detected in settlement agreement',
                'legal_source': self.legal_source,
                'prohibited_items': [k for k, v in has_prohibited.items() if v],
                'penalty': 'Agreement void and unenforceable for those provisions',
                'suggestion': 'Cannot waive: personal injury claims, future rights, pension rights'
            }

        # Check for consideration
        consideration_patterns = [
            r'(?:in\s+)?consideration\s+(?:of|for)',
            r'payment\s+of.*(?:£|\$|GBP)',
            r'ex[- ]gratia',
            r'(?:severance|termination)\s+(?:payment|package)'
        ]

        has_consideration = any(re.search(p, text, re.IGNORECASE) for p in consideration_patterns)

        # Check for without prejudice
        without_prejudice_patterns = [
            r'without\s+prejudice',
            r'off\s+the\s+record',
            r'settlement\s+(?:discussion|negotiation)'
        ]

        is_protected = any(re.search(p, text, re.IGNORECASE) for p in without_prejudice_patterns)

        if requirement_score >= 6 and has_appropriate_adviser and has_consideration:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Valid settlement agreement ({requirement_score}/8 requirements)',
                'legal_source': self.legal_source,
                'requirements_met': [k for k, v in found_requirements.items() if v]
            }

        if requirement_score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'critical',
                'message': f'Settlement agreement incomplete ({requirement_score}/8 requirements)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found_requirements.items() if not v],
                'suggestion': 'Must meet all s.203 ERA requirements: written, particular complaint, independent adviser (identified), adviser insurance, advice received, adviser certificate'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Settlement agreement fails to meet statutory requirements',
            'legal_source': self.legal_source,
            'penalty': 'Agreement void and unenforceable; employee retains all statutory rights',
            'suggestion': 'Ensure s.203 ERA compliance: (1) written, (2) relates to particular complaint, (3) independent adviser, (4) adviser identified, (5) adviser insured, (6) advice received, (7) conditions met'
        }
