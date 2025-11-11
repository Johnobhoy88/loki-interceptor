"""
FCA Consumer Duty Compliance Checker
Covers all 4 Consumer Duty Outcomes (PS22/9)

Legal References:
- PRIN 2A (Consumer Duty)
- Cross-cutting rules
- Four Outcomes: Products & Services, Price & Value, Consumer Understanding, Consumer Support
"""

import re
from typing import Dict, List, Tuple


class ConsumerDutyChecker:
    """
    Validates compliance with FCA Consumer Duty requirements
    Effective from July 31, 2023 (new products) / July 31, 2024 (existing)
    """

    def __init__(self):
        self.name = "consumer_duty"
        self.legal_source = "FCA PRIN 2A (Consumer Duty)"

    def check_all_outcomes(self, text: str, document_type: str = None) -> Dict:
        """Check all 4 Consumer Duty outcomes"""
        results = {
            'products_services': self.check_products_services_outcome(text),
            'price_value': self.check_price_value_outcome(text),
            'consumer_understanding': self.check_consumer_understanding_outcome(text),
            'consumer_support': self.check_consumer_support_outcome(text)
        }

        # Aggregate results
        total_fails = sum(1 for r in results.values() if r['status'] == 'FAIL')
        total_warnings = sum(1 for r in results.values() if r['status'] == 'WARNING')
        total_passes = sum(1 for r in results.values() if r['status'] == 'PASS')

        overall_status = 'PASS'
        if total_fails > 0:
            overall_status = 'FAIL'
        elif total_warnings > 0:
            overall_status = 'WARNING'

        return {
            'status': overall_status,
            'severity': 'critical' if total_fails > 0 else 'medium' if total_warnings > 0 else 'none',
            'message': f'Consumer Duty: {total_passes} outcomes pass, {total_warnings} warnings, {total_fails} fails',
            'legal_source': self.legal_source,
            'outcomes': results,
            'summary': {
                'passes': total_passes,
                'warnings': total_warnings,
                'fails': total_fails
            }
        }

    def check_products_services_outcome(self, text: str) -> Dict:
        """
        Outcome 1: Products and Services
        Products and services meet needs of customers in target market
        Reference: PRIN 2A.4 & PROD
        """
        text_lower = text.lower()
        spans = []
        issues = []

        # Check for product suitability statements
        suitability_patterns = [
            r'designed\s+(?:to\s+)?meet\s+(?:the\s+)?needs',
            r'suitable\s+for\s+(?:customer|client|target\s+market)',
            r'appropriate\s+for\s+(?:customer|client)',
            r'fit\s+for\s+purpose',
            r'intended\s+use'
        ]

        has_suitability = any(re.search(p, text, re.IGNORECASE) for p in suitability_patterns)

        # Check for red flags - products sold that don't meet needs
        red_flags = [
            r'(?:all|any)\s+customer.*(?:can\s+buy|may\s+purchase)',
            r'sold\s+to\s+(?:maximize|increase)\s+(?:profit|commission|sales)',
            r'regardless\s+of\s+(?:need|suitability|appropriateness)',
            r'no\s+(?:assessment|check)\s+(?:of\s+)?(?:need|suitability)'
        ]

        for pattern in red_flags:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                issues.append('Product governance failure detected')
                for m in matches:
                    spans.append({
                        'type': 'product_outcome_failure',
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Check for distribution strategy
        distribution_terms = ['distribution strategy', 'target market', 'customer segment']
        has_distribution = any(term in text_lower for term in distribution_terms)

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Products & Services Outcome: Critical issues detected',
                'legal_source': 'PRIN 2A.4 (Products & Services Outcome)',
                'issues': issues,
                'spans': spans
            }

        if not has_suitability:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Products & Services: No clear suitability statement',
                'legal_source': 'PRIN 2A.4',
                'suggestion': 'Explain how product meets needs of target market'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Products & Services Outcome: Requirements met',
            'legal_source': 'PRIN 2A.4'
        }

    def check_price_value_outcome(self, text: str) -> Dict:
        """
        Outcome 2: Price and Value
        Price represents fair value
        Reference: PRIN 2A.5
        """
        text_lower = text.lower()
        spans = []
        issues = []

        # Check for fair value assessment
        value_patterns = [
            r'fair\s+value',
            r'value\s+for\s+money',
            r'price.*(?:reflects|proportionate|reasonable)',
            r'(?:assessed|evaluated)\s+(?:the\s+)?value',
            r'fair\s+price'
        ]

        has_value_assessment = any(re.search(p, text, re.IGNORECASE) for p in value_patterns)

        # Red flags - unfair pricing
        pricing_red_flags = [
            r'maximize.*(?:fee|charge|price)',
            r'hidden\s+(?:fee|charge|cost)',
            r'(?:excessive|unfair|exploitative)\s+(?:fee|charge|price)',
            r'no\s+value\s+(?:for\s+money|assessment)',
            r'price.*not\s+justified'
        ]

        for pattern in pricing_red_flags:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                issues.append('Unfair pricing indicator detected')
                for m in matches:
                    spans.append({
                        'type': 'price_value_failure',
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Check for fee transparency
        transparency_terms = ['fee breakdown', 'charge breakdown', 'total cost', 'all-in cost']
        has_transparency = any(term in text_lower for term in transparency_terms)

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Price & Value Outcome: Unfair pricing detected',
                'legal_source': 'PRIN 2A.5 (Price & Value Outcome)',
                'issues': issues,
                'spans': spans
            }

        if not has_value_assessment and ('price' in text_lower or 'fee' in text_lower or 'charge' in text_lower):
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Price & Value: No fair value assessment',
                'legal_source': 'PRIN 2A.5',
                'suggestion': 'Include fair value assessment showing price is proportionate to benefits'
            }

        return {
            'status': 'PASS' if has_value_assessment else 'N/A',
            'severity': 'none',
            'message': 'Price & Value Outcome: Requirements met' if has_value_assessment else 'Not applicable',
            'legal_source': 'PRIN 2A.5'
        }

    def check_consumer_understanding_outcome(self, text: str) -> Dict:
        """
        Outcome 3: Consumer Understanding
        Communications enable customers to make informed decisions
        Reference: PRIN 2A.6
        """
        text_lower = text.lower()
        spans = []
        issues = []

        # Check for clarity indicators
        clarity_indicators = [
            r'clear(?:ly)?\s+(?:explain|state|set\s+out)',
            r'(?:plain|simple)\s+(?:language|english|terms)',
            r'easy\s+to\s+understand',
            r'avoid.*jargon',
            r'consumer\s+testing'
        ]

        has_clarity = any(re.search(p, text, re.IGNORECASE) for p in clarity_indicators)

        # Red flags - confusing or misleading
        confusion_flags = [
            r'(?:complex|technical|complicated)\s+(?:language|terms|jargon)',
            r'(?:hidden|buried|obscured)\s+(?:in|within)\s+(?:footnote|small\s+print)',
            r'difficult\s+to\s+understand',
            r'no\s+(?:explanation|definition)',
            r'assume.*(?:knowledge|understanding|familiarity)'
        ]

        for pattern in confusion_flags:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                issues.append('Consumer understanding barrier detected')
                for m in matches:
                    spans.append({
                        'type': 'understanding_failure',
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for key information prominence
        has_key_info = bool(re.search(r'key\s+(?:information|facts|features|risks)', text, re.IGNORECASE))

        # Check for accessibility
        accessibility_terms = ['accessible', 'large print', 'audio', 'braille', 'reasonable adjustment']
        has_accessibility = any(term in text_lower for term in accessibility_terms)

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Consumer Understanding Outcome: Barriers detected',
                'legal_source': 'PRIN 2A.6 (Consumer Understanding Outcome)',
                'issues': issues,
                'spans': spans
            }

        if not has_clarity and len(text.split()) > 100:  # Only check for longer documents
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Consumer Understanding: Clarity could be improved',
                'legal_source': 'PRIN 2A.6',
                'suggestion': 'Use plain language, avoid jargon, ensure key information is prominent'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Consumer Understanding Outcome: Requirements met',
            'legal_source': 'PRIN 2A.6'
        }

    def check_consumer_support_outcome(self, text: str) -> Dict:
        """
        Outcome 4: Consumer Support
        Customer service meets needs throughout product lifecycle
        Reference: PRIN 2A.7
        """
        text_lower = text.lower()
        spans = []
        issues = []

        # Check for support availability
        support_patterns = [
            r'(?:customer|client)\s+(?:support|service|help)',
            r'contact\s+(?:us|details)',
            r'(?:phone|email|chat|helpline)',
            r'(?:available|open)\s+(?:\d+/\d+|\d+\s+hours)',
            r'assistance.*(?:available|provided)',
            r'help(?:desk|line)'
        ]

        has_support = any(re.search(p, text, re.IGNORECASE) for p in support_patterns)

        # Check for complaints process
        complaints_patterns = [
            r'complaint(?:s)?',
            r'(?:unhappy|dissatisfied|problem)',
            r'financial\s+ombudsman',
            r'escalat(?:e|ion)'
        ]

        has_complaints = any(re.search(p, text, re.IGNORECASE) for p in complaints_patterns)

        # Red flags - poor support
        support_red_flags = [
            r'no\s+(?:support|customer\s+service|help)',
            r'(?:limited|restricted)\s+(?:support|service)',
            r'(?:only|exclusively)\s+(?:online|email)',
            r'cannot\s+(?:contact|reach|speak\s+to)',
            r'no\s+complaint(?:s)?\s+process'
        ]

        for pattern in support_red_flags:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                issues.append('Inadequate consumer support detected')
                for m in matches:
                    spans.append({
                        'type': 'support_failure',
                        'text': m.group(),
                        'severity': 'high'
                    })

        # Check for vulnerable customer support
        vulnerability_terms = ['vulnerable customer', 'additional support', 'reasonable adjustment']
        has_vulnerability_support = any(term in text_lower for term in vulnerability_terms)

        if issues:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Consumer Support Outcome: Inadequate support',
                'legal_source': 'PRIN 2A.7 (Consumer Support Outcome)',
                'issues': issues,
                'spans': spans
            }

        # Document must mention support if it's customer-facing
        is_customer_facing = any(term in text_lower for term in ['customer', 'client', 'you', 'your'])

        if is_customer_facing and not has_support and len(text.split()) > 200:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Consumer Support: No support information provided',
                'legal_source': 'PRIN 2A.7',
                'suggestion': 'Include customer support contact details and complaints process'
            }

        return {
            'status': 'PASS' if has_support else 'N/A',
            'severity': 'none',
            'message': 'Consumer Support Outcome: Requirements met' if has_support else 'Not applicable',
            'legal_source': 'PRIN 2A.7'
        }

    def assess_foreseeable_harm(self, text: str) -> Dict:
        """
        Check for foreseeable harm prevention
        Core requirement across all Consumer Duty outcomes
        """
        text_lower = text.lower()

        harm_indicators = [
            r'foreseeable\s+harm',
            r'prevent\s+(?:harm|detriment)',
            r'avoid\s+(?:harm|poor\s+outcome)',
            r'mitigate\s+risk\s+of\s+harm'
        ]

        has_harm_prevention = any(re.search(p, text, re.IGNORECASE) for p in harm_indicators)

        # Known harm scenarios
        harm_scenarios = [
            r'(?:cancel|exit).*(?:difficult|impossible|penalty)',
            r'(?:lock|tie)(?:d)?\s+in',
            r'(?:automatic|auto).*renew(?:al)?.*without\s+(?:notice|consent)',
            r'(?:pressure|rush|urgency).*(?:decision|purchase)',
            r'vulnerable.*(?:target|exploit)'
        ]

        harm_risks = []
        for pattern in harm_scenarios:
            if re.search(pattern, text, re.IGNORECASE):
                harm_risks.append(pattern)

        if harm_risks:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Foreseeable harm: Risk scenarios detected',
                'legal_source': 'PRIN 2A.2 (Foreseeable Harm)',
                'risks': harm_risks
            }

        return {
            'status': 'PASS' if has_harm_prevention else 'N/A',
            'message': 'Foreseeable harm prevention addressed' if has_harm_prevention else 'Not applicable',
            'legal_source': 'PRIN 2A.2'
        }
