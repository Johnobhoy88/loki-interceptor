import re


class ComplaintRouteClockGate:
    def __init__(self):
        self.name = "complaint_route_clock"
        self.severity = "critical"
        self.legal_source = "FCA DISP 1.6 (Complaints Time Limits)"

    def _is_relevant(self, text):
        """Check if document mentions complaints"""
        text_lower = text.lower()
        return 'complaint' in text_lower or 'complain' in text_lower or 'dissatisfied' in text_lower

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain complaint handling procedures',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for 8-week time limit mention
        eight_week_patterns = [
            r'8\s+weeks?',
            r'eight\s+weeks?',
            r'56\s+days?',
            r'within\s+8\s+weeks?',
            r'by\s+8\s+weeks?'
        ]

        has_eight_week_limit = False
        for pattern in eight_week_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if it's in context of complaints/response
                for m in matches:
                    context_start = max(0, m.start() - 150)
                    context_end = min(len(text), m.end() + 150)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['complaint', 'response', 'reply', 'final', 'resolve']):
                        has_eight_week_limit = True
                        spans.append({
                            'type': 'eight_week_limit',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for "final response" mention
        final_response_patterns = [
            r'final\s+response',
            r'final\s+decision',
            r'our\s+final\s+(?:view|position)',
            r'complaint\s+resolution'
        ]

        has_final_response = False
        for pattern in final_response_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_final_response = True
                for m in matches:
                    spans.append({
                        'type': 'final_response_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for how to complain information
        complaint_method_patterns = [
            r'(?:to\s+)?(?:make|lodge|submit|raise)\s+a\s+complaint',
            r'how\s+to\s+complain',
            r'complaints?\s+(?:procedure|process)',
            r'contact\s+(?:us\s+)?(?:to\s+)?complain',
            r'write\s+to.*complaint',
            r'email.*complaint',
            r'call.*complaint'
        ]

        has_complaint_method = False
        for pattern in complaint_method_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_complaint_method = True
                for m in matches:
                    spans.append({
                        'type': 'complaint_method',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for contact details for complaints
        has_complaint_contact = any(re.search(pattern, text, re.IGNORECASE) for pattern in [
            r'complaints?\s+(?:department|team|handler)',
            r'(?:email|write\s+to|call).*complaint',
            r'complaint.*(?:@|tel|phone)',
        ])

        # Determine status
        issues = []

        # Critical: No 8-week time limit mentioned
        if not has_eight_week_limit:
            issues.append('8-week final response time limit not stated')

        # No complaint method/contact
        if not has_complaint_method and not has_complaint_contact:
            issues.append('How to make a complaint not explained')

        # Critical failure: missing time limit
        if not has_eight_week_limit:
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing mandatory 8-week final response time limit',
                'legal_source': self.legal_source,
                'suggestion': 'FCA DISP rules require stating: "We will send you a final response within 8 weeks of receiving your complaint."',
                'spans': spans,
                'details': details
            }

        # Warning: time limit present but process unclear
        if not has_complaint_method:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Time limit stated but complaint process could be clearer',
                'legal_source': self.legal_source,
                'suggestion': 'Clearly explain how customers can make a complaint (phone, email, post, online).',
                'spans': spans
            }

        # Pass
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Complaint time limit and process adequately described',
            'legal_source': self.legal_source,
            'spans': spans
        }
