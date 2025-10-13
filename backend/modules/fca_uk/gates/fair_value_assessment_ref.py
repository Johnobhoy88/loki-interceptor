import re


class FairValueAssessmentRefGate:
    def __init__(self):
        self.name = "fair_value_assessment_ref"
        self.severity = "medium"
        self.legal_source = "FCA PROD 4.2.17 (Fair Value Assessment Reviews)"

    def _is_relevant(self, text):
        """Check if document discusses products or value assessments"""
        text_lower = text.lower()
        keywords = [
            'product', 'value', 'assessment', 'review', 'price',
            'fee', 'charge', 'cost', 'governance', 'monitoring'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss pricing or product value',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check if product pricing/value is mentioned
        has_pricing = any(re.search(pattern, text, re.IGNORECASE) for pattern in [
            r'price|fee|charge|cost|premium',
            r'value\s+for\s+money',
            r'fair\s+value'
        ])

        if not has_pricing:
            return {'status': 'N/A'}

        # Check for value assessment references
        assessment_patterns = [
            r'value\s+assessment',
            r'fair\s+value\s+assessment',
            r'assess(?:ing|ment)?\s+(?:the\s+)?(?:fair\s+)?value',
            r'value\s+(?:review|evaluation|analysis)',
            r'price\s+(?:review|assessment)'
        ]

        has_assessment = False
        for pattern in assessment_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_assessment = True
                for m in matches:
                    spans.append({
                        'type': 'value_assessment',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for periodic/ongoing review references
        periodic_patterns = [
            r'(?:periodic|regular|ongoing|annual|yearly|quarterly)\s+(?:review|assessment|evaluation)',
            r'(?:review|assess|monitor)(?:ed|ing)?\s+(?:at\s+least\s+)?(?:annual|yearly|periodic)',
            r'(?:continuous|ongoing)\s+(?:monitoring|assessment)',
            r'(?:every|each)\s+(?:year|quarter|6\s+months?)',
            r're-?assess'
        ]

        has_periodic = False
        for pattern in periodic_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if in context of value/price/product
                for m in matches:
                    context_start = max(0, m.start() - 150)
                    context_end = min(len(text), m.end() + 150)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['value', 'price', 'product', 'fee', 'charge', 'fair']):
                        has_periodic = True
                        spans.append({
                            'type': 'periodic_assessment',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for governance/oversight references
        governance_patterns = [
            r'(?:product\s+)?governance',
            r'oversight\s+(?:committee|board|function)',
            r'product\s+(?:review|committee|oversight)',
            r'(?:board|committee)\s+(?:review|approval|oversight)'
        ]

        has_governance = False
        for pattern in governance_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_governance = True
                for m in matches:
                    spans.append({
                        'type': 'governance_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for specific value assessment factors
        factor_patterns = [
            r'(?:cost|expense|fee)s?\s+(?:vs|versus|compared\s+to|relative\s+to)\s+(?:benefit|value)',
            r'total\s+cost\s+of\s+ownership',
            r'(?:benchmark|compare|comparison)\s+(?:with|to|against)',
            r'market\s+(?:rate|price|standard|norm)',
            r'price\s+(?:competitive|reasonable|justified)'
        ]

        has_factors = False
        for pattern in factor_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_factors = True
                for m in matches:
                    spans.append({
                        'type': 'value_factor',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        assessment_components = []
        if has_assessment:
            assessment_components.append('value assessment mentioned')
        if has_periodic:
            assessment_components.append('periodic review')
        if has_governance:
            assessment_components.append('governance oversight')
        if has_factors:
            assessment_components.append('assessment factors')

        # Warning: Product with pricing but no value assessment reference
        if not has_assessment and not has_periodic:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Product pricing mentioned but no value assessment process referenced',
                'legal_source': self.legal_source,
                'suggestion': 'PROD 4.2.17 requires manufacturers to assess whether products provide fair value and review this at least annually.',
                'spans': spans
            }

        # Warning: Assessment mentioned but no periodic review
        if has_assessment and not has_periodic:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Value assessment mentioned but periodic review not specified',
                'legal_source': self.legal_source,
                'suggestion': 'State that fair value assessments are reviewed at least annually or when material changes occur.',
                'spans': spans
            }

        # Pass: Good coverage
        if len(assessment_components) >= 2:
            details = []
            for component in assessment_components:
                details.append(component)
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Fair value assessment process referenced ({len(assessment_components)} elements)',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Marginal pass
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Value assessment referenced',
            'legal_source': self.legal_source,
            'spans': spans
        }
