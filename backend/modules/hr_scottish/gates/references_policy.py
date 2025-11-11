import re


class ReferencesPolicyGate:
    def __init__(self):
        self.name = "references_policy"
        self.severity = "medium"
        self.legal_source = "Defamation Act 2013, Spring v Guardian Assurance [1995], Contract Law"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['reference', 'testimonial', 'recommendation', 'former employee'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        reference_patterns = [
            r'reference(?:s)?',
            r'testimonial',
            r'(?:provide|give|supply).*(?:reference|recommendation)'
        ]

        has_reference_policy = any(re.search(p, text, re.IGNORECASE) for p in reference_patterns)

        if not has_reference_policy:
            return {'status': 'N/A', 'message': 'No reference policy', 'legal_source': self.legal_source}

        elements = {
            'written_request': r'(?:in\s+)?writing|written\s+request',
            'authorized_persons': r'(?:authorized|designated|HR|manager).*(?:only|sole)',
            'factual_only': r'factual|confirm.*(?:employment|dates|position)',
            'no_opinion': r'(?:not|no).*(?:opinion|subjective|personal\s+view)',
            'accuracy': r'(?:accurate|true|correct)',
            'reasonable_care': r'reasonable\s+care|due\s+(?:care|diligence)',
            'duty_of_care': r'duty\s+of\s+care|owe.*duty',
            'data_protection': r'(?:GDPR|data\s+protection|subject\s+access)',
            'qualified_privilege': r'qualified\s+privilege',
            'malice_warning': r'malice|bad\s+faith',
            'consent': r'consent.*(?:employee|subject)',
            'retain_copy': r'retain|keep.*(?:copy|record)',
            'standardized': r'standard(?:i[sz]ed)?.*(?:format|template)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for problematic practices
        problematic_practices = [
            r'(?:will\s+not|refuse\s+to|no).*(?:provide|give).*reference',
            r'(?:blacklist|negative\s+reference).*(?:all|certain)',
            r'opinion.*(?:performance|ability|character)'
        ]

        has_problematic = any(re.search(p, text, re.IGNORECASE) for p in problematic_practices)

        if has_problematic:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': 'Potentially problematic reference practices',
                'legal_source': 'Spring v Guardian Assurance [1995] - duty of care in references',
                'suggestion': 'Refusing all references may breach duty of care. Provide factual references. Negative opinions must be: (1) accurate, (2) based on reasonable investigation, (3) not malicious.'
            }

        if score >= 8:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive reference policy ({score}/13 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 5:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Adequate reference policy ({score}/13)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: qualified privilege, duty of care, data protection compliance, consent requirements'
            }

        if score >= 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Reference policy incomplete ({score}/13)',
                'legal_source': self.legal_source,
                'suggestion': 'Add: authorized persons only, factual information, reasonable care, accuracy, data protection, consent, standardized format'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Reference policy lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Implement policy: (1) authorized persons, (2) factual information only, (3) accuracy and reasonable care, (4) GDPR compliance, (5) obtain consent, (6) qualified privilege protection'
        }
