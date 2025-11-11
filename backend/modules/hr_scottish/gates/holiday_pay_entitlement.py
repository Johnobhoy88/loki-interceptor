import re


class HolidayPayEntitlementGate:
    def __init__(self):
        self.name = "holiday_pay_entitlement"
        self.severity = "high"
        self.legal_source": "Working Time Regulations 1998 reg.13-16"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['holiday', 'annual leave', 'vacation', 'leave'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        holiday_patterns = [
            r'(?:annual\s+)?(?:holiday|leave)',
            r'vacation',
            r'paid\s+(?:time\s+)?off'
        ]

        has_holiday = any(re.search(p, text, re.IGNORECASE) for p in holiday_patterns)

        if not has_holiday:
            return {'status': 'N/A', 'message': 'No holiday provisions', 'legal_source': self.legal_source}

        elements = {
            '28_days': r'(?:5\.6|28)\s+(?:weeks?|days?)',
            'statutory_minimum': r'statutory\s+(?:minimum|entitlement)',
            'accrual': r'accru(?:e|al)|build\s+up',
            'carry_over': r'carry\s+over|roll\s+over',
            'payment_on_termination': r'(?:payment|paid).*(?:termination|leaving|exit)',
            'calculation': r'(?:calculat|week\'s\s+pay|normal\s+pay)',
            'notice_requirement': r'(?:notice|request).*(?:advance|prior)',
            'public_holidays': r'public\s+holiday|bank\s+holiday',
            'part_time_pro_rata': r'pro[- ]rata|proportion(?:al|ate)',
            'sickness_accrual': r'(?:sick|illness).*(?:accrue|continue)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive holiday pay provisions ({score}/10)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Holiday pay provisions incomplete ({score}/10)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:4],
                'suggestion': 'Add: 5.6 weeks/28 days minimum, accrual, calculation method, payment on termination'
            }

        return {
            'status': 'FAIL',
            'severity': 'high',
            'message': 'Inadequate holiday pay provisions',
            'legal_source': self.legal_source,
            'penalty': 'Tribunal claims for unpaid holiday pay; no time limit if series of deductions',
            'suggestion': 'Must provide minimum 5.6 weeks (28 days) per WTR 1998; specify accrual, calculation, carry-over rules'
        }
