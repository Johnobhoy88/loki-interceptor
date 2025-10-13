import re


class InformalThreatsGate:
    def __init__(self):
        self.name = "informal_threats"
        self.severity = "critical"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"

    def _is_relevant(self, text):
        """Detect informal disciplinary/threatening language"""
        text_lower = (text or '').lower()

        # Informal disciplinary indicators
        informal_keywords = [
            'report to hr',
            'risk losing',
            'losing your job',
            'lose your job',
            'job is at risk',
            'final chance',
            'last warning',
            'must improve',
            'not acceptable',
            'too many',
            'too often',
            'attendance',
            'absence',
            'late',
            'performance issues',
            'your behavior',
            'unacceptable'
        ]

        has_informal = any(kw in text_lower for kw in informal_keywords)

        # Check for threatening/action language
        action_patterns = [
            r'report to\s+(?:hr|manager|supervisor)',
            r'(?:risk|could|may)\s+(?:lose|losing)',
            r'(?:lose|losing)\s+(?:your|the)\s+job',
            r'immediate(?:ly)?\s+(?:action|meeting)',
            r'see\s+(?:me|us|hr)',
            r'discuss\s+(?:this|your)',
        ]

        has_action = any(re.search(p, text_lower) for p in action_patterns)

        return has_informal or has_action

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a disciplinary communication',
                'legal_source': self.legal_source
            }

        text_lower = (text or '').lower()

        # Check for proper formal process indicators
        formal_indicators = [
            r'formal\s+(?:disciplinary|process|procedure)',
            r'disciplinary\s+(?:hearing|meeting|process)',
            r'investigation\s+(?:into|of|report)',
            r'right\s+to\s+(?:be\s+)?accompanied',
            r'appeal\s+this\s+decision',
            r'evidence\s+(?:attached|enclosed)',
            r'acas\s+code',
            r'following\s+investigation'
        ]

        has_formal_process = any(re.search(p, text_lower) for p in formal_indicators)

        if has_formal_process:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Formal process referenced despite informal tone'
            }

        # Detect specific informal violations
        violations = []

        if 'report to' in text_lower and 'immediate' in text_lower:
            violations.append("Requires immediate meeting without proper notice")

        if any(phrase in text_lower for phrase in ['risk losing', 'lose your job', 'losing your job']):
            violations.append("Threatens job loss without formal disciplinary procedure")

        if any(phrase in text_lower for phrase in ['too often', 'too many', 'not acceptable']) and 'specific' not in text_lower:
            violations.append("Vague allegations without specific details")

        if 'meeting' not in text_lower and 'hearing' not in text_lower:
            violations.append("No formal meeting/hearing arranged")

        if 'accompanied' not in text_lower and 'representative' not in text_lower:
            violations.append("No mention of right to be accompanied")

        if not violations:
            violations.append("Informal threatening language without proper ACAS procedure")

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Informal disciplinary threat violates ACAS Code requirements',
            'legal_source': self.legal_source,
            'suggestion': 'Use formal disciplinary procedure: arrange proper meeting, provide specific allegations, notify of right to accompaniment, allow time to prepare, conduct investigation first.',
            'details': violations
        }
