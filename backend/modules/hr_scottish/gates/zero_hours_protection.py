import re


class ZeroHoursProtectionGate:
    def __init__(self):
        self.name = "zero_hours_protection"
        self.severity = "high"
        self.legal_source = "Employment Rights Act 1996 s.27A, Exclusivity Terms in Zero Hours Contracts Regulations 2022"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['zero', 'casual', 'variable', 'hours', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        zero_hours_patterns = [
            r'zero[- ]hours?',
            r'casual\s+(?:worker|employment)',
            r'variable\s+hours?',
            r'no\s+guarantee.*hours?'
        ]

        is_zero_hours = any(re.search(p, text, re.IGNORECASE) for p in zero_hours_patterns)

        if not is_zero_hours:
            return {'status': 'N/A', 'message': 'Not a zero hours contract', 'legal_source': self.legal_source}

        # Check for prohibited exclusivity clause
        exclusivity_patterns = [
            r'(?:shall\s+not|not\s+permitted\s+to).*(?:work\s+for|employed\s+by).*(?:other|another)',
            r'exclusive(?:ly)?.*(?:service|employment)',
            r'(?:prohibit|restrict).*(?:other\s+employment|working\s+elsewhere)'
        ]

        has_exclusivity = any(re.search(p, text, re.IGNORECASE) for p in exclusivity_patterns)

        if has_exclusivity:
            # Check for opt-out (valid if employee has opted out)
            opt_out_patterns = [
                r'opt[- ]out',
                r'employee.*(?:agree|consent).*exclusivity',
                r'unless.*(?:agreed|consented)'
            ]
            has_opt_out = any(re.search(p, text, re.IGNORECASE) for p in opt_out_patterns)

            if not has_opt_out:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Prohibited exclusivity clause in zero hours contract',
                    'legal_source': 'Exclusivity Terms Regulations 2022',
                    'penalty': 'Clause is unenforceable; tribunal claim possible',
                    'suggestion': 'Remove exclusivity clause or add opt-out provision (employee must expressly agree)'
                }

        elements = {
            'no_guarantee': r'(?:no|not)\s+guarantee.*(?:hours?|work)',
            'right_to_refuse': r'(?:right\s+to|may)\s+(?:refuse|decline|reject)\s+(?:work|shift)',
            'notice_of_shifts': r'(?:notice|advance).*(?:shift|work|rota)',
            'holiday_pay': r'holiday\s+pay|annual\s+leave',
            'ssp_entitlement': r'(?:sick|SSP)',
            'no_detriment': r'(?:no|not).*detriment.*(?:refus|declin)',
            'written_statement': r'written\s+(?:statement|particulars)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 5:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Compliant zero hours contract ({score}/7 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Zero hours contract incomplete ({score}/7)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v],
                'suggestion': 'Add: no guarantee, right to refuse, notice of shifts, holiday pay, no detriment'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Zero hours contract lacks key protections',
            'legal_source': self.legal_source,
            'suggestion': 'Ensure: no exclusivity, no guarantee of hours, right to refuse work, holiday/SSP entitlement, no detriment for refusing'
        }
