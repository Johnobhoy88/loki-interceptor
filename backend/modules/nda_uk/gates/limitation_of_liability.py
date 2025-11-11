import re


class LimitationOfLiabilityGate:
    def __init__(self):
        self.name = "limitation_of_liability"
        self.severity = "medium"
        self.legal_source = "Unfair Contract Terms Act 1977, Consumer Rights Act 2015"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for limitation of liability clause
        limitation_patterns = [
            r'limit(?:ation)?.*(?:of\s+)?liability',
            r'liability.*limited\s+to',
            r'(?:exclude|disclaim).*liability',
            r'maximum\s+liability'
        ]

        has_limitation = any(re.search(p, text, re.IGNORECASE) for p in limitation_patterns)

        if not has_limitation:
            return {
                'status': 'N/A',
                'message': 'No limitation of liability provisions',
                'legal_source': self.legal_source
            }

        # Check for prohibited exclusions under UCTA 1977
        prohibited_exclusions = {
            'death_personal_injury': r'(?:exclude|limit).*(?:death|personal\s+injury)',
            'fraud': r'(?:exclude|limit).*fraud',
            'all_liability': r'(?:exclude|disclaim).*(?:all|any)\s+liability'
        }

        violations = []
        for violation_type, pattern in prohibited_exclusions.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Check if there's a carve-out
                carveout_patterns = [
                    r'except.*(?:death|personal\s+injury|fraud)',
                    r'(?:save|excluding).*(?:death|fraud)',
                    r'nothing.*(?:exclude|limit).*(?:fraud|death)'
                ]
                has_carveout = any(re.search(p, text, re.IGNORECASE) for p in carveout_patterns)
                if not has_carveout:
                    violations.append(violation_type)

        if violations:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Prohibited liability exclusions detected',
                'legal_source': 'Unfair Contract Terms Act 1977 s.2',
                'violations': violations,
                'penalty': 'Void and unenforceable',
                'suggestion': 'Cannot exclude liability for death/personal injury or fraud. Add carve-out.'
            }

        # Check for indirect/consequential damages exclusion
        consequential_patterns = [
            r'(?:exclude|not\s+liable).*(?:indirect|consequential|special|punitive).*(?:loss|damage)',
            r'no\s+liability.*(?:loss\s+of\s+(?:profit|revenue|data|goodwill))'
        ]

        excludes_consequential = any(re.search(p, text, re.IGNORECASE) for p in consequential_patterns)

        # Check for cap on liability
        cap_patterns = [
            r'(?:limited|capped)\s+to.*(?:£|\$|GBP|amount)',
            r'(?:not\s+exceed|maximum).*(?:£|\$|GBP)',
            r'aggregate\s+liability.*(?:£|\$|amount)'
        ]

        has_cap = any(re.search(p, text, re.IGNORECASE) for p in cap_patterns)

        # Check if cap is reasonable (e.g., linked to fees paid, insurance)
        reasonable_cap_patterns = [
            r'(?:fees?|amount)\s+paid',
            r'insurance\s+(?:coverage|limit)',
            r'\d+\s+(?:times|x).*fee',
            r'12\s+months'
        ]

        has_reasonable_cap = any(re.search(p, text, re.IGNORECASE) for p in reasonable_cap_patterns)

        # Check for carve-outs that cannot be limited
        proper_carveouts = [
            r'except.*fraud',
            r'(?:save|excluding).*(?:fraud|fraudulent)',
            r'nothing.*limit.*(?:fraud|wilful)',
            r'provided\s+that.*nothing.*(?:fraud|death)'
        ]

        has_proper_carveouts = any(re.search(p, text, re.IGNORECASE) for p in proper_carveouts)

        if has_proper_carveouts and has_cap and has_reasonable_cap:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Reasonable limitation of liability with proper carve-outs',
                'legal_source': self.legal_source,
                'excludes_consequential': excludes_consequential
            }

        if has_proper_carveouts:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Limitation of liability with fraud/death carve-outs',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding cap on liability (e.g., linked to fees paid or insurance)'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Limitation of liability missing mandatory carve-outs',
            'legal_source': self.legal_source,
            'suggestion': 'Add: "Nothing in this Agreement limits liability for fraud, fraudulent misrepresentation, or death/personal injury caused by negligence"'
        }
