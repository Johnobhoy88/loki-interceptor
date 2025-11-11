import re


class FurtherAssuranceGate:
    def __init__(self):
        self.name = "further_assurance"
        self.severity = "low"
        self.legal_source = "Contract Law"

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

        # Check for further assurance clause
        further_assurance_patterns = [
            r'further\s+assurance',
            r'execute.*(?:document|instrument).*(?:necessary|required|reasonably)',
            r'take.*(?:action|step).*(?:necessary|required|give\s+effect)',
            r'cooperat(?:e|ion).*(?:implement|effect|perform)'
        ]

        has_further_assurance = any(re.search(p, text, re.IGNORECASE) for p in further_assurance_patterns)

        if not has_further_assurance:
            return {
                'status': 'N/A',
                'message': 'No further assurance provision',
                'legal_source': self.legal_source,
                'note': 'Further assurance clause useful to ensure parties cooperate in implementation'
            }

        # Check for specific obligations
        obligations = {
            'execute_documents': r'execute.*(?:document|instrument)',
            'take_actions': r'take.*(?:action|step)',
            'provide_information': r'provide.*information',
            'cooperate': r'cooperat(?:e|ion)',
            'reasonably_necessary': r'reasonably\s+(?:necessary|required)',
            'give_effect': r'give.*effect|implement'
        }

        found_obligations = {}
        for obligation_type, pattern in obligations.items():
            found_obligations[obligation_type] = bool(re.search(pattern, text, re.IGNORECASE))

        # Check for cost allocation
        cost_patterns = [
            r'(?:at|expense\s+of|cost\s+of)',
            r'bear.*(?:own|their)\s+cost',
            r'without.*(?:cost|charge|expense)'
        ]

        addresses_cost = any(re.search(p, text, re.IGNORECASE) for p in cost_patterns)

        # Check for timeframe
        timeframe_patterns = [
            r'(?:promptly|immediately|without\s+delay)',
            r'within\s+\d+\s+(?:day|business\s+day)',
            r'as\s+soon\s+as\s+(?:reasonably\s+)?(?:practicable|possible)'
        ]

        has_timeframe = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)

        obligation_count = sum(found_obligations.values())

        if obligation_count >= 4 and has_timeframe:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive further assurance clause ({obligation_count} obligations)',
                'legal_source': self.legal_source,
                'obligations': [k for k, v in found_obligations.items() if v]
            }

        if obligation_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Further assurance provision included',
                'legal_source': self.legal_source,
                'obligations': [k for k, v in found_obligations.items() if v],
                'suggestion': 'Consider adding timeframe (e.g., promptly, reasonably practicable)'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Basic further assurance provision',
            'legal_source': self.legal_source,
            'suggestion': 'Consider specifying: execute documents, take actions, cooperate, timeframe'
        }
