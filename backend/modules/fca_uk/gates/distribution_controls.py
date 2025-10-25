import re


class DistributionControlsGate:
    def __init__(self):
        self.name = "distribution_controls"
        self.severity = "medium"
        self.legal_source = "FCA PROD 4 (Product Governance - Distribution)"

    def _is_relevant(self, text):
        """Check if document mentions distribution or intermediaries"""
        text_lower = text.lower()
        keywords = [
            'distribute', 'distribution', 'intermediary', 'intermediaries',
            'adviser', 'advisor', 'broker', 'agent', 'third party',
            'partner', 'seller', 'channel'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe intermediary or third-party distribution arrangements',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for distribution channel mentions
        channel_patterns = [
            r'\b(?:intermediary|intermediaries|adviser|advisor|broker|agent)\b',
            r'third[\s-]party\s+(?:seller|distributor|provider)',
            r'distribution\s+(?:channel|partner|network)',
            r'(?:through|via)\s+(?:intermediaries|advisers|brokers|agents)',
            r'appointed\s+representative'
        ]

        has_intermediaries = False
        for pattern in channel_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_intermediaries = True
                for m in matches:
                    spans.append({
                        'type': 'distribution_channel',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        if not has_intermediaries:
            return {'status': 'N/A'}

        # Check for distribution controls
        control_patterns = {
            'distribution_agreement': [
                r'distribution\s+agreement',
                r'terms\s+of\s+(?:appointment|distribution)',
                r'contract\s+(?:with|for)\s+(?:intermediar|distribut)',
                r'agreement\s+(?:govern|set\s+out|specify)'
            ],
            'training_competence': [
                r'(?:training|competence|qualification)\s+(?:requirement|standard)',
                r'(?:trained|qualified|competent)\s+(?:to|in)',
                r'appropriate\s+(?:training|qualification|knowledge)',
                r'(?:staff|adviser|intermediary)\s+(?:training|competence)'
            ],
            'target_market_alignment': [
                r'(?:align|consistent|compatible)\s+(?:with\s+)?target\s+market',
                r'target\s+market\s+(?:information|data|details)',
                r'only\s+(?:sell|distribute|offer)\s+to\s+target\s+market',
                r'ensure.*target\s+market'
            ],
            'monitoring': [
                r'monitor(?:ing)?\s+(?:distribution|sales|intermediar)',
                r'oversee|oversight',
                r'review\s+(?:distribution|sales)',
                r'(?:regular|ongoing|periodic)\s+(?:review|assessment)',
                r'management\s+information|mi\s+data'
            ],
            'complaints_feedback': [
                r'(?:complaint|feedback)\s+(?:from|about)\s+(?:customer|distribution)',
                r'customer\s+outcome',
                r'(?:report|notify)\s+(?:issue|complaint|concern)',
                r'escalate|escalation'
            ]
        }

        controls_present = {}
        for control_type, patterns in control_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if control_type not in controls_present:
                        controls_present[control_type] = []
                    for m in matches:
                        controls_present[control_type].append(m.group())
                        spans.append({
                            'type': f'control_{control_type}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for absence of controls (negative indicators)
        negative_patterns = [
            r'no\s+(?:control|oversight|monitoring)',
            r'(?:not|un)regulated',
            r'(?:independent|outside)\s+(?:our\s+)?control',
            r'no\s+responsibility\s+for',
            r'no\s+(?:knowledge|suitability)\s+(?:checks|hurdles|requirements)',
            r'automatically\s+accept',
            r'everyone\s+(?:qualifies|approved)'
        ]

        has_negative_indicators = False
        for pattern in negative_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_negative_indicators = True
                for m in matches:
                    spans.append({
                        'type': 'control_absence',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Determine status
        control_count = len(controls_present)

        # Fail: Intermediaries used but no controls or negative indicators
        if has_negative_indicators:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Distribution via intermediaries without adequate controls',
                'legal_source': self.legal_source,
                'suggestion': 'PROD 4 requires manufacturers to establish distribution arrangements. Cannot disclaim responsibility for distribution outcomes.',
                'spans': spans
            }

        # Warning: Intermediaries but minimal controls
        if control_count < 2:
            details = []
            details.append(f'Controls present: {", ".join(list(controls_present.keys())) if controls_present else "none"}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Distribution controls may be insufficient ({control_count} types detected)',
                'legal_source': self.legal_source,
                'suggestion': 'Implement distribution controls: (1) agreements with intermediaries, (2) training/competence requirements, (3) target market alignment, (4) ongoing monitoring, (5) complaint/feedback loops.',
                'spans': spans,
                'details': details
            }

        # Pass: Good controls
        if control_count >= 2:
            details = []
            details.append(f'Controls present: {", ".join(controls_present.keys())}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Distribution controls in place ({control_count} types: {", ".join(controls_present.keys())})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Some distribution controls evident',
            'legal_source': self.legal_source,
            'spans': spans
        }
