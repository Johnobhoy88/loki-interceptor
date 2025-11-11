import re


class AgeDiscriminationGate:
    def __init__(self):
        self.name = "age_discrimination"
        self.severity = "high"
        self.legal_source = "Equality Act 2010 s.13, Employment Equality (Age) Regulations 2006 (repealed but case law relevant)"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['age', 'young', 'older', 'retirement', 'years', 'experience'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        # Check for potentially discriminatory age-related terms
        direct_age_discrimination = [
            r'(?:must|should|prefer).*(?:be\s+)?(?:under|over|between)\s+\d+',
            r'(?:young|youthful|energetic|dynamic)\s+(?:person|candidate|applicant)',
            r'(?:mature|experienced|seasoned).*(?:only|preferred)',
            r'recent\s+graduate(?:s)?.*(?:only|preferred)',
            r'digital\s+native',
            r'(?:long[- ]?established|many\s+years).*(?:required|essential)'
        ]

        has_direct_discrimination = any(re.search(p, text, re.IGNORECASE) for p in direct_age_discrimination)

        # Check for default retirement age (abolished)
        retirement_age_patterns = [
            r'(?:default|compulsory|mandatory)\s+retirement\s+age',
            r'retire(?:ment)?\s+(?:at|age)\s+(?:65|60)',
            r'must\s+retire.*age'
        ]

        has_default_retirement = any(re.search(p, text, re.IGNORECASE) for p in retirement_age_patterns)

        if has_default_retirement:
            # Check for objective justification
            justification_patterns = [
                r'objectively\s+justif(?:y|ied)',
                r'legitimate\s+aim',
                r'proportionate\s+means'
            ]
            has_justification = any(re.search(p, text, re.IGNORECASE) for p in justification_patterns)

            if not has_justification:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Default retirement age without objective justification',
                    'legal_source': 'Equality Act 2010 s.13 (default retirement age abolished 2011)',
                    'penalty': 'Unlimited compensation for age discrimination',
                    'suggestion': 'Cannot impose compulsory retirement age unless objectively justified. Default retirement age abolished in 2011.'
                }

        # Check for LIFO (Last In First Out) - indirectly discriminatory
        lifo_patterns = [
            r'(?:last\s+in|LIFO).*first\s+out',
            r'length\s+of\s+service.*(?:selection|redundancy)',
            r'(?:most\s+)?recent.*(?:joiner|appointment).*(?:first|select)'
        ]

        has_lifo = any(re.search(p, text, re.IGNORECASE) for p in lifo_patterns)

        if has_lifo:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'LIFO redundancy selection criterion detected',
                'legal_source': 'Equality Act 2010 s.19 (indirect age discrimination)',
                'penalty': 'Unlimited compensation for age discrimination',
                'suggestion': 'LIFO (Last In First Out) is indirectly discriminatory against younger workers. Use objective, skills-based criteria.'
            }

        # Check for positive provisions
        positive_elements = {
            'no_age_discrimination': r'(?:not|never).*discriminat.*(?:on\s+grounds\s+of\s+)?age',
            'open_to_all_ages': r'(?:open\s+to|welcome).*(?:all\s+ages|candidates\s+of\s+any\s+age)',
            'benefits_based_on_service': r'(?:benefit|entitlement).*(?:length\s+of\s+service|service[- ]related)',
            'training_all_ages': r'training.*(?:available|provided).*(?:all|regardless\s+of\s+age)',
            'flexible_retirement': r'(?:flexible|phased)\s+retirement',
            'no_upper_age_limit': r'no\s+(?:upper\s+)?age\s+limit'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in positive_elements.items()}
        score = sum(found.values())

        if has_direct_discrimination:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Direct age discrimination language detected',
                'legal_source': self.legal_source,
                'penalty': 'Unlimited compensation for age discrimination',
                'suggestion': 'Remove age-related terms: "young", "recent graduate", "digital native", "many years experience required", age ranges. Focus on skills and competencies.'
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Good age discrimination protections ({score}/6 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic age discrimination protections ({score}/6)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: no age discrimination clause, open to all ages, flexible retirement options'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Limited age discrimination provisions',
            'legal_source': self.legal_source,
            'suggestion': 'Add protections: no age discrimination, no upper age limits, avoid LIFO, service-related benefits must be justified, no default retirement age'
        }
