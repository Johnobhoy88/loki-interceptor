import re


class FairClearNotMisleadingGate:
    def __init__(self):
        self.name = "fair_clear_not_misleading"
        self.severity = "critical"
        self.legal_source = "FCA COBS 4.2 (Fair, Clear and Not Misleading)"

    def _is_relevant(self, text):
        """Check if document is promotional material"""
        text_lower = text.lower()
        promo_keywords = [
            'invest', 'return', 'profit', 'gain', 'growth', 'performance',
            'benefit', 'advantage', 'opportunity', 'offer', 'special',
            'guaranteed', 'secure', 'safe', 'best', 'exclusive'
        ]
        return any(kw in text_lower for kw in promo_keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not promotional or does not make financial claims',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for unsubstantiated superlatives
        superlatives = [
            r'\b(?:best|highest|top|leading|number\s+one|#1|unbeatable|unsurpassed|unmatched|superior|premier|ultimate|perfect)\b',
            r'\b(?:guaranteed|promise|ensure|certain|definite|assured)\b.*(?:return|profit|gain|yield)',
            r'\bguaranteed\b.*\d+%',
            r'\b(?:risk-free|no\s+risk|zero\s+risk|without\s+risk)\b(?!\s+(?:deposit|up\s+to|for\s+the\s+first))',
            r'\b(?:safe|secure)\b.*(?:investment|return|profit)',
            r'\b(?:always|never\s+lose|cannot\s+lose|can\'t\s+lose|zero\s+chance\s+of\s+loss)\b'
        ]

        violations = []
        for pattern in superlatives:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                violations.append('unsubstantiated_claims')
                for m in matches:
                    spans.append({
                        'type': 'unsubstantiated_superlative',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Check for emphasis on benefits without risks
        benefit_patterns = [
            r'(?:high|significant|attractive|exceptional|outstanding)\s+(?:return|yield|profit|gain|growth|performance)',
            r'\d+%\s+(?:return|yield|gain|profit)',
            r'(?:up\s+to|as\s+much\s+as)\s+\d+%'
        ]

        has_benefits = False
        for pattern in benefit_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_benefits = True
                for m in matches:
                    spans.append({
                        'type': 'benefit_claim',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Check for risk warnings
        risk_patterns = [
            r'risk',
            r'may\s+(?:lose|fall|decrease|go\s+down)',
            r'(?:value|capital)\s+(?:at\s+)?risk',
            r'not\s+guaranteed',
            r'past\s+performance',
            r'no\s+guarantee'
        ]

        has_risks = any(re.search(pattern, text, re.IGNORECASE) for pattern in risk_patterns)

        # Check for misleading comparisons
        misleading_comparisons = [
            r'(?:better|more|higher)\s+than\s+(?:bank|savings|deposit)',
            r'outperform(?:s|ed|ing)?\s+(?:the\s+)?market',
            r'beat(?:s|ing)?\s+(?:the\s+)?(?:market|index|average)'
        ]

        has_misleading_comparison = False
        for pattern in misleading_comparisons:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_misleading_comparison = True
                violations.append('misleading_comparison')
                for m in matches:
                    spans.append({
                        'type': 'misleading_comparison',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Check for hidden disclaimers (small text indicators)
        hidden_disclaimer_patterns = [
            r'(?:\*{1,3}|†|‡)(?:.*?)(?:terms|conditions|apply|details)',
            r'see\s+(?:footnote|below|terms|conditions|website)'
        ]

        has_hidden_disclaimers = False
        for pattern in hidden_disclaimer_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_hidden_disclaimers = True
                for m in matches:
                    spans.append({
                        'type': 'potential_hidden_disclaimer',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Determine status
        critical_issues = []
        warnings = []

        if 'unsubstantiated_claims' in violations or 'misleading_comparison' in violations:
            critical_issues.append('Unsubstantiated or misleading claims detected')

        if has_benefits and not has_risks:
            critical_issues.append('Benefits emphasized without balanced risk disclosure')

        if has_hidden_disclaimers:
            warnings.append('Potential hidden disclaimers - ensure material information is prominent')

        # Critical failure
        if critical_issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Financial promotion fails fair, clear, not misleading test',
                'legal_source': self.legal_source,
                'suggestion': 'Remove unsubstantiated superlatives. Balance benefits with equally prominent risk warnings. Avoid misleading comparisons. Support all claims with evidence.',
                'spans': spans,
                'details': critical_issues + warnings
            }

        # Warning
        if warnings:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Potential COBS 4.2 issues detected',
                'legal_source': self.legal_source,
                'suggestion': 'Ensure all material information is prominent and not relegated to footnotes.',
                'spans': spans,
                'details': warnings
            }

        # Pass
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No obvious fair/clear/misleading issues detected',
            'legal_source': self.legal_source,
            'spans': spans
        }
