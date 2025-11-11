import re


class RightToDisconnectGate:
    def __init__(self):
        self.name = "right_to_disconnect"
        self.severity = "medium"
        self.legal_source = "Working Time Regulations 1998, Employment Rights Act 2023, Health and Safety at Work Act 1974"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['disconnect', 'out of hours', 'working time', 'email', 'contact', 'availability'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        disconnect_patterns = [
            r'right\s+to\s+disconnect',
            r'(?:outside|out\s+of).*(?:working\s+hours|office\s+hours)',
            r'(?:not|no).*(?:required|expected).*(?:respond|answer|available).*(?:outside|after\s+hours)'
        ]

        has_disconnect = any(re.search(p, text, re.IGNORECASE) for p in disconnect_patterns)

        elements = {
            'working_hours_defined': r'(?:working|office|core)\s+hours?.*(?:\d+|am|pm|to)',
            'no_expectation_outside_hours': r'(?:not|no).*(?:expect|require).*(?:outside|after|before).*hours?',
            'email_policy': r'(?:email|message|contact).*(?:outside|out\s+of).*hours?',
            'respect_boundaries': r'respect.*(?:boundary|boundaries|work[- ]life)',
            'work_life_balance': r'work[- ]life\s+balance',
            'emergency_exception': r'emergency|urgent|critical',
            'on_call_separate': r'(?:on[- ]call|standby).*(?:separate|additional|compensat)',
            'overtime_approval': r'overtime.*(?:approval|authorised|authorized)',
            'rest_periods': r'(?:rest|break).*(?:period|entitle)',
            'stress_prevention': r'(?:stress|burnout|wellbeing|mental\s+health)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for problematic always-on culture
        always_on_patterns = [
            r'(?:must|required|expected).*(?:available|respond).*(?:24|at\s+all\s+times)',
            r'(?:always|constantly)\s+(?:available|contactable)',
            r'(?:respond|reply).*(?:immediately|promptly).*(?:any\s+time|regardless)'
        ]

        has_always_on = any(re.search(p, text, re.IGNORECASE) for p in always_on_patterns)

        if has_always_on:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': '"Always-on" culture detected - health and safety risk',
                'legal_source': 'Working Time Regulations 1998, HSWA 1974 (duty to protect mental health)',
                'suggestion': 'Excessive availability expectations breach WTR rest requirements and create stress/burnout risk. Define working hours, right to disconnect, emergency exceptions only.'
            }

        if has_disconnect or score >= 5:
            if score >= 7:
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': f'Strong right to disconnect provisions ({score}/10 elements)',
                    'legal_source': self.legal_source,
                    'elements_found': [k for k, v in found.items() if v]
                }

            if score >= 4:
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': f'Basic right to disconnect provisions ({score}/10)',
                    'legal_source': self.legal_source,
                    'suggestion': 'Consider adding: emergency exceptions, on-call compensation, stress prevention, work-life balance support'
                }

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Right to disconnect mentioned',
                'legal_source': self.legal_source,
                'suggestion': 'Strengthen policy: define working hours, no expectation to respond outside hours, respect boundaries, emergency exceptions only'
            }

        return {
            'status': 'N/A',
            'message': 'No right to disconnect provisions',
            'legal_source': self.legal_source,
            'note': 'Consider adding right to disconnect policy to support work-life balance and comply with WTR rest requirements'
        }
