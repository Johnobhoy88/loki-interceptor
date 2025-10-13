import re


class ComprehensionAidsGate:
    def __init__(self):
        self.name = "comprehension_aids"
        self.severity = "medium"
        self.legal_source = "FCA PRIN 2A.5 (Consumer Understanding Outcome)"

    def _is_relevant(self, text):
        """Check if document contains complex information"""
        text_lower = text.lower()
        # Look for complex financial terms or lengthy documents
        complex_terms = [
            'derivative', 'leverage', 'portfolio', 'bond', 'equity',
            'maturity', 'yield', 'premium', 'liability', 'covenant',
            'subordinated', 'counterparty', 'collateral'
        ]
        return any(term in text_lower for term in complex_terms) or len(text) > 1000

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain complex financial information requiring comprehension aids',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check for comprehension aids
        aids = {
            'plain_language': [
                r'in\s+simple\s+terms',
                r'this\s+means',
                r'for\s+example',
                r'to\s+put\s+it\s+another\s+way',
                r'in\s+other\s+words'
            ],
            'key_risks': [
                r'key\s+risks?',
                r'important\s+(?:to\s+)?(?:note|understand|know)',
                r'main\s+risks?',
                r'(?:please\s+)?(?:be\s+)?aware',
                r'warning'
            ],
            'next_steps': [
                r'(?:next|following)\s+steps?',
                r'what\s+(?:happens|you\s+need\s+to\s+do)\s+next',
                r'how\s+to\s+(?:proceed|apply|continue)',
                r'to\s+(?:move\s+forward|progress)'
            ],
            'summaries': [
                r'(?:in\s+)?summary',
                r'key\s+(?:points?|information)',
                r'at\s+a\s+glance',
                r'quick\s+overview',
                r'highlights?'
            ]
        }

        found_aids = []
        spans = []

        for aid_type, patterns in aids.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if aid_type not in found_aids:
                        found_aids.append(aid_type)
                    for m in matches:
                        spans.append({
                            'type': f'aid_{aid_type}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for jargon without explanation
        jargon_pattern = r'\b(?:derivative|amortisation|subordinated|covenant|counterparty|collateral|basis\s+points?|bps)\b'
        jargon_matches = list(re.finditer(jargon_pattern, text, re.IGNORECASE))

        unexplained_jargon = []
        for m in jargon_matches:
            jargon_term = m.group()
            # Check if there's an explanation nearby (within 200 chars)
            context_start = max(0, m.start() - 100)
            context_end = min(len(text), m.end() + 100)
            context = text[context_start:context_end].lower()

            has_explanation = any(indicator in context for indicator in [
                'means', 'refers to', 'is when', 'this is', 'defined as'
            ])

            if not has_explanation:
                unexplained_jargon.append(jargon_term)
                spans.append({
                    'type': 'unexplained_jargon',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'medium'
                })

        # Check for overly long sentences (potential comprehension barrier)
        sentences = re.split(r'[.!?]+', text)
        long_sentences = 0
        for sentence in sentences:
            words = len(sentence.split())
            if words > 40:
                long_sentences += 1

        # Determine status
        issues = []

        if unexplained_jargon:
            issues.append(f'{len(unexplained_jargon)} technical term(s) without plain English explanation')

        if long_sentences > 3:
            issues.append(f'{long_sentences} overly long sentences (>40 words)')

        if len(found_aids) == 0 and (unexplained_jargon or long_sentences > 0):
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'FAIL',
                'severity': 'medium',
                'message': 'Complex content without comprehension aids',
                'legal_source': self.legal_source,
                'suggestion': 'Add plain English explanations, key risk summaries, examples, or next steps to support consumer understanding.',
                'spans': spans,
                'details': details
            }

        if issues:
            details = []
            for issue in issues:
                details.append(issue)
            details.append(f'Aids found: {", ".join(found_aids)}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Potential comprehension barriers detected',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding more plain language explanations and simplifying complex sentences.',
                'spans': spans,
                'details': details
            }

        if len(found_aids) >= 2:
            details = []
            details.append(f'Aids found: {", ".join(found_aids)}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Good comprehension aids present ({len(found_aids)} types)',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No significant comprehension barriers detected',
            'legal_source': self.legal_source,
            'spans': spans
        }
