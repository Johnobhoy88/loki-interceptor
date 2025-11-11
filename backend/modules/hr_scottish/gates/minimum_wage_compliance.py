import re


class MinimumWageComplianceGate:
    def __init__(self):
        self.name = "minimum_wage_compliance"
        self.severity = "critical"
        self.legal_source = "National Minimum Wage Act 1998, National Living Wage Regulations"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['wage', 'salary', 'pay', 'remuneration', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        # Check for wage/salary information
        wage_patterns = [
            r'(?:wage|salary|pay|remuneration)',
            r'£\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'per\s+(?:hour|annum|month|week)'
        ]

        mentions_pay = any(re.search(p, text, re.IGNORECASE) for p in wage_patterns)

        if not mentions_pay:
            return {'status': 'N/A', 'message': 'No wage/salary provisions', 'legal_source': self.legal_source}

        elements = {
            'nmw_reference': r'(?:national\s+)?minimum\s+wage|NMW',
            'nlw_reference': r'(?:national\s+)?living\s+wage|NLW',
            'age_bands': r'(?:age|23|21|18|under)',
            'hourly_rate': r'(?:£|per)\s*(?:\d+\.\d{2})?.*(?:per\s+)?hour',
            'working_time': r'working\s+time|hours\s+worked',
            'deductions': r'deduction(?:s)?',
            'accommodation_offset': r'accommodation|living',
            'apprentice_rate': r'apprentice',
            'enforcement': r'HMRC|enforcement',
            'record_keeping': r'(?:record|payroll|pay\s+slip)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for prohibited deductions
        prohibited_deductions = [
            r'(?:cost|charge).*(?:uniform|equipment|tools)',
            r'deduct.*(?:training|course|DBS)',
            r'charge.*(?:required|mandatory)'
        ]

        has_prohibited_deductions = any(re.search(p, text, re.IGNORECASE) for p in prohibited_deductions)

        if has_prohibited_deductions:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Prohibited deductions that may reduce pay below NMW',
                'legal_source': self.legal_source,
                'penalty': 'Arrears, 200% penalty, criminal prosecution, public naming',
                'suggestion': 'Cannot deduct for: uniforms, tools, equipment, training, DBS checks if it reduces pay below NMW'
            }

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Good NMW compliance awareness ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Limited NMW references ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Ensure compliance with NMW/NLW rates, age bands, working time definition, permitted deductions'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'No explicit NMW compliance provisions',
            'legal_source': self.legal_source,
            'note': 'Employer must comply with NMW Act 1998 regardless of contract terms',
            'suggestion': 'Reference NMW/NLW, specify hourly rate, ensure deductions comply'
        }
