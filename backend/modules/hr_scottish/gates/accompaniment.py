import re

class AccompanimentGate:
    def __init__(self):
        self.name = "accompaniment"
        self.severity = "critical"
        self.legal_source = "Employment Relations Act 1999, Section 10"
        self.relevance_keywords = ['disciplinary', 'grievance', 'hearing', 'meeting', 'invited', 'attend']
        self.patterns = [
            r'right to be accompanied',
            r'accompanied by.*(?:colleague|representative|trade union)',
            r'bring.*(?:colleague|representative|trade union)',
            r'may.*bring.*(?:someone|companion|colleague)',
            r'entitled to.*(?:companion|accompaniment)'
        ]

    def _is_relevant(self, text):
        """Check if text is about a disciplinary/grievance process"""
        text_lower = text.lower()
        # Broader detection: disciplinary process OR serious workplace issues + meeting
        process_keywords = ['disciplinary', 'grievance', 'misconduct', 'performance',
                           'conduct', 'complaints', 'concerns', 'allegations', 'investigation',
                           'dismissed', 'dismissal', 'termination', 'suspension', 'warning']
        meeting_keywords = ['hearing', 'meeting', 'invited', 'attend', 'discuss', 'report to']

        has_process = any(kw in text_lower for kw in process_keywords)
        has_meeting = any(kw in text_lower for kw in meeting_keywords)

        # BUG FIX #4: Trigger on immediate dismissal/termination even without meeting keywords
        # Also detect formal notice structures
        immediate_action = any(word in text_lower for word in ['dismissed', 'dismissal', 'termination', 'vacate', 'terminated'])
        formal_notice = ('employee' in text_lower and 'date' in text_lower) or 'notice' in text_lower

        # Trigger if ANY of: (process + meeting) OR immediate_action OR formal_notice
        return (has_process and has_meeting) or immediate_action or (formal_notice and has_process)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary or grievance procedure document',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        issues = []
        warnings = []

        # Check for proper accompaniment rights
        has_accompaniment = False
        for pattern in self.patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_accompaniment = True
                break

        if not has_accompaniment:
            issues.append("No mention of right to be accompanied")

        # Check for restrictions or limitations (these are violations)
        restriction_patterns = [
            r'(?:you )?(?:may not|cannot|must not).*(?:bring|accompanied by).*(?:solicitor|lawyer)',
            r'companion must be.*(?:employee|colleague)',  # Overly restrictive
            r'(?:no|cannot have).*legal representation',
            r'meeting.*(?:alone|unaccompanied|yourself only)',
            r'come by yourself',
            r'attend.*on your own'
        ]

        restrictions_found = []
        for pattern in restriction_patterns:
            match = re.search(pattern, text_lower)
            if match:
                restrictions_found.append(match.group())
                issues.append(f"Potentially unlawful restriction: '{match.group()}'")

        # Check for specific qui can accompany
        mentions_colleague = bool(re.search(r'colleague|co-worker|work.?mate', text_lower))
        mentions_union = bool(re.search(r'trade union|union rep', text_lower))

        if has_accompaniment and not (mentions_colleague or mentions_union):
            warnings.append("Right mentioned but doesn't specify colleague or trade union representative")

        # Check for advance notice requirement for companion
        has_advance_notice = bool(re.search(r'(?:inform|notify|tell).*(?:in advance|beforehand|prior)', text_lower))
        if has_accompaniment and not has_advance_notice:
            warnings.append("Should mention employee must give advance notice of companion's name")

        # Check for inappropriately restrictive wording
        if re.search(r'you may bring one person', text_lower) and not re.search(r'colleague|trade union', text_lower):
            warnings.append("Wording too vague - should specify 'colleague or trade union rep'")

        # Determine status
        if not has_accompaniment or restrictions_found:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Statutory right to accompaniment missing or restricted',
                'details': issues,
                'legal_source': self.legal_source,
                'suggestion': 'Add: "You have the statutory right to be accompanied at this meeting by a work colleague or trade union representative. Please inform us in advance if you wish to be accompanied and provide the name of your companion."',
                'penalty': 'ACAS Code breach can add up to 25% to tribunal awards'
            }

        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Accompaniment rights could be clearer',
                'details': warnings,
                'legal_source': self.legal_source,
                'suggestion': 'Clarify: (1) Companion can be colleague or trade union rep, (2) Employee must give advance notice of companion name'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Statutory right to accompaniment properly stated',
            'legal_source': self.legal_source
        }
