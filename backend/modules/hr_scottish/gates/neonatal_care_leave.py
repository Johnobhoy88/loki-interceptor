import re


class NeonatalCareLeaveGate:
    def __init__(self):
        self.name = "neonatal_care_leave"
        self.severity = "medium"
        self.legal_source = "Neonatal Care Leave and Pay Act 2023, Employment Rights Act 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['neonatal', 'nicu', 'premature', 'special care', 'baby', 'newborn'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        neonatal_patterns = [
            r'neonatal\s+(?:care\s+)?leave',
            r'(?:NICU|neonatal\s+intensive\s+care)',
            r'(?:special\s+care|neonatal\s+unit).*leave',
            r'premature.*baby.*leave'
        ]

        has_neonatal = any(re.search(p, text, re.IGNORECASE) for p in neonatal_patterns)

        if not has_neonatal:
            return {'status': 'N/A', 'message': 'No neonatal care leave provisions', 'legal_source': self.legal_source}

        elements = {
            '12_weeks': r'(?:12|twelve)\s+weeks?',
            'both_parents': r'(?:both|each)\s+(?:parent|partner)',
            'day_one_right': r'(?:day\s+one|from\s+(?:start|commencement))|(?:all\s+employees)',
            'continuous_period': r'(?:7|seven)\s+(?:consecutive\s+)?days?.*(?:hospital|care)',
            'neonatal_pay': r'neonatal.*pay|statutory.*pay',
            'notification': r'(?:notice|notify).*(?:employer|manager)',
            'evidence': r'(?:evidence|certificate).*(?:hospital|medical|healthcare)',
            'protection': r'(?:not|no).*detriment.*neonatal',
            'first_year': r'(?:first|within)\s+(?:year|12\s+months?)',
            'flexible': r'(?:flexible|block|pattern).*(?:take|use)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 7:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive neonatal care leave ({score}/10 elements) - compliant with 2023 Act',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Neonatal care leave incomplete ({score}/10)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v],
                'suggestion': 'Neonatal Care Leave Act 2023: 12 weeks per parent, day one right, baby in neonatal care 7+ continuous days in first year, notification + evidence, statutory pay, protection from detriment'
            }

        if score >= 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Basic neonatal provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Expand to meet 2023 Act: 12 weeks each parent, day one right, continuous 7-day hospitalization, notification/evidence requirements, protection'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Neonatal care leave mentioned without detail',
            'legal_source': self.legal_source,
            'suggestion': 'Implement Neonatal Care Leave Act 2023 provisions: up to 12 weeks per parent (additional to other leave), day one right, for babies in neonatal care 7+ days in first year, statutory neonatal pay'
        }
