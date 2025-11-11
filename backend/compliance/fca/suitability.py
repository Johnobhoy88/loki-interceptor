"""
FCA Suitability Report Validator
Validates suitability reports for investment advice

Legal References:
- COBS 9.2 (Assessing suitability)
- COBS 9.4 (Suitability reports)
- COBS 10 (Appropriateness)
"""

import re
from typing import Dict, List


class SuitabilityReportValidator:
    """
    Validates investment suitability reports
    Ensures all COBS 9.4 required elements are present
    """

    def __init__(self):
        self.name = "suitability_report"
        self.legal_source = "FCA COBS 9.4 (Suitability Reports)"

    def check_suitability_report(self, text: str) -> Dict:
        """Main suitability report validation"""
        text_lower = text.lower()

        # Determine if this is a suitability report
        if not self._is_suitability_report(text):
            return {
                'status': 'N/A',
                'message': 'Not a suitability report',
                'legal_source': self.legal_source
            }

        results = {
            'client_needs': self.check_client_needs(text),
            'recommendation': self.check_recommendation(text),
            'suitability_reason': self.check_suitability_reason(text),
            'risks': self.check_risks_explanation(text),
            'alternative_consideration': self.check_alternatives(text),
            'costs_charges': self.check_costs_and_charges(text),
            'disadvantages': self.check_disadvantages(text),
            'switching_justification': self.check_switching(text)
        }

        failures = [k for k, v in results.items() if v['status'] == 'FAIL']
        warnings = [k for k, v in results.items() if v['status'] == 'WARNING']

        overall_status = 'PASS'
        overall_severity = 'none'

        if failures:
            overall_status = 'FAIL'
            overall_severity = 'critical'
        elif warnings:
            overall_status = 'WARNING'
            overall_severity = 'medium'

        return {
            'status': overall_status,
            'severity': overall_severity,
            'message': f'Suitability Report: {len(failures)} failures, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings,
            'completeness': f'{len(results) - len(failures) - len(warnings)}/{len(results)} elements present'
        }

    def _is_suitability_report(self, text: str) -> bool:
        """Detect if this is a suitability report"""
        suitability_terms = [
            r'suitability\s+(?:report|letter|assessment)',
            r'(?:personal|investment)\s+recommendation',
            r'why\s+(?:this|the)\s+(?:investment|product|recommendation)\s+is\s+suitable',
            r'based\s+on\s+your\s+(?:circumstances|needs|objectives)',
            r'(?:recommend|advise).*(?:invest|purchase|buy|switch)'
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in suitability_terms)

    def check_client_needs(self, text: str) -> Dict:
        """
        Check for client needs, objectives, and circumstances
        COBS 9.2.1R: Must assess client's knowledge, experience, financial situation, objectives
        """
        needs_elements = {
            'knowledge_experience': [
                r'(?:knowledge|experience|understanding)\s+of',
                r'(?:familiar|experience)\s+with',
                r'(?:investment|financial)\s+experience',
                r'(?:never|previously)\s+invested'
            ],
            'financial_situation': [
                r'(?:income|salary|earning)',
                r'(?:asset|wealth|net\s+worth)',
                r'(?:existing|current)\s+(?:investment|savings|pension)',
                r'(?:regular|disposable)\s+income',
                r'financial\s+(?:position|situation|circumstances)'
            ],
            'investment_objectives': [
                r'(?:investment|financial)\s+(?:objective|goal|aim)',
                r'(?:seeking|looking\s+for|need|want|require)',
                r'(?:capital\s+)?(?:growth|income|preservation)',
                r'(?:retirement|long[- ]term|short[- ]term)',
                r'time\s+(?:horizon|frame|scale)'
            ],
            'risk_tolerance': [
                r'(?:risk\s+)?(?:tolerance|appetite|profile|attitude)',
                r'(?:prepared|willing|able)\s+to\s+(?:accept|take|bear)',
                r'(?:capacity|ability)\s+for\s+loss',
                r'(?:low|medium|high|balanced|cautious|adventurous)\s+risk'
            ]
        }

        found_elements = {}
        total_matches = 0

        for category, patterns in needs_elements.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if category not in found_elements:
                        found_elements[category] = True
                        total_matches += 1
                    break

        missing = [cat.replace('_', ' ') for cat in needs_elements.keys() if cat not in found_elements]

        if total_matches < 3:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Insufficient client needs assessment ({total_matches}/4 elements)',
                'legal_source': 'COBS 9.2.1R',
                'suggestion': f'Must assess all 4 elements: knowledge/experience, financial situation, objectives, risk tolerance. Missing: {", ".join(missing)}',
                'found': list(found_elements.keys()),
                'missing': missing
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Client needs comprehensively assessed ({total_matches}/4 elements)',
            'legal_source': 'COBS 9.2.1R',
            'elements': list(found_elements.keys())
        }

    def check_recommendation(self, text: str) -> Dict:
        """Check that recommendation is clearly stated"""
        recommendation_patterns = [
            r'(?:i|we)\s+recommend',
            r'(?:my|our)\s+recommendation',
            r'(?:i|we)\s+(?:advise|suggest)',
            r'(?:should|ought\s+to)\s+(?:invest|purchase|buy|transfer)',
            r'recommended\s+(?:product|investment|fund|plan)'
        ]

        has_recommendation = any(re.search(p, text, re.IGNORECASE) for p in recommendation_patterns)

        if not has_recommendation:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No clear recommendation stated',
                'legal_source': 'COBS 9.4.3R',
                'suggestion': 'Clearly state: "I/We recommend..." with specific product details'
            }

        # Check for product specificity
        product_details = [
            r'(?:fund|product|plan|policy|bond|isa)\s+name',
            r'provider:\s*\w+',
            r'(?:isin|sedol|fund\s+code)',
            r'\w+\s+(?:fund|investment|product)'
        ]

        has_specificity = any(re.search(p, text, re.IGNORECASE) for p in product_details)

        if not has_specificity:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Recommendation present but lacks product specificity',
                'legal_source': 'COBS 9.4.3R',
                'suggestion': 'Include specific product name, provider, and identifying codes'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Recommendation clearly stated with product details',
            'legal_source': 'COBS 9.4.3R'
        }

    def check_suitability_reason(self, text: str) -> Dict:
        """
        Check for explanation of why recommendation is suitable
        COBS 9.4.6R: Must explain why advice is suitable based on client information
        """
        suitability_explanations = [
            r'suitable\s+because',
            r'meets\s+your\s+(?:needs|objectives|goals)',
            r'aligns\s+with\s+your\s+(?:risk|objectives|circumstances)',
            r'appropriate\s+(?:for\s+you\s+)?because',
            r'based\s+on\s+your\s+(?:stated|expressed)',
            r'(?:consistent|in\s+line)\s+with\s+your'
        ]

        has_explanation = any(re.search(p, text, re.IGNORECASE) for p in suitability_explanations)

        if not has_explanation:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No explanation of why recommendation is suitable',
                'legal_source': 'COBS 9.4.6R',
                'suggestion': 'Explain specifically why this recommendation meets client\'s needs, objectives, and risk profile'
            }

        # Check for linkage to client circumstances
        linkage_patterns = [
            r'your\s+(?:need|objective|goal|circumstance|situation)',
            r'given\s+(?:your|that\s+you)',
            r'because\s+you\s+(?:are|have|want|need)',
            r'taking\s+into\s+account\s+your'
        ]

        linkage_count = sum(len(list(re.finditer(p, text, re.IGNORECASE))) for p in linkage_patterns)

        if linkage_count < 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Suitability explanation could be more detailed',
                'legal_source': 'COBS 9.4.6R',
                'suggestion': 'Strengthen connection between recommendation and client circumstances throughout document'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Suitability well explained ({linkage_count} linkages to client)',
            'legal_source': 'COBS 9.4.6R'
        }

    def check_risks_explanation(self, text: str) -> Dict:
        """Check for risk disclosure"""
        risk_patterns = [
            r'risk',
            r'(?:could|may|might)\s+(?:lose|fall|decrease)',
            r'(?:value|capital)\s+(?:can|may)\s+(?:go\s+down|fall|fluctuate)',
            r'not\s+guaranteed',
            r'volatile'
        ]

        risk_mentions = sum(len(list(re.finditer(p, text, re.IGNORECASE))) for p in risk_patterns)

        if risk_mentions == 0:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No risk disclosure',
                'legal_source': 'COBS 9.4.7R',
                'suggestion': 'Must explain specific risks of recommendation'
            }

        # Check for specific risk types
        specific_risks = {
            'market_risk': r'market\s+risk',
            'volatility': r'volatil(?:e|ity)',
            'capital_loss': r'(?:lose|loss\s+of).*(?:capital|money|investment)',
            'inflation_risk': r'inflation\s+risk',
            'currency_risk': r'currency\s+risk',
            'liquidity_risk': r'liquidity\s+risk'
        }

        found_risks = [risk_type for risk_type, pattern in specific_risks.items()
                       if re.search(pattern, text, re.IGNORECASE)]

        if len(found_risks) < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Generic risk disclosure ({len(found_risks)} specific risks)',
                'legal_source': 'COBS 9.4.7R',
                'suggestion': 'Provide specific risk types: market, volatility, capital loss, inflation, currency, liquidity'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Risks explained ({len(found_risks)} specific risks disclosed)',
            'legal_source': 'COBS 9.4.7R',
            'risks': found_risks
        }

    def check_alternatives(self, text: str) -> Dict:
        """Check if alternatives were considered"""
        alternatives_patterns = [
            r'(?:alternative|other)\s+(?:option|product|investment|solution)',
            r'considered\s+(?:other|alternative)',
            r'compared\s+(?:with|to|against)',
            r'(?:why\s+)?(?:not|rejected)\s+(?:other|alternative)',
            r'reasons?\s+for\s+(?:not\s+)?choosing'
        ]

        has_alternatives = any(re.search(p, text, re.IGNORECASE) for p in alternatives_patterns)

        if not has_alternatives:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No mention of alternatives considered',
                'legal_source': 'COBS 9.2.6R',
                'suggestion': 'Demonstrate alternatives were considered and explain why recommendation is most suitable'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Alternatives considered',
            'legal_source': 'COBS 9.2.6R'
        }

    def check_costs_and_charges(self, text: str) -> Dict:
        """Check for costs and charges disclosure"""
        cost_patterns = [
            r'(?:cost|charge|fee)s?',
            r'(?:initial|ongoing|exit|annual)\s+(?:charge|fee|cost)',
            r'total\s+cost',
            r'£\d+',
            r'\d+\.?\d*%',
            r'(?:no\s+)?commission',
            r'transaction\s+(?:cost|fee)'
        ]

        cost_mentions = sum(len(list(re.finditer(p, text, re.IGNORECASE))) for p in cost_patterns)

        if cost_mentions == 0:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No costs or charges disclosed',
                'legal_source': 'COBS 6.1ZA & 9.4',
                'suggestion': 'Must disclose all costs: initial charges, ongoing charges, transaction costs, exit fees'
            }

        # Check for comprehensive disclosure
        cost_elements = {
            'initial': r'initial\s+(?:charge|fee|cost)',
            'ongoing': r'ongoing\s+(?:charge|fee|cost)',
            'transaction': r'transaction\s+(?:cost|fee)',
            'total': r'total\s+(?:cost|charge)'
        }

        found_elements = [elem for elem, pattern in cost_elements.items()
                         if re.search(pattern, text, re.IGNORECASE)]

        if len(found_elements) < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Limited cost disclosure ({len(found_elements)} elements)',
                'legal_source': 'COBS 6.1ZA',
                'suggestion': 'Disclose: initial charges, ongoing charges, transaction costs, total cost in £ and %'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Costs disclosed ({len(found_elements)} elements)',
            'legal_source': 'COBS 6.1ZA',
            'elements': found_elements
        }

    def check_disadvantages(self, text: str) -> Dict:
        """Check for disadvantages disclosure"""
        disadvantage_patterns = [
            r'disadvantage',
            r'drawback',
            r'limitation',
            r'restriction',
            r'(?:not|cannot)\s+(?:access|withdraw|exit)',
            r'(?:tied|locked)\s+in',
            r'penalty\s+(?:for|if)',
            r'(?:con|downside)'
        ]

        has_disadvantages = any(re.search(p, text, re.IGNORECASE) for p in disadvantage_patterns)

        if not has_disadvantages:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No disadvantages mentioned',
                'legal_source': 'COBS 9.4.9R',
                'suggestion': 'Disclose any disadvantages: restrictions, penalties, limitations'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Disadvantages disclosed',
            'legal_source': 'COBS 9.4.9R'
        }

    def check_switching(self, text: str) -> Dict:
        """Check switching justification if applicable"""
        switching_indicators = [
            r'switch(?:ing)?',
            r'transfer(?:ring)?\s+(?:from|out\s+of)',
            r'existing\s+(?:investment|policy|pension)',
            r'surrender',
            r'encash',
            r'replace\s+(?:current|existing)'
        ]

        is_switching = any(re.search(p, text, re.IGNORECASE) for p in switching_indicators)

        if not is_switching:
            return {
                'status': 'N/A',
                'message': 'Not a switching recommendation',
                'legal_source': 'COBS 9.4.10R'
            }

        # Check for switching justification
        justification_patterns = [
            r'benefit.*(?:switch|transfer)',
            r'(?:advantage|reason)\s+(?:for|to)\s+(?:switch|transfer)',
            r'(?:current|existing).*(?:unsuitable|inappropriate|not\s+meeting)',
            r'(?:better|improved|enhanced).*(?:than|compared)',
            r'(?:lower\s+)?(?:cost|charge|fee)',
            r'(?:exit|penalty)\s+(?:charge|fee)'
        ]

        has_justification = any(re.search(p, text, re.IGNORECASE) for p in justification_patterns)

        if not has_justification:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Switching recommended without clear justification',
                'legal_source': 'COBS 9.4.10R',
                'suggestion': 'Must explain why switching is beneficial, including comparison of costs, benefits, and any penalties'
            }

        # Check for loss disclosure
        loss_patterns = [
            r'(?:lose|loss\s+of).*(?:benefit|guarantee|bonus)',
            r'(?:exit|surrender|penalty)\s+(?:charge|fee)',
            r'give\s+up',
            r'no\s+longer\s+(?:have|receive)'
        ]

        has_loss_disclosure = any(re.search(p, text, re.IGNORECASE) for p in loss_patterns)

        if not has_loss_disclosure:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Switching justified but potential losses not fully disclosed',
                'legal_source': 'COBS 9.4.10R',
                'suggestion': 'Disclose any lost benefits, guarantees, bonuses, or exit penalties'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Switching properly justified with loss disclosure',
            'legal_source': 'COBS 9.4.10R'
        }
