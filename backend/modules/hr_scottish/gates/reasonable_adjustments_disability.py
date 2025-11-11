import re


class ReasonableAdjustmentsDisabilityGate:
    def __init__(self):
        self.name = "reasonable_adjustments_disability"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010 ss.20-22, 39, Employment Code of Practice"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['disability', 'disabl', 'adjustment', 'accommodation', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        adjustment_patterns = [
            r'reasonable\s+adjustment',
            r'disabilit(?:y|ies)',
            r'accommodate.*disabil'
        ]

        has_adjustment_policy = any(re.search(p, text, re.IGNORECASE) for p in adjustment_patterns)

        if not has_adjustment_policy:
            return {'status': 'N/A', 'message': 'No reasonable adjustments policy', 'legal_source': self.legal_source}

        elements = {
            'anticipatory_duty': r'anticipatory|proactive|advance',
            'individual_assessment': r'individual.*(?:assessment|basis|circumstances)',
            'consultation': r'consult.*(?:employee|individual|person)',
            'examples': r'(?:example|such\s+as|including|may\s+include)',
            'physical_features': r'(?:physical|premises|building|access)',
            'auxiliary_aids': r'(?:auxiliary|equipment|aid|assistive|software)',
            'working_arrangements': r'(?:working\s+(?:hours|pattern|arrangement)|flexible)',
            'recruitment': r'recruitment|interview|application',
            'absence_management': r'absence.*(?:relate|due\s+to).*disabilit',
            'training': r'training.*(?:awareness|disabilit)',
            'cost_consideration': r'(?:cost|expense).*(?:reasonable|disproportionate)',
            'no_knowledge_defence': r'(?:did\s+not\s+know|unaware|knowledge).*disabilit'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found_elements.values())

        # Check for prohibited practices
        prohibited_patterns = [
            r'(?:all|any)\s+(?:employee|applicant).*(?:must|required).*(?:medic|health|fitness)',
            r'pre[- ]employment.*(?:health|medical).*(?:question|screen)'
        ]

        has_prohibited = any(re.search(p, text, re.IGNORECASE) for p in prohibited_patterns)

        if has_prohibited:
            # Check if it's for reasonable adjustments purpose
            permitted_purpose_patterns = [
                r'(?:determine|establish).*(?:reasonable\s+adjustment|support\s+required)',
                r'(?:only|solely).*(?:adjustment|support|accommodation)',
                r'not.*(?:assess|determine).*(?:suitability|fitness\s+to\s+work)'
            ]
            has_permitted_purpose = any(re.search(p, text, re.IGNORECASE) for p in permitted_purpose_patterns)

            if not has_permitted_purpose:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Prohibited pre-employment health questions detected',
                    'legal_source': 'Equality Act 2010 s.60',
                    'penalty': 'Unlimited compensation for disability discrimination',
                    'suggestion': 'Cannot ask health questions before job offer except: (1) determine reasonable adjustments, (2) monitoring, (3) positive action. See s.60 Equality Act'
                }

        if score >= 8:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive reasonable adjustments policy ({score}/12 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v]
            }

        if score >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Reasonable adjustments policy incomplete ({score}/12)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found_elements.items() if not v][:5],
                'suggestion': 'Add: individual assessment, consultation, examples (physical features, auxiliary aids, working arrangements), anticipatory duty'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate reasonable adjustments policy',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited compensation for disability discrimination',
            'suggestion': 'Must provide reasonable adjustments per Equality Act 2010 s.20: (1) changing provisions, criteria, practices, (2) altering physical features, (3) providing auxiliary aids. Duty is anticipatory and individual.'
        }
