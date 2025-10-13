import re


class AllegationsGate:
    def __init__(self):
        self.name = "allegations"
        self.severity = "high"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"

    def _is_relevant(self, text):
        text_lower = text.lower()
        # Broader detection: any workplace issue that requires clear allegations
        relevant_keywords = ['disciplinary', 'grievance', 'misconduct', 'allegations',
                            'complaints', 'concerns', 'conduct', 'performance issue',
                            'dismissed', 'dismissal', 'terminated', 'warning']
        return any(kw in text_lower for kw in relevant_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe disciplinary allegations or misconduct',
                'legal_source': self.legal_source
            }

        issues = []
        vague_spans = []
        text_lower = text.lower()

        # Check for specific dates/details
        has_dates = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text, re.IGNORECASE))
        has_times = bool(re.search(r'\d{1,2}:\d{2}|(?:\d+\s*(?:am|pm))', text, re.IGNORECASE))

        # Extended vague terms that AI commonly generates
        vague_terms = [
            'poor attitude', 'bad attitude', 'unprofessional', 'inappropriate',
            'unacceptable behaviour', 'unacceptable behavior', 'concerns about',
            'issues with', 'problems with', 'poor performance', 'below standard',
            'not meeting expectations', 'lack of', 'failure to', 'too often',
            'too many', 'several times', 'on occasion', 'repeatedly'
        ]

        for term in vague_terms:
            for match in re.finditer(re.escape(term), text, re.IGNORECASE):
                vague_spans.append({
                    'type': 'vague_allegation',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'high'
                })

        # Check for specific incident descriptions
        has_who = bool(re.search(r'(?:witness|present|reported by|complained by)', text_lower))
        has_where = bool(re.search(r'(?:in|at|on)\s+(?:the\s+)?(?:office|workplace|room|site|location)', text_lower))
        has_what_happened = bool(re.search(r'(?:said|did|failed to|refused to|was seen)', text_lower))

        # Analyze specificity
        if vague_spans:
            issues.append(f"{len(vague_spans)} vague term(s) without specific examples")

        if not has_dates:
            issues.append("No specific dates of alleged incidents")

        if not has_times and ('meeting' not in text_lower):
            issues.append("No specific times provided for incidents")

        if not has_who:
            issues.append("No witnesses or reporting parties mentioned")

        if not has_where:
            issues.append("No locations specified for incidents")

        if not has_what_happened and len(text) > 100:
            issues.append("No clear description of what specifically occurred")

        # Quantitative check for very short allegations
        allegation_words = len(text.split())
        if allegation_words < 50 and any(kw in text_lower for kw in ['misconduct', 'disciplinary', 'allegation']):
            issues.append(f"Allegation very brief ({allegation_words} words) - lacks detail")

        # Check for patterns that indicate proper detail
        # More lenient: dates OR what_happened OR specific incident details
        has_proper_detail = (has_dates and has_what_happened) or (has_who and has_where and has_dates) or (has_dates and len(issues) < 4)

        if has_proper_detail and not vague_spans:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Allegations include sufficient specific details',
                'spans': [],
                'legal_source': self.legal_source
            }

        # Only fail if MANY issues AND vague language
        if len(issues) >= 5 or len(vague_spans) >= 3:
            return {
                'status': 'FAIL',
                'severity': 'high',  # Changed from critical - allows better risk calibration
                'message': f'Allegations lack specificity ({len(issues)} issues found)',
                'spans': vague_spans,
                'details': issues,
                'suggestion': 'Include: (1) Specific dates and times, (2) Exact locations, (3) Clear description of what was said/done, (4) Names of witnesses, (5) Specific examples of conduct/behavior.',
                'legal_source': self.legal_source
            }

        if issues or vague_spans:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Allegations could be more specific',
                'spans': vague_spans,
                'details': issues,
                'suggestion': 'Add more specific details: dates, times, locations, and concrete examples.',
                'legal_source': self.legal_source
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Allegations include specific details',
            'spans': [],
            'legal_source': self.legal_source
        }
