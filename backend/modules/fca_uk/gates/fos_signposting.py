import re


class FosSignpostingGate:
    def __init__(self):
        self.name = "fos_signposting"
        self.severity = "critical"
        self.legal_source = "FCA DISP 1.6.2 (Financial Ombudsman Service Signposting)"

    def _is_relevant(self, text):
        """Check if document mentions complaints or final response"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in [
            'complaint', 'final response', 'dissatisfied', 'unhappy with'
        ])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss complaint procedures (FOS signposting required in complaint contexts)',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for Financial Ombudsman Service mention
        fos_patterns = [
            r'financial\s+ombudsman\s+service',
            r'\bfos\b',
            r'ombudsman',
            r'financial-ombudsman\.org\.uk'
        ]

        has_fos_reference = False
        for pattern in fos_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_fos_reference = True
                for m in matches:
                    spans.append({
                        'type': 'fos_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for 6-month time limit
        six_month_patterns = [
            r'6\s+months?',
            r'six\s+months?',
            r'within\s+6\s+months?',
            r'180\s+days?'
        ]

        has_six_month_limit = False
        for pattern in six_month_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check context for FOS/ombudsman/complaint
                for m in matches:
                    context_start = max(0, m.start() - 200)
                    context_end = min(len(text), m.end() + 200)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['ombudsman', 'fos', 'final response', 'complaint', 'refer']):
                        has_six_month_limit = True
                        spans.append({
                            'type': 'six_month_limit',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for FOS contact details
        fos_contact_patterns = [
            r'(?:call|phone|contact).*ombudsman.*0800',
            r'0800\s*023\s*4567',
            r'complaint\.info@financial-ombudsman',
            r'exchange\s+tower.*london.*e14',
            r'financial-ombudsman\.org\.uk'
        ]

        has_fos_contact = False
        for pattern in fos_contact_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_fos_contact = True
                for m in matches:
                    spans.append({
                        'type': 'fos_contact_details',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for "refer to" language
        refer_patterns = [
            r'refer\s+(?:your\s+)?(?:complaint\s+)?to\s+(?:the\s+)?(?:financial\s+)?ombudsman',
            r'contact\s+(?:the\s+)?(?:financial\s+)?ombudsman',
            r'take\s+your\s+complaint\s+to\s+(?:the\s+)?ombudsman',
            r'escalate.*ombudsman',
            r'right\s+to\s+refer'
        ]

        has_refer_language = False
        for pattern in refer_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_refer_language = True
                for m in matches:
                    spans.append({
                        'type': 'fos_referral_language',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for "free to consumer" mention
        free_patterns = [
            r'free\s+(?:of\s+charge|service)',
            r'no\s+(?:cost|charge|fee).*ombudsman',
            r'free.*ombudsman'
        ]

        has_free_mention = False
        for pattern in free_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_free_mention = True
                for m in matches:
                    spans.append({
                        'type': 'fos_free_service',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        issues = []

        # Critical: No FOS reference at all
        if not has_fos_reference:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No Financial Ombudsman Service signposting',
                'legal_source': self.legal_source,
                'suggestion': 'DISP 1.6.2 requires informing customers they can refer complaints to the Financial Ombudsman Service within 6 months of final response.',
                'spans': spans
            }

        # FOS mentioned but missing 6-month time limit
        if not has_six_month_limit:
            issues.append('6-month time limit not stated')

        # FOS mentioned but no contact details
        if not has_fos_contact and not has_refer_language:
            issues.append('How to contact FOS not provided')

        # Warnings or failures
        if len(issues) >= 2:
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Incomplete FOS signposting ({len(issues)} issues)',
                'legal_source': self.legal_source,
                'suggestion': 'Must include: (1) FOS name, (2) 6-month time limit from final response, (3) FOS contact details (0800 023 4567 or financial-ombudsman.org.uk).',
                'spans': spans,
                'details': details
            }

        if len(issues) == 1:
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'FOS signposting incomplete',
                'legal_source': self.legal_source,
                'suggestion': f'Add: {", ".join(issues)}',
                'spans': spans,
                'details': details
            }

        # Pass
        completeness = []
        if has_fos_reference:
            completeness.append('FOS named')
        if has_six_month_limit:
            completeness.append('6-month limit')
        if has_fos_contact or has_refer_language:
            completeness.append('contact details')
        if has_free_mention:
            completeness.append('free service noted')

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'FOS signposting complete ({", ".join(completeness)})',
            'legal_source': self.legal_source,
            'spans': spans
        }
