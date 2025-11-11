import re


class ProtectedCharacteristicsGate:
    def __init__(self):
        self.name = "protected_characteristics"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010 s.4"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['discrimin', 'equal', 'diversity', 'protected', 'policy', 'procedure'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        discrimination_patterns = [
            r'discriminat(?:ion|ory)',
            r'equal(?:ity)?\s+(?:opportunity|treatment)',
            r'protected\s+characteristic'
        ]

        mentions_discrimination = any(re.search(p, text, re.IGNORECASE) for p in discrimination_patterns)

        if not mentions_discrimination:
            return {'status': 'N/A', 'message': 'No discrimination/equality provisions', 'legal_source': self.legal_source}

        # Check for all 9 protected characteristics
        characteristics = {
            'age': r'\bage\b',
            'disability': r'disabilit(?:y|ies)',
            'gender_reassignment': r'gender\s+reassignment|trans(?:gender|sexual)?',
            'marriage_civil_partnership': r'(?:marriage|marital\s+status|civil\s+partnership)',
            'pregnancy_maternity': r'(?:pregnancy|maternity)',
            'race': r'\brace\b|ethnic(?:ity)?|national(?:ity)?',
            'religion_belief': r'religion|belief|faith',
            'sex': r'\bsex\b|gender(?!\s+reassignment)',
            'sexual_orientation': r'sexual\s+orientation|(?:lesbian|gay|bisexual)'
        }

        found_characteristics = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in characteristics.items()}
        coverage = sum(found_characteristics.values())

        # Check for types of discrimination
        discrimination_types = {
            'direct': r'direct\s+discriminat',
            'indirect': r'indirect\s+discriminat',
            'harassment': r'harassment',
            'victimisation': r'victimi[sz]ation'
        }

        found_types = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in discrimination_types.items()}

        if coverage == 9 and sum(found_types.values()) >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'All 9 protected characteristics covered with discrimination types',
                'legal_source': self.legal_source,
                'characteristics': list(found_characteristics.keys()),
                'discrimination_types': [k for k, v in found_types.items() if v]
            }

        if coverage >= 7:
            missing_chars = [k for k, v in found_characteristics.items() if not v]
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'{coverage}/9 protected characteristics covered',
                'legal_source': self.legal_source,
                'missing': missing_chars,
                'suggestion': f'Add missing characteristics: {", ".join(missing_chars)}'
            }

        if coverage >= 4:
            missing_chars = [k for k, v in found_characteristics.items() if not v]
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Only {coverage}/9 protected characteristics covered',
                'legal_source': self.legal_source,
                'penalty': 'Unlimited compensation for discrimination claims',
                'missing': missing_chars,
                'suggestion': 'Must cover all 9: age, disability, gender reassignment, marriage/civil partnership, pregnancy/maternity, race, religion/belief, sex, sexual orientation'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate protected characteristics coverage',
            'legal_source': self.legal_source,
            'penalty': 'High discrimination claim risk',
            'suggestion': 'Cover all 9 protected characteristics per Equality Act 2010 s.4'
        }
