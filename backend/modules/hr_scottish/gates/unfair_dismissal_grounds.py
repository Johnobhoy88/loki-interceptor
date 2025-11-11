import re


class UnfairDismissalGroundsGate:
    def __init__(self):
        self.name = "unfair_dismissal_grounds"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 ss.94-98"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['dismiss', 'terminat', 'disciplinary', 'capability', 'conduct'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        dismissal_patterns = [
            r'dismiss(?:al)?',
            r'terminat(?:e|ion)',
            r'end.*employment'
        ]

        has_dismissal = any(re.search(p, text, re.IGNORECASE) for p in dismissal_patterns)

        if not has_dismissal:
            return {'status': 'N/A', 'message': 'No dismissal provisions', 'legal_source': self.legal_source}

        # Check for potentially fair reasons (s.98)
        fair_reasons = {
            'capability': r'capabilit(?:y|ies)|competenc(?:e|y)|performance|qualification',
            'conduct': r'misconduct|conduct|disciplinary',
            'redundancy': r'redundan(?:cy|t)',
            'statutory_bar': r'(?:statutory|legal).*(?:bar|restriction|continu)',
            'some_other_substantial_reason': r'(?:SOSR|some\s+other\s+substantial\s+reason|business\s+(?:need|reorganisation))'
        }

        found_reasons = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in fair_reasons.items()}

        # Check for automatically unfair reasons
        automatically_unfair = {
            'pregnancy': r'pregnan(?:cy|t)|maternity',
            'family_leave': r'(?:maternity|paternity|adoption|parental)\s+leave',
            'flexible_working': r'flexible\s+working.*request',
            'health_safety': r'health\s+and\s+safety',
            'whistleblowing': r'whistleblow|protected\s+disclosure',
            'trade_union': r'trade\s+union|union\s+(?:member|activity)',
            'part_time': r'part[- ]time|(?:less\s+favourable|discriminat).*part[- ]time',
            'fixed_term': r'fixed[- ]term',
            'minimum_wage': r'(?:minimum|living)\s+wage|assert.*(?:statutory\s+)?right',
            'working_time': r'working\s+time.*(?:refuse|limit)'
        }

        found_unfair = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in automatically_unfair.items()}

        # Check for procedural fairness elements
        procedural_elements = {
            'investigation': r'investigat',
            'meeting': r'(?:disciplinary|capability)\s+(?:meeting|hearing)',
            'evidence': r'evidence',
            'right_to_be_accompanied': r'(?:accompan|representative)',
            'decision': r'decision.*(?:writing|written)',
            'appeal': r'appeal',
            'warnings': r'warning(?:s)?|progressive',
            'acas_code': r'ACAS\s+Code'
        }

        found_procedural = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in procedural_elements.items()}

        fair_score = sum(found_reasons.values())
        procedural_score = sum(found_procedural.values())

        # Check if any automatically unfair reason mentioned in dismissal context
        for reason_type, found in found_unfair.items():
            if found:
                # Check if it's mentioned as prohibited
                protection_patterns = [
                    r'(?:not|never).*dismiss.*' + reason_type,
                    r'unfair.*dismiss.*' + reason_type,
                    r'protect.*' + reason_type
                ]
                is_protected = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)

                if not is_protected:
                    return {
                        'status': 'FAIL',
                        'severity': 'critical',
                        'message': f'Automatically unfair dismissal ground mentioned: {reason_type}',
                        'legal_source': 'Employment Rights Act 1996 s.104',
                        'penalty': 'Automatic unfair dismissal; no qualifying period; unlimited compensation',
                        'suggestion': f'Cannot dismiss for: {reason_type}. Ensure policy explicitly protects against automatically unfair dismissals'
                    }

        if fair_score >= 3 and procedural_score >= 5:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Good dismissal framework ({fair_score}/5 reasons, {procedural_score}/8 procedures)',
                'legal_source': self.legal_source,
                'fair_reasons': [k for k, v in found_reasons.items() if v],
                'procedural_elements': [k for k, v in found_procedural.items() if v]
            }

        if fair_score >= 2 and procedural_score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Dismissal provisions incomplete ({fair_score}/5 reasons, {procedural_score}/8 procedures)',
                'legal_source': self.legal_source,
                'suggestion': 'Follow ACAS Code: investigation, meeting, evidence, representation, decision, appeal. Only dismiss for fair reason.'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate unfair dismissal safeguards',
            'legal_source': self.legal_source,
            'penalty': 'Basic award + compensatory award (up to £115,115 or 52 weeks pay)',
            'suggestion': 'Must have fair reason (capability, conduct, redundancy, statutory bar, SOSR) + fair procedure per ACAS Code'
        }
