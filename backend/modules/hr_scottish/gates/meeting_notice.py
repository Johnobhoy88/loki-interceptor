import re
from datetime import datetime, timedelta


class MeetingNoticeGate:
    def __init__(self):
        self.name = "meeting_notice"
        self.severity = "high"
        self.legal_source = "ACAS Code - Reasonable notice required"

    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['disciplinary', 'grievance', 'hearing', 'meeting', 'investigation'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary or grievance meeting invitation',
                'legal_source': self.legal_source
            }

        lower = text.lower()
        issues = []
        matches = []

        # Check for urgent/immediate requirements
        urgent_indicators = [
            'immediate', 'immediately', 'today', 'tomorrow', 'asap',
            'as soon as possible', 'urgent', 'right now', 'right away',
            'this afternoon', 'this morning', 'end of day'
        ]

        for ind in urgent_indicators:
            for m in re.finditer(re.escape(ind), lower, re.IGNORECASE):
                matches.append({
                    'type': 'short_notice',
                    'start': m.start(),
                    'end': m.end(),
                    'text': text[m.start():m.end()],
                    'severity': 'high'
                })
                issues.append(f"Requires '{ind}' action - no reasonable notice period")

        # Check for specific dates that might be too soon
        # Look for patterns like "meeting on [date]" where date is very soon
        date_patterns = [
            r'meeting.*?(?:on|at)\s+(\d{1,2}[/-]\d{1,2})',  # meeting on 10/5
            r'(?:hearing|meeting).*?(\w+day)',  # meeting Monday, Tuesday, etc.
        ]

        for pattern in date_patterns:
            if re.search(pattern, lower):
                if 'tomorrow' in lower or 'today' in lower:
                    issues.append("Same-day or next-day meeting scheduling")

        # Check for lack of meeting details
        has_date = bool(re.search(r'\d{1,2}[/-]\d{1,2}|(?:monday|tuesday|wednesday|thursday|friday)', lower))
        has_time = bool(re.search(r'\d{1,2}:\d{2}|(?:\d+\s*(?:am|pm))', lower))
        has_location = bool(re.search(r'(?:room|office|location|venue|teams|zoom|address)', lower))

        if not has_date and 'meeting' in lower:
            issues.append("No specific date provided for meeting")
        if not has_time and 'meeting' in lower:
            issues.append("No specific time provided for meeting")
        if not has_location and 'meeting' in lower and 'online' not in lower:
            issues.append("No location or format specified for meeting")

        # Critical failure: immediate action required
        if matches:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Inadequate notice period detected ({len(matches)} instances)',
                'spans': matches,
                'details': issues,
                'suggestion': 'Provide at least 48 hours notice for disciplinary meetings. Specify date, time, and location clearly.'
            }

        # Warning: missing important details
        if issues:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Meeting notice missing important details',
                'details': issues,
                'suggestion': 'Include specific date, time, and location/format for the meeting.'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Adequate notice period and meeting details provided',
            'spans': []
        }
