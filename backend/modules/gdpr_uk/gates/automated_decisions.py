import re


class AutomatedDecisionsGate:
    def __init__(self):
        self.name = "automated_decisions"
        self.severity = "critical"
        self.legal_source = "GDPR Article 22"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        # Broaden to catch AI-made decisions even without "AI" keyword
        return any(kw in text_lower for kw in [
            'automated', 'algorithm', 'ai', 'profiling', 'machine learning',
            'automatically', 'system', 'rejected', 'approved', 'decision'
        ])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not involve automated decision-making or profiling',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check for automated/system decision keywords
        automated_decision_indicators = [
            r'automatically\s+(?:rejected|approved|decided)',
            r'(?:our|the)\s+(?:ai|system|algorithm)\s+(?:rejected|approved|decided)',
            r'decision\s+(?:is|was)\s+(?:final|automatic)',
            r'automated\s+decision',
            r'no\s+human\s+(?:override|review|intervention)',
            r'no\s+appeal'
        ]

        has_automated_decision = any(re.search(p, text, re.IGNORECASE) for p in automated_decision_indicators)

        # Check for right to human review/intervention
        human_review_patterns = [
            r'right.*human\s+review',
            r'human\s+(?:intervention|review)',
            r'contest.*decision',
            r'challenge.*decision',
            r'appeal'
        ]

        has_human_review = any(re.search(p, text, re.IGNORECASE) for p in human_review_patterns)

        anti_review_patterns = [
            r'no\s+human\s+(?:override|review|intervention)',
            r'no\s+appeal',
            r'decision\s+is\s+final'
        ]

        if any(re.search(p, text, re.IGNORECASE) for p in anti_review_patterns):
            has_human_review = False
            has_automated_decision = True

        # If automated decision WITHOUT human review rights = GDPR violation
        if has_automated_decision and not has_human_review:
            spans = []
            for p in automated_decision_indicators:
                for m in re.finditer(p, text, re.IGNORECASE):
                    spans.append({
                        'type': 'automated_decision_no_review',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })

            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Automated decision without right to human review violates GDPR Article 22',
                'legal_source': self.legal_source,
                'spans': spans,
                'suggestion': 'Add: "You have the right to request human review of this decision, obtain an explanation, and challenge it."'
            }

        risk_children = bool(re.search(r'\bchild|teen|under\s+1[36-8]|parental\s+consent', text_lower))
        risk_special = bool(re.search(r'special\s+category|health\s+data|biometric|genetic|lifestyle|medical', text_lower))
        risk_international = bool(re.search(r'singapore|dubai|united\s+states|uae|outside\s+the\s+uk|overseas|international\s+transfer', text_lower))
        risk_automated = has_automated_decision

        high_risk_factors = sum([risk_children, risk_special, risk_international, risk_automated])
        has_dpia_reference = bool(re.search(r'data\s+protection\s+impact\s+assessment|dpia', text_lower))

        if high_risk_factors >= 2 and not has_dpia_reference:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'High-risk processing identified but no Data Protection Impact Assessment reference',
                'legal_source': self.legal_source,
                'suggestion': 'Conduct and reference a Data Protection Impact Assessment (DPIA) covering automated decisions, children, special category data, and international transfers.',
            }

        # Check if automated decision-making is disclosed with safeguards
        if has_automated_decision and has_human_review:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Automated decision-making disclosed with safeguards', 'spans': []}

        # General case: automation mentioned without clear decision context
        indicator_terms = ['ai', 'algorithm', 'automated', 'profiling', 'machine learning']
        spans = []
        for term in indicator_terms:
            for m in re.finditer(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                spans.append({
                    'type': 'automation_indicator',
                    'start': m.start(),
                    'end': m.end(),
                    'text': m.group(),
                    'severity': 'medium'
                })

        if spans:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Automation mentioned - ensure Article 22 safeguards if used for decisions',
                'legal_source': self.legal_source,
                'spans': spans,
                'suggestion': 'If using automated decision-making, disclose it and provide right to human review.'
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'No automated decision-making detected'}
