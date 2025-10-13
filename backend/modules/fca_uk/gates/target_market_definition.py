import re


class TargetMarketDefinitionGate:
    def __init__(self):
        self.name = "target_market_definition"
        self.severity = "high"
        self.legal_source = "FCA PROD 1.4 & PROD 3 (Product Governance - Target Market)"

    def _is_relevant(self, text):
        """Check if document discusses products or product design"""
        text_lower = text.lower()
        keywords = [
            'product', 'service', 'designed', 'target', 'customer',
            'suitable', 'appropriate', 'market', 'distribution'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss product design or target markets',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for target market definition
        target_market_patterns = [
            r'target\s+market',
            r'target\s+customer',
            r'designed\s+for',
            r'intended\s+for',
            r'suitable\s+for',
            r'appropriate\s+for',
            r'this\s+product\s+(?:is\s+)?(?:for|aimed\s+at)'
        ]

        has_target_market = False
        for pattern in target_market_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_target_market = True
                for m in matches:
                    spans.append({
                        'type': 'target_market_mention',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for specific target market criteria (PROD requirements)
        criteria_categories = {
            'customer_type': [
                r'(?:retail|professional|institutional|eligible\s+counterparty)\s+(?:customer|client|investor)',
                r'(?:high\s+net\s+worth|mass\s+market|mainstream)',
                r'(?:sophisticated|experienced|first-time)\s+investor'
            ],
            'knowledge_experience': [
                r'(?:knowledge|experience|understanding)\s+of',
                r'(?:familiar|experience)\s+with',
                r'(?:basic|advanced|expert)\s+(?:knowledge|understanding)',
                r'(?:no|limited|extensive)\s+(?:experience|knowledge)'
            ],
            'financial_situation': [
                r'(?:income|wealth|assets)\s+(?:of|above|over|between)',
                r'(?:afford|can\s+bear)\s+(?:loss|risk)',
                r'financial\s+(?:capacity|situation|circumstances)',
                r'(?:minimum|maximum)\s+investment'
            ],
            'risk_profile': [
                r'(?:risk\s+)?(?:appetite|tolerance|profile)',
                r'(?:low|medium|high|aggressive|conservative)\s+risk',
                r'(?:willing|able)\s+to\s+(?:accept|bear)\s+(?:risk|loss)',
                r'(?:capital|income)\s+(?:preservation|growth)'
            ],
            'objectives': [
                r'(?:investment|financial)\s+objective',
                r'(?:seeking|looking\s+for|need|require)',
                r'(?:retirement|income|growth|protection)\s+(?:planning|need)',
                r'time\s+horizon'
            ],
            'demographic': [
                r'age(?:d)?\s+(?:between\s+)?\d+',
                r'\d+\s+(?:year|yr)s?\s+old',
                r'(?:retired|retiring|approaching\s+retirement)',
                r'(?:working|employed|self-employed)'
            ]
        }

        defined_criteria = {}
        for category, patterns in criteria_categories.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if category not in defined_criteria:
                        defined_criteria[category] = []
                    for m in matches:
                        defined_criteria[category].append(m.group())
                        spans.append({
                            'type': f'criteria_{category}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for generic/vague targeting (red flag)
        generic_patterns = [
            r'(?:all|everyone|anyone|any)\s+(?:customer|investor|client)',
            r'suitable\s+for\s+(?:everyone|all|anyone)',
            r'no\s+(?:restriction|requirement|minimum)',
            r'broadly\s+suitable',
            r'wide\s+(?:range|appeal)'
        ]

        is_generic = False
        for pattern in generic_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                is_generic = True
                for m in matches:
                    spans.append({
                        'type': 'generic_target_market',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for negative target market (who it's NOT for)
        negative_target_patterns = [
            r'not\s+(?:suitable|appropriate|designed|intended)\s+for',
            r'should\s+not\s+(?:invest|apply|use)',
            r'(?:exclude|excluding|excluded)',
            r'outside\s+(?:the\s+)?target\s+market'
        ]

        has_negative_target = False
        for pattern in negative_target_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_negative_target = True
                for m in matches:
                    spans.append({
                        'type': 'negative_target_market',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        criteria_count = len(defined_criteria)

        # Critical fail: Generic targeting
        if is_generic:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Generic "for everyone" target market detected',
                'legal_source': self.legal_source,
                'suggestion': 'PROD rules prohibit generic target markets. Define specific characteristics: customer type, knowledge/experience, financial situation, risk profile, objectives.',
                'spans': spans
            }

        # Fail: No target market defined
        if not has_target_market:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'No target market defined',
                'legal_source': self.legal_source,
                'suggestion': 'Product governance requires defining target market. Specify who the product IS and ISN\'T suitable for.',
                'spans': spans
            }

        # Warning: Target market mentioned but insufficient criteria
        if has_target_market and criteria_count < 2:
            details = []
            details.append(f'Defined criteria: {", ".join(list(defined_criteria.keys()))}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Target market mentioned but lacks sufficient criteria ({criteria_count} categories)',
                'legal_source': self.legal_source,
                'suggestion': 'Define target market using multiple criteria from: customer type, knowledge/experience, financial situation, risk profile, objectives, demographics.',
                'spans': spans,
                'details': details
            }

        # Pass: Good target market definition
        if criteria_count >= 2:
            quality_indicators = []
            if criteria_count >= 3:
                quality_indicators.append('comprehensive criteria')
            if has_negative_target:
                quality_indicators.append('exclusions stated')

            details = []
            details.append(f'Defined criteria: {", ".join(list(defined_criteria.keys()))}')
            if quality_indicators:
                details.append(f'Quality: {", ".join(quality_indicators)}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Target market well-defined ({criteria_count} criteria categories{": " + ", ".join(quality_indicators) if quality_indicators else ""})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Default pass
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Target market defined',
            'legal_source': self.legal_source,
            'spans': spans
        }
