import re


class JurisdictionVenueGate:
    def __init__(self):
        self.name = "jurisdiction_venue"
        self.severity = "medium"
        self.legal_source = "Civil Procedure Rules, Brussels Recast Regulation"

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

        # Check for jurisdiction clause
        jurisdiction_patterns = [
            r'jurisdiction',
            r'(?:courts?|tribunals?)\s+of',
            r'submit\s+to.*(?:jurisdiction|courts?)',
            r'exclusive\s+(?:jurisdiction|venue)'
        ]

        has_jurisdiction = any(re.search(p, text, re.IGNORECASE) for p in jurisdiction_patterns)

        if not has_jurisdiction:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No jurisdiction clause',
                'legal_source': self.legal_source,
                'suggestion': 'Add jurisdiction clause to specify which courts have authority',
                'risk': 'Uncertainty about forum for disputes'
            }

        # Check for UK courts
        uk_courts = [
            r'courts?\s+of.*(?:England|Wales|Scotland|Northern\s+Ireland|United\s+Kingdom)',
            r'English\s+courts?',
            r'Scottish\s+courts?',
            r'High\s+Court',
            r'Court\s+of\s+Session'
        ]

        has_uk_courts = any(re.search(p, text, re.IGNORECASE) for p in uk_courts)

        # Check for exclusivity
        exclusive_patterns = [
            r'exclusive(?:ly)?.*jurisdiction',
            r'non-exclusive\s+jurisdiction',
            r'submit.*exclusively',
            r'only.*courts?'
        ]

        exclusive_matches = [p for p in exclusive_patterns if re.search(p, text, re.IGNORECASE)]

        is_exclusive = any(re.search(r'exclusive(?:ly)?.*jurisdiction', text, re.IGNORECASE) and
                          not re.search(r'non-exclusive', text, re.IGNORECASE))
        is_non_exclusive = re.search(r'non-exclusive', text, re.IGNORECASE)

        # Check for service of process
        service_patterns = [
            r'service\s+of\s+process',
            r'(?:serve|served).*(?:writ|claim|proceedings)',
            r'agent\s+for\s+service'
        ]

        has_service = any(re.search(p, text, re.IGNORECASE) for p in service_patterns)

        # Check for waiver of sovereign immunity (for government contracts)
        immunity_patterns = [
            r'waiv(?:e|es|er).*sovereign\s+immunity',
            r'sovereign\s+immunity.*waiv',
            r'immunities.*waiv(?:e|ed)'
        ]

        has_immunity_waiver = any(re.search(p, text, re.IGNORECASE) for p in immunity_patterns)

        details = {
            'uk_courts': has_uk_courts,
            'exclusive': is_exclusive,
            'non_exclusive': is_non_exclusive,
            'service_provisions': has_service
        }

        if has_uk_courts and is_exclusive:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Exclusive UK jurisdiction clause',
                'legal_source': self.legal_source,
                'details': details
            }

        if has_uk_courts:
            jurisdiction_type = 'exclusive' if is_exclusive else 'non-exclusive' if is_non_exclusive else 'unclear'
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'UK jurisdiction clause ({jurisdiction_type})',
                'legal_source': self.legal_source,
                'details': details,
                'suggestion': 'Consider specifying whether jurisdiction is exclusive or non-exclusive'
            }

        # Non-UK jurisdiction
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Non-UK jurisdiction specified',
            'legal_source': self.legal_source,
            'details': details,
            'note': 'Ensure consistency with governing law clause and enforceability in specified jurisdiction'
        }
