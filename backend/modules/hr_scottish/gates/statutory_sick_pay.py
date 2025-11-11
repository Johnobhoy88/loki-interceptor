import re


class StatutorySickPayGate:
    def __init__(self):
        self.name = "statutory_sick_pay"
        self.severity = "high"
        self.legal_source = "Social Security Contributions and Benefits Act 1992, SSP Regulations"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['sick', 'illness', 'absence', 'ssp', 'policy', 'procedure'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - no sick pay provisions',
                'legal_source': self.legal_source
            }

        # Check for SSP mention
        ssp_patterns = [
            r'(?:statutory\s+)?sick\s+pay|SSP',
            r'entitle(?:d|ment).*sick(?:ness)?.*pay',
            r'absence.*(?:due\s+to\s+)?(?:illness|sickness)'
        ]

        mentions_sick_pay = any(re.search(p, text, re.IGNORECASE) for p in ssp_patterns)

        if not mentions_sick_pay:
            return {
                'status': 'N/A',
                'message': 'No sick pay provisions',
                'legal_source': self.legal_source
            }

        # Check for qualifying days (4+ consecutive days)
        qualifying_patterns = [
            r'(?:after|from)\s+(?:the\s+)?(?:4th|fourth)\s+(?:consecutive\s+)?day',
            r'qualifying\s+days?',
            r'waiting\s+days?'
        ]

        has_qualifying_period = any(re.search(p, text, re.IGNORECASE) for p in qualifying_patterns)

        # Check for medical evidence requirements
        medical_evidence_patterns = [
            r'(?:doctor|medical|GP|fit\s+note|doctor\'s\s+note)',
            r'self[- ]certif(?:y|ication)',
            r'(?:after|from)\s+7\s+days?',
            r'medical\s+evidence'
        ]

        requires_evidence = any(re.search(p, text, re.IGNORECASE) for p in medical_evidence_patterns)

        # Check for notification requirements
        notification_patterns = [
            r'(?:notify|inform|report).*(?:manager|supervisor|employer)',
            r'as\s+soon\s+as\s+(?:possible|practicable)',
            r'first\s+day.*(?:absence|sickness)',
            r'within\s+\d+\s+(?:hour|day)'
        ]

        has_notification = any(re.search(p, text, re.IGNORECASE) for p in notification_patterns)

        # Check for SSP rate reference
        rate_patterns = [
            r'statutory\s+rate',
            r'£\s*\d+(?:\.\d{2})?.*(?:per\s+week|weekly)',
            r'prescribed\s+rate'
        ]

        mentions_rate = any(re.search(p, text, re.IGNORECASE) for p in rate_patterns)

        # Check for maximum entitlement period (28 weeks)
        max_period_patterns = [
            r'28\s+weeks?',
            r'maximum.*(?:entitlement|period)',
            r'up\s+to.*weeks?'
        ]

        mentions_max_period = any(re.search(p, text, re.IGNORECASE) for p in max_period_patterns)

        # Check for return to work
        return_to_work_patterns = [
            r'return[- ]to[- ]work',
            r'(?:fit|able)\s+to\s+return',
            r'resumption\s+of\s+(?:work|duties)'
        ]

        addresses_return = any(re.search(p, text, re.IGNORECASE) for p in return_to_work_patterns)

        elements_present = sum([
            has_qualifying_period,
            requires_evidence,
            has_notification,
            mentions_rate,
            mentions_max_period,
            addresses_return
        ])

        if elements_present >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive SSP provisions ({elements_present}/6 elements)',
                'legal_source': self.legal_source
            }

        if elements_present >= 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Basic SSP provisions but incomplete ({elements_present}/6)',
                'legal_source': self.legal_source,
                'suggestion': 'Ensure policy covers: qualifying days, medical evidence from day 8, notification requirements, statutory rate'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Sick pay provisions lack statutory requirements',
            'legal_source': self.legal_source,
            'penalty': 'Employer may be liable for unpaid SSP claims',
            'suggestion': 'Add: 4-day qualifying period, medical evidence (self-cert up to 7 days), notification process, SSP rate, 28-week limit'
        }
