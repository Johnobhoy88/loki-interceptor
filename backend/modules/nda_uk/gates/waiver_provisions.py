import re


class WaiverProvisionsGate:
    def __init__(self):
        self.name = "waiver_provisions"
        self.severity = "low"
        self.legal_source = "Contract Law, Waiver doctrine"

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

        # Check for waiver provisions
        waiver_patterns = [
            r'waiver',
            r'failure\s+to\s+(?:enforce|exercise)',
            r'no\s+(?:single|partial).*(?:waiver|exercise)',
            r'delay\s+in\s+(?:enforc|exercis)'
        ]

        has_waiver_clause = any(re.search(p, text, re.IGNORECASE) for p in waiver_patterns)

        if not has_waiver_clause:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No waiver provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding no-waiver clause to preserve rights',
                'risk': 'Delay or failure to enforce may be construed as waiver'
            }

        # Check for non-waiver language
        non_waiver_patterns = [
            r'(?:no|not).*waiver',
            r'failure.*(?:not|shall\s+not).*(?:constitute|deemed).*waiver',
            r'delay.*(?:not|shall\s+not).*waiver',
            r'single.*(?:not|shall\s+not).*prevent'
        ]

        has_non_waiver = any(re.search(p, text, re.IGNORECASE) for p in non_waiver_patterns)

        # Check for cumulative rights
        cumulative_patterns = [
            r'cumulat(?:ive|ively)',
            r'not\s+exclusive',
            r'in\s+addition\s+to',
            r'(?:remedies|rights).*not.*exclusive'
        ]

        has_cumulative = any(re.search(p, text, re.IGNORECASE) for p in cumulative_patterns)

        # Check for written waiver requirement
        written_patterns = [
            r'waiver.*(?:must|shall).*(?:be\s+)?in\s+writing',
            r'written\s+waiver',
            r'signed.*waiver'
        ]

        requires_written = any(re.search(p, text, re.IGNORECASE) for p in written_patterns)

        if has_non_waiver and has_cumulative and requires_written:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive waiver provisions with written requirement',
                'legal_source': self.legal_source
            }

        if has_non_waiver and has_cumulative:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Non-waiver and cumulative rights provisions included',
                'legal_source': self.legal_source
            }

        if has_non_waiver:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Non-waiver provision included',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding that rights are cumulative and non-exclusive'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Waiver mentioned but provisions unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify that failure to enforce does not constitute waiver'
        }
