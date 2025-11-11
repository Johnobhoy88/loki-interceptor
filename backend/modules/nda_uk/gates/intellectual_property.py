import re


class IntellectualPropertyGate:
    def __init__(self):
        self.name = "intellectual_property"
        self.severity = "medium"
        self.legal_source = "Copyright, Designs and Patents Act 1988, Patent Act 1977"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential', 'agreement'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check if IP is mentioned
        ip_patterns = [
            r'intellectual\s+property',
            r'\bIP\b',
            r'patent(?:s)?',
            r'copyright(?:s)?',
            r'trade\s*mark(?:s)?',
            r'design\s+right(?:s)?',
            r'know[- ]how'
        ]

        mentions_ip = any(re.search(p, text, re.IGNORECASE) for p in ip_patterns)

        if not mentions_ip:
            return {
                'status': 'N/A',
                'message': 'No intellectual property provisions',
                'legal_source': self.legal_source
            }

        # Check for ownership provisions
        ownership_patterns = [
            r'(?:own|ownership).*intellectual\s+property',
            r'(?:vest|vested|vests).*(?:in|with)',
            r'(?:retain|retains).*(?:all\s+)?rights?',
            r'title.*(?:remain|vest)'
        ]

        has_ownership = any(re.search(p, text, re.IGNORECASE) for p in ownership_patterns)

        # Check for license grants
        license_patterns = [
            r'licen[cs]e(?:s|d)?.*(?:to\s+use|granted)',
            r'grant(?:s|ed)?.*(?:licen[cs]e|right)',
            r'permission\s+to\s+use',
            r'authorize[ds]?\s+to\s+use'
        ]

        has_license = any(re.search(p, text, re.IGNORECASE) for p in license_patterns)

        # Check for pre-existing IP
        preexisting_patterns = [
            r'pre-existing|background|prior',
            r'owned\s+(?:prior\s+to|before)',
            r'existing.*(?:intellectual\s+property|IP)'
        ]

        addresses_preexisting = any(re.search(p, text, re.IGNORECASE) for p in preexisting_patterns)

        # Check for employee inventions (Section 39 Patents Act 1977)
        employee_invention_patterns = [
            r'employee.*invention',
            r'section\s+39.*patent',
            r'invention.*(?:course\s+of\s+employment|normal\s+duties)',
            r'belong\s+to.*employer'
        ]

        addresses_employee_inventions = any(re.search(p, text, re.IGNORECASE) for p in employee_invention_patterns)

        # Check for improvements/derivatives
        improvements_patterns = [
            r'improvement(?:s)?',
            r'derivat(?:ive|ives)',
            r'modif(?:y|ication|ications)',
            r'enhancements?'
        ]

        addresses_improvements = any(re.search(p, text, re.IGNORECASE) for p in improvements_patterns)

        # Check for IP indemnity
        ip_indemnity_patterns = [
            r'indemni.*(?:infringement|IP|intellectual\s+property)',
            r'(?:defend|protect).*(?:against|from).*infringement',
            r'claim.*infring'
        ]

        has_ip_indemnity = any(re.search(p, text, re.IGNORECASE) for p in ip_indemnity_patterns)

        # Check for warranty of ownership
        warranty_patterns = [
            r'warrant(?:s|y).*(?:own|title|right)',
            r'represent.*(?:own|ownership|entitled)',
            r'has\s+(?:full\s+)?(?:right|authority|power).*(?:disclose|license)'
        ]

        has_warranty = any(re.search(p, text, re.IGNORECASE) for p in warranty_patterns)

        # Calculate comprehensiveness
        elements_present = sum([
            has_ownership,
            has_license,
            addresses_preexisting,
            addresses_improvements,
            has_ip_indemnity,
            has_warranty
        ])

        if elements_present >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive IP provisions ({elements_present}/6 elements)',
                'legal_source': self.legal_source,
                'elements': {
                    'ownership': has_ownership,
                    'license': has_license,
                    'preexisting': addresses_preexisting,
                    'improvements': addresses_improvements,
                    'indemnity': has_ip_indemnity,
                    'warranty': has_warranty
                }
            }

        if elements_present >= 2:
            missing = []
            if not has_ownership:
                missing.append('ownership')
            if not addresses_preexisting:
                missing.append('pre-existing IP')
            if not has_warranty:
                missing.append('warranty of ownership')

            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'IP provisions incomplete ({elements_present}/6 elements)',
                'legal_source': self.legal_source,
                'missing': missing,
                'suggestion': 'Clarify IP ownership, address pre-existing IP, and add warranty'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'IP mentioned but provisions inadequate',
            'legal_source': self.legal_source,
            'suggestion': 'Add provisions for: IP ownership, license scope, pre-existing IP, warranties'
        }
