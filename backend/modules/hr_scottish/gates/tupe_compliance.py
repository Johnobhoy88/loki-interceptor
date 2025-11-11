import re


class TUPEComplianceGate:
    def __init__(self):
        self.name = "tupe_compliance"
        self.severity = "critical"
        self.legal_source = "Transfer of Undertakings (Protection of Employment) Regulations 2006"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['tupe', 'transfer', 'outsourc', 'service provision', 'business transfer'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        tupe_patterns = [
            r'\bTUPE\b',
            r'transfer\s+of\s+undertaking',
            r'relevant\s+transfer',
            r'service\s+provision\s+change'
        ]

        has_tupe = any(re.search(p, text, re.IGNORECASE) for p in tupe_patterns)

        if not has_tupe:
            return {'status': 'N/A', 'message': 'No TUPE provisions', 'legal_source': self.legal_source}

        elements = {
            'automatic_transfer': r'automatic(?:ally)?\s+transfer',
            'terms_protected': r'(?:term|condition).*(?:protect|transfer|preserve)',
            'consultation': r'(?:inform|consult).*(?:employee|workforce|representative)',
            'employee_liability_information': r'ELI|employee\s+liability\s+information',
            'objection_right': r'(?:object|opt[- ]out|refuse).*transfer',
            'dismissal_protection': r'(?:unfair|automatic).*dismiss.*(?:TUPE|transfer)',
            'collective_agreement': r'collective\s+agreement',
            'pensions': r'pension(?:s)?',
            'measures': r'envisaged\s+measures',
            'timing': r'(?:long\s+enough|28\s+days?)\s+before',
            'representatives': r'employee\s+representative|(?:elect|appoint).*representative'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for prohibited variations
        prohibited_variations = [
            r'(?:vary|change|amend).*(?:term|condition).*(?:transfer|TUPE)',
            r'less\s+favourable.*(?:after|following)\s+transfer'
        ]

        has_prohibited_variation = any(re.search(p, text, re.IGNORECASE) for p in prohibited_variations)

        if has_prohibited_variation:
            # Check if there's an ETO reason
            eto_patterns = [
                r'ETO',
                r'economic.*technical.*organisational',
                r'business\s+(?:reason|necessity)'
            ]
            has_eto = any(re.search(p, text, re.IGNORECASE) for p in eto_patterns)

            if not has_eto:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Prohibited variation of terms on TUPE transfer without ETO reason',
                    'legal_source': 'TUPE 2006 reg.4',
                    'penalty': 'Variation void; breach of contract; unfair dismissal if employee resigns',
                    'suggestion': 'Cannot vary terms due to transfer unless ETO reason entailing changes in workforce'
                }

        if score >= 8:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive TUPE compliance ({score}/11 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'TUPE provisions incomplete ({score}/11)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:5],
                'suggestion': 'Add: automatic transfer, protected terms, consultation, ELI, dismissal protection, objection rights'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate TUPE compliance',
            'legal_source': self.legal_source,
            'penalty': 'Up to 13 weeks pay per employee for consultation failures; unfair dismissal claims',
            'suggestion': 'Must comply with TUPE 2006: automatic transfer of employees, protection of terms, consultation (inform 28 days before), ELI, no dismissal by reason of transfer'
        }
