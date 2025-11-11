"""
FCA Target Market Assessment Validator
Implements Product Governance (PROD) target market requirements

Legal References:
- PROD 1.4 & PROD 3 (Product Governance and Target Market)
- MiFID II Product Governance
- Consumer Duty (PRIN 2A.4) - Products & Services Outcome
"""

import re
from typing import Dict, List, Tuple


class TargetMarketAssessor:
    """
    Validates target market definitions for financial products
    Ensures PROD compliance in product design and distribution
    """

    def __init__(self):
        self.name = "target_market_assessor"
        self.legal_source = "FCA PROD 1.4 & PROD 3"

    TARGET_MARKET_DIMENSIONS = {
        'customer_type': ['retail', 'professional', 'eligible counterparty', 'high net worth', 'sophisticated'],
        'knowledge_experience': ['none', 'basic', 'informed', 'advanced', 'expert'],
        'financial_situation': ['low income', 'medium income', 'high income', 'high net worth'],
        'risk_tolerance': ['low', 'medium', 'high', 'very high'],
        'objectives': ['preservation', 'income', 'growth', 'speculation'],
        'distribution': ['advised', 'non-advised', 'execution only']
    }

    def assess_target_market(self, text: str, product_type: str = None) -> Dict:
        """Main target market assessment"""
        text_lower = text.lower()

        # Determine if document discusses target market
        if not self._discusses_target_market(text):
            return {
                'status': 'N/A',
                'message': 'Target market not discussed',
                'legal_source': self.legal_source
            }

        results = {
            'definition_present': self.check_definition_present(text),
            'specificity': self.check_specificity(text),
            'negative_target': self.check_negative_target_market(text),
            'distribution_strategy': self.check_distribution_strategy(text),
            'target_market_dimensions': self.analyze_target_market_dimensions(text),
            'generic_targeting': self.check_generic_targeting(text)
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
            'message': f'Target Market: {len(failures)} failures, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings
        }

    def _discusses_target_market(self, text: str) -> bool:
        """Check if document discusses target market"""
        target_market_terms = [
            r'target\s+market',
            r'target\s+customer',
            r'designed\s+for',
            r'intended\s+(?:for|customer)',
            r'suitable\s+for',
            r'appropriate\s+for',
            r'product\s+governance',
            r'customer\s+segment'
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in target_market_terms)

    def check_definition_present(self, text: str) -> Dict:
        """Check if target market is defined"""
        definition_patterns = [
            r'target\s+market\s+(?:is|comprises|includes|consists)',
            r'(?:designed|intended|suitable)\s+for\s+(?:customer|client|investor)s?\s+who',
            r'target\s+customer(?:s)?\s+(?:are|include)',
            r'(?:this|the)\s+product\s+is\s+(?:for|aimed\s+at)'
        ]

        has_definition = any(re.search(p, text, re.IGNORECASE) for p in definition_patterns)

        if not has_definition:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'No target market definition found',
                'legal_source': 'PROD 3.2.2R',
                'suggestion': 'Define target market: who the product IS designed for'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Target market definition present',
            'legal_source': 'PROD 3.2.2R'
        }

    def check_specificity(self, text: str) -> Dict:
        """Check specificity of target market definition"""
        # Count specific criteria mentioned
        specific_criteria = {
            'age': r'age(?:d)?\s+(?:between\s+)?\d+',
            'income': r'(?:income|salary|earning).*£[\d,]+',
            'experience': r'(?:\d+\s+years?|experienced|inexperienced)\s+(?:of\s+)?(?:investing|experience)',
            'wealth': r'(?:asset|wealth|net\s+worth).*£[\d,]+',
            'risk_level': r'(?:low|medium|high|balanced|cautious|adventurous)\s+risk',
            'investment_horizon': r'(?:time\s+horizon|investment\s+period).*(?:\d+\s+years?|long[- ]term|short[- ]term)',
            'capacity_for_loss': r'capacity\s+for\s+loss',
            'objectives': r'(?:seeking|looking\s+for|objective).*(?:growth|income|preservation)'
        }

        found_criteria = {}
        for criterion, pattern in specific_criteria.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_criteria[criterion] = True

        specificity_score = len(found_criteria)

        if specificity_score < 3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Target market lacks specificity ({specificity_score} criteria)',
                'legal_source': 'PROD 3.2.2R',
                'suggestion': 'Define target market with specific criteria: age, income, experience, risk tolerance, objectives, investment horizon',
                'found_criteria': list(found_criteria.keys())
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Target market well-defined ({specificity_score} specific criteria)',
            'legal_source': 'PROD 3.2.2R',
            'criteria': list(found_criteria.keys())
        }

    def check_negative_target_market(self, text: str) -> Dict:
        """
        Check for negative target market (who product is NOT for)
        Best practice under PROD
        """
        negative_patterns = [
            r'not\s+(?:suitable|appropriate|designed|intended)\s+for',
            r'should\s+not\s+(?:invest|purchase|use)',
            r'(?:exclude|excluding|excluded)',
            r'outside\s+(?:the\s+)?target\s+market',
            r'inappropriate\s+for',
            r'(?:who|customer).*should\s+not'
        ]

        has_negative_target = any(re.search(p, text, re.IGNORECASE) for p in negative_patterns)

        if not has_negative_target:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No negative target market (who it\'s NOT for)',
                'legal_source': 'PROD 3.2.2R (Best practice)',
                'suggestion': 'State who the product is NOT suitable for (e.g., customers with low risk tolerance, short investment horizons)'
            }

        # Check specificity of exclusions
        specific_exclusions = [
            r'not\s+suitable\s+for.*(?:risk[- ]averse|cautious|conservative)',
            r'not\s+suitable\s+for.*(?:short[- ]term|less\s+than\s+\d+\s+years)',
            r'not\s+suitable\s+for.*(?:inexperienced|no\s+experience)',
            r'exclude.*(?:specific\s+sector|country|industry)'
        ]

        is_specific = any(re.search(p, text, re.IGNORECASE) for p in specific_exclusions)

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Negative target market {"specified" if is_specific else "mentioned"}',
            'legal_source': 'PROD 3.2.2R',
            'specific': is_specific
        }

    def check_distribution_strategy(self, text: str) -> Dict:
        """Check for distribution strategy alignment with target market"""
        distribution_patterns = [
            r'distribution\s+(?:strategy|channel|method)',
            r'(?:advised|non[- ]advised|execution[- ]only)',
            r'(?:intermediar|distributor|platform)',
            r'how\s+(?:the\s+)?product\s+(?:will\s+be\s+|is\s+)?(?:sold|distributed|marketed)',
            r'sales\s+channel'
        ]

        has_distribution_strategy = any(re.search(p, text, re.IGNORECASE) for p in distribution_patterns)

        if not has_distribution_strategy:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No distribution strategy mentioned',
                'legal_source': 'PROD 3.2.10R',
                'suggestion': 'Define distribution strategy: advised, non-advised, channels, and how it aligns with target market'
            }

        # Check for alignment statement
        alignment_patterns = [
            r'(?:consistent|aligned|compatible)\s+with\s+target\s+market',
            r'distribution.*(?:appropriate|suitable)\s+for\s+target',
            r'target\s+market.*(?:through|via|using)'
        ]

        has_alignment = any(re.search(p, text, re.IGNORECASE) for p in alignment_patterns)

        if not has_alignment:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Distribution strategy mentioned but alignment not clear',
                'legal_source': 'PROD 3.2.10R',
                'suggestion': 'Explain how distribution strategy is consistent with target market needs'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Distribution strategy aligned with target market',
            'legal_source': 'PROD 3.2.10R'
        }

    def analyze_target_market_dimensions(self, text: str) -> Dict:
        """
        Analyze coverage of target market dimensions
        PROD requires assessment across multiple dimensions
        """
        dimensions_found = {}

        # Customer type
        customer_type_patterns = {
            'retail': r'\bretail\b',
            'professional': r'professional\s+(?:client|investor)',
            'high_net_worth': r'high\s+net\s+worth',
            'sophisticated': r'(?:sophisticated|certified)\s+investor',
            'eligible_counterparty': r'eligible\s+counterpart'
        }

        for ctype, pattern in customer_type_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                dimensions_found['customer_type'] = ctype
                break

        # Knowledge and experience
        knowledge_patterns = {
            'none': r'no\s+(?:experience|knowledge)',
            'basic': r'basic\s+(?:knowledge|understanding)',
            'informed': r'informed\s+investor',
            'advanced': r'(?:advanced|significant)\s+(?:knowledge|experience)',
            'expert': r'(?:expert|professional|sophisticated)'
        }

        for level, pattern in knowledge_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                dimensions_found['knowledge_experience'] = level
                break

        # Risk tolerance
        risk_patterns = {
            'low': r'(?:low|cautious|conservative)\s+risk',
            'medium': r'(?:medium|moderate|balanced)\s+risk',
            'high': r'(?:high|aggressive|adventurous)\s+risk',
            'very_high': r'(?:very\s+high|speculative|maximum)\s+risk'
        }

        for level, pattern in risk_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                dimensions_found['risk_tolerance'] = level
                break

        # Investment objectives
        objective_patterns = {
            'preservation': r'capital\s+preservation',
            'income': r'(?:income|yield|dividend)',
            'growth': r'capital\s+growth',
            'balanced': r'balanced\s+(?:growth|objective)',
            'speculation': r'speculative'
        }

        for obj, pattern in objective_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                dimensions_found['objective'] = obj
                break

        dimension_count = len(dimensions_found)

        if dimension_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Target market dimensions insufficient ({dimension_count} dimensions)',
                'legal_source': 'PROD 3.2.2R',
                'suggestion': 'Define target market across dimensions: customer type, knowledge/experience, risk tolerance, objectives',
                'found_dimensions': dimensions_found
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Target market dimensions defined ({dimension_count} dimensions)',
            'legal_source': 'PROD 3.2.2R',
            'dimensions': dimensions_found
        }

    def check_generic_targeting(self, text: str) -> Dict:
        """
        Check for prohibited generic targeting
        "For everyone" is not acceptable under PROD
        """
        generic_patterns = [
            r'(?:all|everyone|anyone|any)\s+(?:customer|investor|client)',
            r'suitable\s+for\s+(?:everyone|all|anyone)',
            r'no\s+(?:restriction|requirement|minimum|limit)',
            r'broadly\s+suitable',
            r'wide\s+(?:range|appeal)',
            r'mass\s+market',
            r'general\s+public',
            r'any\s+investor\s+(?:can|may)'
        ]

        has_generic_targeting = False
        examples = []

        for pattern in generic_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_generic_targeting = True
                for m in matches[:2]:  # Limit examples
                    examples.append(m.group())

        if has_generic_targeting:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Generic "for everyone" targeting detected',
                'legal_source': 'PROD 3.2.2R',
                'suggestion': 'PROD prohibits generic target markets. Define specific characteristics: customer type, knowledge, financial situation, risk profile.',
                'examples': examples
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No generic targeting detected',
            'legal_source': 'PROD 3.2.2R'
        }

    def generate_target_market_template(self) -> Dict:
        """Generate a template for proper target market definition"""
        return {
            'template': {
                'customer_type': 'Retail/Professional/High Net Worth/Sophisticated',
                'knowledge_experience': 'None/Basic/Informed/Advanced/Expert',
                'financial_situation': {
                    'minimum_income': '£X per year',
                    'minimum_investable_assets': '£X',
                    'capacity_for_loss': 'Description'
                },
                'risk_tolerance': 'Low/Medium/High/Very High',
                'investment_objectives': 'Preservation/Income/Growth/Speculation',
                'investment_horizon': 'Short-term (<5 years) / Medium-term (5-10) / Long-term (>10)',
                'distribution_strategy': 'Advised/Non-advised/Execution-only',
                'negative_target_market': 'Who the product is NOT suitable for'
            },
            'example': {
                'customer_type': 'Retail investors',
                'knowledge_experience': 'Informed investors with understanding of equity markets',
                'financial_situation': {
                    'minimum_income': '£30,000 per year',
                    'minimum_investable_assets': '£10,000',
                    'capacity_for_loss': 'Can afford to lose some or all of investment without affecting lifestyle'
                },
                'risk_tolerance': 'Medium to high risk tolerance',
                'investment_objectives': 'Capital growth over long term',
                'investment_horizon': 'Minimum 5 years',
                'distribution_strategy': 'Available on advised and non-advised basis through financial advisers and platforms',
                'negative_target_market': 'Not suitable for: risk-averse investors, those needing capital preservation, short-term investors (<5 years), or those without equity market understanding'
            }
        }
