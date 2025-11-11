import re


class DataSubjectRightsGate:
    def __init__(self):
        self.name = "data_subject_rights"
        self.severity = "high"
        self.legal_source = "UK GDPR Articles 12-23, Data Protection Act 2018"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['data', 'personal information', 'privacy', 'gdpr', 'employee'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        gdpr_patterns = [
            r'(?:personal\s+)?data',
            r'GDPR|data\s+protection',
            r'privacy|information'
        ]

        mentions_data = any(re.search(p, text, re.IGNORECASE) for p in gdpr_patterns)

        if not mentions_data:
            return {'status': 'N/A', 'message': 'No data protection provisions', 'legal_source': self.legal_source}

        # Check for data subject rights
        rights = {
            'right_to_be_informed': r'(?:inform|transparency|privacy\s+notice)',
            'right_of_access': r'(?:access|subject\s+access\s+request|SAR)',
            'right_to_rectification': r'(?:rectif|correct|amend).*(?:inaccurate|incorrect)',
            'right_to_erasure': r'(?:eras|delet|right\s+to\s+be\s+forgotten)',
            'right_to_restrict': r'restrict.*processing',
            'right_to_portability': r'(?:data\s+)?portability',
            'right_to_object': r'(?:object|opt[- ]out).*processing',
            'automated_decisions': r'(?:automated|profiling).*(?:decision|processing)'
        }

        found_rights = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in rights.items()}
        rights_score = sum(found_rights.values())

        # Check for response timeframes
        timeframe_patterns = [
            r'(?:within|respond.*within)\s+(?:one|1)\s+month',
            r'30\s+days?',
            r'(?:prompt|timely).*(?:response|reply)'
        ]

        has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)

        # Check for free of charge
        free_patterns = [
            r'(?:free|without).*(?:charge|fee|cost)',
            r'no\s+(?:charge|fee)'
        ]

        mentions_free = any(re.search(p, text, re.IGNORECASE) for p in free_patterns)

        # Check for exemptions/restrictions
        exemption_patterns = [
            r'(?:exempt|restrict).*(?:legal\s+obligation|vital\s+interest|public\s+interest)',
            r'manifestly\s+unfounded|excessive'
        ]

        mentions_exemptions = any(re.search(p, text, re.IGNORECASE) for p in exemption_patterns)

        # Additional GDPR compliance elements
        compliance_elements = {
            'lawful_basis': r'lawful\s+basis|legal\s+basis',
            'retention': r'retention\s+period|how\s+long.*(?:keep|retain)',
            'security': r'(?:security|safeguard).*(?:personal\s+)?data',
            'breach_notification': r'(?:data\s+)?breach.*(?:notif|report)',
            'dpo_contact': r'(?:DPO|data\s+protection\s+officer).*contact',
            'ico_complaint': r'(?:ICO|Information\s+Commissioner).*(?:complain|lodge)'
        }

        found_compliance = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in compliance_elements.items()}
        compliance_score = sum(found_compliance.values())

        total_score = rights_score + compliance_score

        if rights_score >= 6 and compliance_score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive GDPR data subject rights ({rights_score}/8 rights, {compliance_score}/6 compliance)',
                'legal_source': self.legal_source,
                'rights_found': [k for k, v in found_rights.items() if v],
                'compliance_found': [k for k, v in found_compliance.items() if v]
            }

        if rights_score >= 4 and compliance_score >= 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Data subject rights incomplete ({rights_score}/8 rights, {compliance_score}/6 compliance)',
                'legal_source': self.legal_source,
                'missing_rights': [k for k, v in found_rights.items() if not v],
                'missing_compliance': [k for k, v in found_compliance.items() if not v],
                'suggestion': 'Add: access, rectification, erasure, restriction, objection rights. One month response time. Free of charge.'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Inadequate data subject rights provisions',
            'legal_source': self.legal_source,
            'penalty': 'Up to £17.5 million or 4% of global turnover; ICO enforcement',
            'suggestion': 'Must provide data subject rights per UK GDPR Arts 12-23: access, rectification, erasure, restriction, portability, objection, automated decisions. Response within 1 month, free of charge.'
        }
