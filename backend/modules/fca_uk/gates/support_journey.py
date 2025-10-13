import re


class SupportJourneyGate:
    def __init__(self):
        self.name = "support_journey"
        self.severity = "high"
        self.legal_source = "FCA PRIN 2A.6 (Consumer Support Outcome)"

    def _is_relevant(self, text):
        """Check if document involves customer journey or actions"""
        text_lower = text.lower()
        keywords = [
            'contact', 'support', 'help', 'cancel', 'complaint',
            'withdraw', 'exit', 'close', 'terminate', 'change',
            'phone', 'email', 'customer service'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe customer support, cancellation, or service processes',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for contact routes
        contact_methods = {
            'phone': [r'\+?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{4,6}', r'(?:phone|call|telephone).*\d{4}'],
            'email': [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r'email\s+(?:us\s+)?(?:at|on)'],
            'online': [r'online\s+(?:portal|account|chat)', r'website', r'www\.', r'\.co(?:m|\.uk)'],
            'post': [r'write\s+to\s+us', r'postal\s+address', r'(?:send|post).*to\s+[A-Z]']
        }

        found_contact = []
        for method, patterns in contact_methods.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if method not in found_contact:
                        found_contact.append(method)
                    for m in matches:
                        spans.append({
                            'type': f'contact_{method}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for dark patterns in cancellation/complaints
        dark_patterns = [
            (r'(?:only|must)\s+(?:cancel|complain|contact).*(?:writing|post|letter)', 'phone_cancel_barrier'),
            (r'(?:complete|fill\s+in|submit).*form.*cancel', 'form_barrier'),
            (r'(?:call|contact).*between\s+\d{1,2}(?:am|pm)?\s*-\s*\d{1,2}(?:am|pm)?.*(?:weekday|monday|tuesday)', 'limited_hours'),
            (r'(?:minimum|notice\s+period).*(?:30|60|90)\s+days?.*cancel', 'long_notice'),
            (r'(?:fee|charge|penalty).*(?:cancel|exit|withdraw|close)', 'exit_fee')
        ]

        dark_pattern_found = []
        for pattern, dp_type in dark_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                dark_pattern_found.append(dp_type)
                for m in matches:
                    spans.append({
                        'type': f'dark_pattern_{dp_type}',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for easy support indicators
        easy_support = [
            r'easy\s+to\s+(?:contact|cancel|complain)',
            r'(?:quick|simple|straightforward).*(?:cancel|exit|withdraw)',
            r'(?:24/7|24\s+hours?|anytime)',
            r'no\s+(?:fee|charge|penalty).*(?:cancel|exit)',
            r'online.*(?:cancel|complain|contact)'
        ]

        has_easy_support = False
        for pattern in easy_support:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_easy_support = True
                for m in matches:
                    spans.append({
                        'type': 'easy_support',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        issues = []

        # Critical failure: dark patterns detected
        if dark_pattern_found:
            details = []
            details.append(f'Dark patterns detected: {", ".join(dark_pattern_found)}')
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': f'Dark patterns detected: {", ".join(dark_pattern_found)}',
                'legal_source': self.legal_source,
                'suggestion': 'Consumer Duty prohibits creating barriers. Make cancellation and complaints as easy as purchase. Remove unnecessary friction.',
                'spans': spans,
                'details': details
            }

        # Warning: limited contact options
        if len(found_contact) < 2:
            issues.append('Limited contact methods (need 2+ channels)')

        # Check if cancellation mentioned without clear process
        has_cancel_mention = any(word in text_lower for word in ['cancel', 'exit', 'withdraw', 'close account', 'terminate'])
        has_cancel_process = any(re.search(pattern, text, re.IGNORECASE) for pattern in [
            r'to\s+cancel.*(?:contact|call|email|visit)',
            r'cancel(?:lation)?\s+(?:process|procedure|steps?)',
            r'how\s+to\s+cancel'
        ])

        if has_cancel_mention and not has_cancel_process:
            issues.append('Cancellation mentioned but process not clearly explained')

        if issues:
            details = []
            for issue in issues:
                details.append(issue)
            details.append(f'Contact methods found: {", ".join(found_contact)}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Customer support journey could be clearer',
                'legal_source': self.legal_source,
                'suggestion': 'Provide multiple easy contact routes. Make cancellation/complaints as easy as sign-up.',
                'spans': spans,
                'details': details
            }

        # Pass
        if len(found_contact) >= 2 or has_easy_support:
            details = []
            details.append(f'Contact methods: {", ".join(found_contact)}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Good customer support provisions ({len(found_contact)} contact methods)',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No support journey issues detected',
            'legal_source': self.legal_source,
            'spans': spans
        }
