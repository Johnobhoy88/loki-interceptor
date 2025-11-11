import re


class ForceMajeureGate:
    def __init__(self):
        self.name = "force_majeure"
        self.severity = "low"
        self.legal_source = "Contract Law, Frustration doctrine"

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

        # Check for force majeure clause
        fm_patterns = [
            r'force\s+majeure',
            r'act\s+of\s+god',
            r'beyond.*reasonable\s+control',
            r'unforeseeable\s+(?:event|circumstance)'
        ]

        has_fm = any(re.search(p, text, re.IGNORECASE) for p in fm_patterns)

        if not has_fm:
            return {
                'status': 'N/A',
                'message': 'No force majeure provision (not always necessary)',
                'legal_source': self.legal_source,
                'note': 'UK law has narrow frustration doctrine; force majeure clause recommended for commercial contracts'
            }

        # Check for specific events listed
        fm_events = {
            'natural_disasters': r'(?:earthquake|flood|hurricane|tsunami|fire|storm)',
            'war': r'(?:war|hostilities|invasion|terrorism|civil\s+(?:war|unrest))',
            'government_action': r'(?:government|state|regulatory)\s+(?:action|intervention|order|embargo)',
            'pandemic': r'(?:pandemic|epidemic|plague|disease\s+outbreak)',
            'strikes': r'(?:strike|labour\s+dispute|industrial\s+action)',
            'utilities': r'(?:power|electricity|utility)\s+(?:failure|outage)',
            'cyber': r'(?:cyber|hacking|computer\s+virus)'
        }

        found_events = []
        for event_type, pattern in fm_events.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_events.append(event_type)

        # Check for notice requirement
        notice_patterns = [
            r'(?:notify|notice).*force\s+majeure',
            r'(?:promptly|immediately).*(?:notify|inform)',
            r'written\s+notice.*(?:event|circumstance)'
        ]

        has_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        # Check for mitigation obligation
        mitigation_patterns = [
            r'mitigate',
            r'reasonable\s+(?:efforts|endeavours).*(?:overcome|avoid)',
            r'minimise.*(?:effect|impact)'
        ]

        has_mitigation = any(re.search(p, text, re.IGNORECASE) for p in mitigation_patterns)

        # Check for termination rights
        termination_patterns = [
            r'(?:terminate|termination).*force\s+majeure',
            r'(?:continue|persist).*\d+.*(?:day|month).*(?:terminate|end)',
            r'right\s+to\s+(?:terminate|end).*(?:event|circumstance)'
        ]

        has_termination = any(re.search(p, text, re.IGNORECASE) for p in termination_patterns)

        score = len(found_events)
        if has_notice:
            score += 1
        if has_mitigation:
            score += 1
        if has_termination:
            score += 1

        if score >= 5:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive force majeure clause',
                'legal_source': self.legal_source,
                'events_covered': found_events
            }

        if score >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Adequate force majeure clause',
                'legal_source': self.legal_source,
                'events_covered': found_events,
                'suggestion': 'Consider adding: notice requirement, mitigation obligation, termination rights'
            }

        missing = []
        if len(found_events) < 3:
            missing.append('specific events')
        if not has_notice:
            missing.append('notice requirement')
        if not has_mitigation:
            missing.append('mitigation obligation')
        if not has_termination:
            missing.append('termination rights')

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Force majeure clause incomplete',
            'legal_source': self.legal_source,
            'events_covered': found_events,
            'missing': missing,
            'suggestion': 'Add specific events, notice requirement, and mitigation obligation'
        }
