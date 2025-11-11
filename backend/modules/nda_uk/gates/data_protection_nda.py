import re


class DataProtectionNDAGate:
    def __init__(self):
        self.name = "data_protection_nda"
        self.severity = "high"
        self.legal_source = "UK GDPR, Data Protection Act 2018"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check if personal data is mentioned
        personal_data_patterns = [
            r'personal\s+(?:data|information)',
            r'data\s+subject',
            r'individual(?:s)?.*(?:data|information)',
            r'GDPR',
            r'data\s+protection'
        ]

        involves_personal_data = any(re.search(p, text, re.IGNORECASE) for p in personal_data_patterns)

        if not involves_personal_data:
            return {
                'status': 'N/A',
                'message': 'No personal data processing indicated',
                'legal_source': self.legal_source
            }

        # Check for GDPR compliance provisions
        gdpr_elements = {
            'lawful_basis': r'lawful\s+basis|legal\s+basis|legitimate\s+interest',
            'purpose_limitation': r'purpose(?:s)?.*(?:specified|limited|defined)',
            'data_minimisation': r'(?:data\s+)?minimi[sz]ation|necessary.*purpose',
            'security': r'(?:appropriate|reasonable)\s+(?:technical|security)\s+measures',
            'retention': r'retention\s+period|kept\s+for.*(?:necessary|period)',
            'data_subject_rights': r'data\s+subject\s+(?:right|access|request)',
            'breach_notification': r'(?:data\s+)?breach.*(?:notif|report)',
            'dpa': r'Data\s+Protection\s+Act|DPA\s+2018',
            'controller_processor': r'(?:data\s+)?(?:controller|processor)'
        }

        found_elements = {}
        for element, pattern in gdpr_elements.items():
            found = re.search(pattern, text, re.IGNORECASE)
            found_elements[element] = bool(found)

        # Check for processor obligations (Article 28)
        processor_obligations = [
            r'process.*only\s+on.*(?:instruction|direction)',
            r'sub-processor',
            r'assist.*data\s+subject\s+rights',
            r'assist.*breach',
            r'delete.*return.*personal\s+data'
        ]

        has_processor_obligations = any(re.search(p, text, re.IGNORECASE) for p in processor_obligations)

        # Check for international transfer provisions
        transfer_patterns = [
            r'(?:international|cross-border)\s+transfer',
            r'(?:adequacy|standard\s+contractual\s+clauses|SCC)',
            r'transfer.*(?:outside|third\s+countr)'
        ]

        has_transfer_provisions = any(re.search(p, text, re.IGNORECASE) for p in transfer_patterns)

        # Calculate compliance score
        compliance_score = sum(found_elements.values())
        total_elements = len(gdpr_elements)

        if compliance_score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive GDPR provisions ({compliance_score}/{total_elements} elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v]
            }

        if compliance_score >= 3:
            missing = [k for k, v in found_elements.items() if not v]
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Partial GDPR compliance ({compliance_score}/{total_elements} elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v],
                'missing': missing[:5],  # Show first 5 missing
                'suggestion': 'Add provisions for: data subject rights, security measures, retention, breach notification'
            }

        missing = [k for k, v in found_elements.items() if not v]
        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Insufficient GDPR compliance provisions for personal data',
            'legal_source': self.legal_source,
            'penalty': 'Potential fines up to £17.5 million or 4% of global turnover',
            'missing': missing,
            'suggestion': 'NDA must comply with UK GDPR when processing personal data. Add provisions for lawful basis, purpose limitation, security, data subject rights'
        }
