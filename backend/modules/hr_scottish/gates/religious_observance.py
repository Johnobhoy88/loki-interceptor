import re


class ReligiousObservanceGate:
    def __init__(self):
        self.name = "religious_observance"
        self.severity = "high"
        self.legal_source = "Equality Act 2010 s.4, s.10, Employment Code of Practice"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['religion', 'belief', 'faith', 'observance', 'prayer', 'holiday'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        religious_patterns = [
            r'religion|belief|faith',
            r'religious\s+observance',
            r'prayer|worship'
        ]

        mentions_religion = any(re.search(p, text, re.IGNORECASE) for p in religious_patterns)

        if not mentions_religion:
            return {'status': 'N/A', 'message': 'No religious observance provisions', 'legal_source': self.legal_source}

        elements = {
            'protected_characteristic': r'protected\s+characteristic',
            'accommodation': r'(?:accommodate|allow|permit).*(?:religious|belief|faith)',
            'prayer_breaks': r'(?:prayer|worship).*(?:break|time|facility)',
            'dress_code': r'(?:dress|uniform|clothing).*(?:religious|belief)',
            'dietary': r'diet(?:ary)?|food.*(?:requirement|restriction)',
            'holiday_leave': r'(?:holiday|leave|time\s+off).*(?:religious|festival|observance)',
            'reasonable_adjustment': r'reasonable.*(?:adjustment|accommodation)',
            'flexibility': r'(?:flexible|flexi).*(?:working|hours|arrangement)',
            'discrimination_prohibition': r'(?:not|never).*discriminat.*(?:religion|belief)',
            'consultation': r'(?:discuss|consult).*(?:requirement|need)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for problematic restrictions
        problematic_patterns = [
            r'(?:must|required|compulsory).*(?:remove|not\s+wear).*(?:headscarf|hijab|turban|cross)',
            r'(?:prohibit|ban).*(?:religious|visible).*(?:symbol|garment)',
            r'no\s+(?:prayer|worship).*(?:during|at\s+work)'
        ]

        has_problematic = any(re.search(p, text, re.IGNORECASE) for p in problematic_patterns)

        if has_problematic:
            # Check if there's a proportionate justification
            justification_patterns = [
                r'health\s+and\s+safety|safety\s+requirement',
                r'legitimate.*(?:business|operational)\s+(?:need|requirement)',
                r'proportionate|necessary'
            ]
            has_justification = any(re.search(p, text, re.IGNORECASE) for p in justification_patterns)

            if not has_justification:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Potentially discriminatory religious restrictions without justification',
                    'legal_source': 'Equality Act 2010 s.19 (indirect discrimination)',
                    'penalty': 'Unlimited compensation for religious discrimination',
                    'suggestion': 'Cannot restrict religious dress/observance unless: (1) health & safety requirement, (2) genuine occupational requirement, (3) proportionate means of achieving legitimate aim'
                }

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive religious observance provisions ({score}/10)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic religious observance provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: prayer breaks, dietary accommodation, holiday leave, dress code flexibility'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Limited religious observance provisions',
            'legal_source': self.legal_source,
            'suggestion': 'Add provisions for: prayer/worship time, religious dress, dietary requirements, religious holidays, reasonable accommodations per Equality Act 2010'
        }
