import re


class ComplianceLawsGate:
    def __init__(self):
        self.name = "compliance_laws"
        self.severity = "medium"
        self.legal_source = "Various UK Statutes"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for general compliance provisions
        compliance_patterns = [
            r'comply\s+with.*(?:law|legislation|regulation)',
            r'in\s+accordance\s+with.*(?:applicable\s+)?law',
            r'obligations?\s+under.*(?:law|act|regulation)',
            r'legal\s+(?:requirement|obligation)'
        ]

        has_compliance = any(re.search(p, text, re.IGNORECASE) for p in compliance_patterns)

        if not has_compliance:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No general compliance with laws provision',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding clause requiring compliance with applicable laws',
                'note': 'Parties are legally required to comply with laws regardless, but clause makes expectation explicit'
            }

        # Check for specific laws/regulations mentioned
        specific_laws = {
            'data_protection': r'(?:GDPR|Data\s+Protection\s+Act|DPA)',
            'anti_bribery': r'Bribery\s+Act\s+2010',
            'modern_slavery': r'Modern\s+Slavery\s+Act',
            'money_laundering': r'Money\s+Laundering.*Regulation',
            'competition': r'Competition\s+Act',
            'equality': r'Equality\s+Act',
            'health_safety': r'Health\s+and\s+Safety',
            'employment': r'Employment\s+(?:Rights\s+)?Act'
        }

        found_laws = {}
        for law_type, pattern in specific_laws.items():
            found_laws[law_type] = bool(re.search(pattern, text, re.IGNORECASE))

        # Check for anti-bribery/corruption provisions
        anti_bribery_patterns = [
            r'(?:bribe|bribery|corrupt)',
            r'improper\s+payment',
            r'facilitation\s+payment',
            r'kick-?back'
        ]

        addresses_bribery = any(re.search(p, text, re.IGNORECASE) for p in anti_bribery_patterns)

        # Check for modern slavery statement
        modern_slavery_patterns = [
            r'modern\s+slavery',
            r'human\s+trafficking',
            r'forced\s+(?:labour|labor)'
        ]

        addresses_slavery = any(re.search(p, text, re.IGNORECASE) for p in modern_slavery_patterns)

        # Check for sanctions compliance
        sanctions_patterns = [
            r'sanction(?:s)?',
            r'embargo',
            r'restricted\s+part(?:y|ies)',
            r'OFAC|Office\s+of\s+Financial\s+Assets\s+Control'
        ]

        addresses_sanctions = any(re.search(p, text, re.IGNORECASE) for p in sanctions_patterns)

        specific_count = sum(found_laws.values())

        if specific_count >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive compliance provisions ({specific_count} specific laws)',
                'legal_source': self.legal_source,
                'laws_mentioned': [k for k, v in found_laws.items() if v]
            }

        if specific_count >= 2 or addresses_bribery or addresses_slavery:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Compliance provisions with specific law references',
                'legal_source': self.legal_source,
                'laws_mentioned': [k for k, v in found_laws.items() if v],
                'suggestion': 'Consider adding: GDPR, Bribery Act, Modern Slavery Act'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'General compliance provision included',
            'legal_source': self.legal_source,
            'suggestion': 'Consider specifying key laws: GDPR, Bribery Act 2010, Modern Slavery Act'
        }
