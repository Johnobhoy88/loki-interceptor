import re


class DurationReasonablenessGate:
    def __init__(self):
        self.name = "duration_reasonableness"
        self.severity = "high"
        self.legal_source = "Common Law - Restraint of Trade"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a confidentiality agreement',
                'legal_source': self.legal_source
            }
        
        # Check for duration
        duration_patterns = [
            r'\d+\s*years?',
            r'\d+\s*months?',
            r'term.*agreement'
        ]
        
        has_duration = any(re.search(p, text, re.IGNORECASE) for p in duration_patterns)
        
        if not has_duration:
            perpetuity_patterns = [
                r'perpetuity',
                r'indefinitely',
                r'permanent(?:ly)?',
                r'forever',
                r'continues indefinitely',
                r'survives.*termination'  # Without timeframe
            ]

            perpetuity = any(re.search(p, text, re.IGNORECASE) for p in perpetuity_patterns)

            if perpetuity:
                return {
                    'status': 'FAIL',
                    'severity': 'high',
                    'message': 'Indefinite/perpetual confidentiality obligations may be unenforceable',
                    'suggestion': 'Apply fixed term (3-5 years) for general information; perpetual only for genuine trade secrets',
                    'legal_source': self.legal_source
                }

            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No confidentiality duration specified',
                'suggestion': 'Specify: "Obligations continue for [X years] from disclosure date"'
            }
        
        # Check for unreasonably long duration
        long_duration = re.search(r'([1-9]\d+)\s*years?', text, re.IGNORECASE)
        if long_duration and int(long_duration.group(1)) > 10:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'{long_duration.group(1)} year term may be unreasonably long',
                'suggestion': 'Standard commercial terms: 3-5 years; Trade secrets can be indefinite'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'Reasonable duration specified', 'legal_source': self.legal_source}
