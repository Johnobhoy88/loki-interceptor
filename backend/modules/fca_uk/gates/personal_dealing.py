import re


class PersonalDealingGate:
    def __init__(self):
        self.name = "personal_dealing"
        self.severity = "medium"
        self.legal_source = "FCA SYSC 10.1.11 (Personal Account Dealing)"

    def _is_relevant(self, text):
        """Check if document mentions employee trading or personal dealing"""
        text_lower = text.lower()
        keywords = [
            'employee', 'staff', 'personal', 'own account', 'trading',
            'deal', 'transaction', 'investment', 'share', 'security'
        ]
        # Need at least two keywords to be relevant
        matches = sum(1 for kw in keywords if kw in text_lower)
        return matches >= 2

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not address employee or staff personal trading/dealing',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Detect personal dealing/trading references
        personal_dealing_patterns = [
            r'personal\s+(?:dealing|trading|transaction|account)',
            r'(?:employee|staff)\s+(?:trading|dealing|investment|transaction)',
            r'(?:own|personal)\s+account',
            r'(?:trade|invest|deal)\s+(?:on\s+)?(?:their\s+)?own\s+account',
            r'personal\s+investment'
        ]

        has_personal_dealing = False
        for pattern in personal_dealing_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_personal_dealing = True
                for m in matches:
                    spans.append({
                        'type': 'personal_dealing_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        if not has_personal_dealing:
            return {'status': 'N/A'}

        # Check for pre-clearance/approval requirements
        preclearance_patterns = [
            r'pre-?clearance',
            r'prior\s+approval',
            r'(?:must|required\s+to|need\s+to)\s+(?:seek|obtain|get)\s+(?:approval|permission|clearance)',
            r'(?:before|prior\s+to)\s+(?:trading|dealing|transacting)',
            r'approval\s+(?:from|by)\s+(?:compliance|manager)',
            r'compliance\s+approval'
        ]

        has_preclearance = False
        for pattern in preclearance_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_preclearance = True
                for m in matches:
                    spans.append({
                        'type': 'preclearance_requirement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for restricted periods
        restriction_patterns = [
            r'(?:restricted|prohibited|closed)\s+(?:period|window)',
            r'(?:blackout|embargo)\s+period',
            r'(?:cannot|must\s+not|prohibited\s+from)\s+(?:trade|deal|invest)',
            r'(?:during|in)\s+(?:close|closed)\s+period',
            r'(?:ahead\s+of|prior\s+to)\s+(?:announcement|result|publication)'
        ]

        has_restrictions = False
        for pattern in restriction_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_restrictions = True
                for m in matches:
                    spans.append({
                        'type': 'trading_restriction',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for personal dealing policy reference
        policy_patterns = [
            r'personal\s+(?:dealing|trading|account)\s+policy',
            r'(?:employee|staff)\s+(?:dealing|trading)\s+(?:policy|rule|procedure)',
            r'policy\s+(?:on|for|regarding)\s+personal\s+(?:dealing|trading)',
            r'code\s+of\s+(?:conduct|ethics).*(?:personal|trading)'
        ]

        has_policy = False
        for pattern in policy_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_policy = True
                for m in matches:
                    spans.append({
                        'type': 'personal_dealing_policy',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for disclosure/notification requirements
        disclosure_patterns = [
            r'(?:disclose|notify|report)\s+(?:personal\s+)?(?:dealing|trading|transaction)',
            r'(?:maintain|keep)\s+(?:record|log)\s+of',
            r'notification\s+(?:of|to)\s+(?:compliance|manager)',
            r'(?:quarterly|monthly|annual)\s+(?:disclosure|report|declaration)'
        ]

        has_disclosure = False
        for pattern in disclosure_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_disclosure = True
                for m in matches:
                    spans.append({
                        'type': 'disclosure_requirement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for insider information references
        insider_patterns = [
            r'insider\s+(?:information|knowledge|dealing)',
            r'inside\s+information',
            r'material\s+(?:non-?public|unpublished)\s+information',
            r'privileged\s+information',
            r'(?:must\s+not|cannot|prohibited)\s+(?:use|exploit|trade\s+on)'
        ]

        has_insider_ref = False
        for pattern in insider_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_insider_ref = True
                for m in matches:
                    spans.append({
                        'type': 'insider_information',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        control_elements = []
        missing_elements = []

        if has_preclearance:
            control_elements.append('pre-clearance required')
        else:
            missing_elements.append('pre-clearance/approval requirement')

        if has_restrictions:
            control_elements.append('restricted periods defined')

        if has_policy:
            control_elements.append('policy referenced')
        else:
            missing_elements.append('personal dealing policy')

        if has_disclosure:
            control_elements.append('disclosure requirements')

        if has_insider_ref:
            control_elements.append('insider dealing prohibitions')

        # Warning: Personal dealing mentioned but no controls
        if len(control_elements) == 0:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Personal dealing mentioned without control measures',
                'legal_source': self.legal_source,
                'suggestion': 'SYSC 10.1.11 requires personal account dealing controls. Include: pre-clearance requirements, restricted periods, and disclosure obligations.',
                'spans': spans
            }

        # Warning: Minimal controls
        if len(control_elements) == 1:
            details = []
            for element in control_elements:
                details.append(element)
            for element in missing_elements:
                details.append(f'Missing: {element}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Personal dealing controls may be insufficient',
                'legal_source': self.legal_source,
                'suggestion': f'Consider adding: {", ".join(missing_elements)}. Robust personal dealing policies typically include pre-clearance, restrictions, and disclosure.',
                'spans': spans,
                'details': details
            }

        # Pass: Good controls
        details = []
        for element in control_elements:
            details.append(element)
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Personal dealing controls in place ({len(control_elements)} elements: {", ".join(control_elements)})',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
