"""
FCA Risk Categorization Module
Automated risk assessment and categorization of financial products and communications

Legal References:
- PS22/10: High-risk investments and non-mass market investments
- COBS 4.7 & 4.12A: Financial promotions to different customer categories
- COBS 10: Appropriateness
"""

import re
from typing import Dict, List, Tuple


class RiskCategorizer:
    """
    Automatically categorizes financial products and communications by risk level
    Assists with appropriate targeting and warnings
    """

    def __init__(self):
        self.name = "risk_categorizer"
        self.legal_source = "FCA PS22/10 & COBS 4.7"

    # High-risk investment indicators (PS22/10)
    HIGH_RISK_INDICATORS = [
        r'\bcrypto(?:currency|asset|token)s?\b',
        r'\bp2p\s+(?:lend|loan)\b',
        r'peer[- ]to[- ]peer',
        r'\bcrowd(?:fund|lending)\b',
        r'speculative\s+mini[- ]?bond',
        r'unregulated\s+collective\s+investment',
        r'\bsto\b',  # Security Token Offering
        r'(?:exotic|structured|complex)\s+(?:derivative|product)',
        r'(?:binary|digital)\s+option',
        r'contract\s+for\s+difference',
        r'\bcfd\b',
        r'(?:forex|foreign\s+exchange)\s+trading',
        r'(?:storage\s+pod|parking|hotel\s+room)\s+investment',
        r'unquoted\s+(?:share|security|equity)',
        r'(?:alternative|illiquid)\s+investment'
    ]

    # Medium-risk indicators
    MEDIUM_RISK_INDICATORS = [
        r'(?:equity|stock|share)\s+(?:fund|investment)',
        r'emerging\s+market',
        r'(?:corporate|high[- ]yield)\s+bond',
        r'(?:balanced|mixed)\s+(?:fund|portfolio)',
        r'(?:property|real\s+estate)\s+fund',
        r'(?:managed|discretionary)\s+portfolio',
        r'(?:unit\s+trust|oeic|investment\s+trust)',
        r'collective\s+investment'
    ]

    # Low-risk indicators
    LOW_RISK_INDICATORS = [
        r'(?:cash|deposit|savings)\s+account',
        r'(?:gilt|government)\s+bond',
        r'(?:investment[- ]grade|aaa|aa)\s+bond',
        r'money\s+market\s+fund',
        r'capital[- ]protected',
        r'guaranteed\s+(?:return|income)',
        r'(?:fixed|term)\s+deposit',
        r'treasury\s+(?:bill|bond)',
        r'pension\s+(?:annuity|guaranteed)'
    ]

    def categorize_risk(self, text: str, product_type: str = None) -> Dict:
        """Main risk categorization function"""
        text_lower = text.lower()

        # Detect risk indicators
        high_risk_matches = self._find_risk_indicators(text, self.HIGH_RISK_INDICATORS)
        medium_risk_matches = self._find_risk_indicators(text, self.MEDIUM_RISK_INDICATORS)
        low_risk_matches = self._find_risk_indicators(text, self.LOW_RISK_INDICATORS)

        # Score-based categorization
        high_score = len(high_risk_matches)
        medium_score = len(medium_risk_matches)
        low_score = len(low_risk_matches)

        # Determine overall risk category
        if high_score > 0:
            risk_category = 'HIGH'
            risk_level = 'high'
            severity = 'critical'
        elif medium_score > low_score:
            risk_category = 'MEDIUM'
            risk_level = 'medium'
            severity = 'medium'
        elif low_score > 0:
            risk_category = 'LOW'
            risk_level = 'low'
            severity = 'none'
        else:
            risk_category = 'UNCLASSIFIED'
            risk_level = 'unknown'
            severity = 'none'

        # Analyze risk warnings present
        warnings_analysis = self.analyze_risk_warnings(text, risk_level)

        # Check target audience appropriateness
        audience_check = self.check_audience_appropriateness(text, risk_level)

        # Generate required warnings
        required_warnings = self.generate_required_warnings(risk_level)

        return {
            'risk_category': risk_category,
            'risk_level': risk_level,
            'severity': severity,
            'confidence': 'high' if (high_score + medium_score + low_score) >= 2 else 'medium',
            'indicators': {
                'high_risk': high_risk_matches,
                'medium_risk': medium_risk_matches,
                'low_risk': low_risk_matches
            },
            'scores': {
                'high': high_score,
                'medium': medium_score,
                'low': low_score
            },
            'warnings_analysis': warnings_analysis,
            'audience_check': audience_check,
            'required_warnings': required_warnings,
            'legal_source': self.legal_source
        }

    def _find_risk_indicators(self, text: str, indicators: List[str]) -> List[str]:
        """Find risk indicators in text"""
        found = []
        for pattern in indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Add unique matches
                for match in matches:
                    if match not in found:
                        found.append(match)
        return found

    def analyze_risk_warnings(self, text: str, risk_level: str) -> Dict:
        """Analyze risk warnings present in text"""
        # General risk warnings
        general_warnings = [
            r'(?:high|significant|substantial)\s+risk',
            r'(?:could|may|might)\s+lose\s+(?:all|some|entire)',
            r'value.*(?:can|may)\s+(?:go\s+down|fall|fluctuate)',
            r'not\s+guaranteed',
            r'(?:capital|investment)\s+at\s+risk',
            r'past\s+performance.*not.*(?:guide|indicator)'
        ]

        # Specific warnings for high-risk
        high_risk_warnings = [
            r'high[- ]risk\s+investment',
            r'speculative',
            r'(?:could|may)\s+lose\s+all',
            r'(?:no|unlikely).*protection',
            r'not\s+(?:suitable|appropriate)\s+for\s+(?:all|everyone)',
            r'(?:complex|difficult\s+to\s+understand)',
            r'(?:illiquid|difficult\s+to\s+sell)'
        ]

        # Count warnings
        general_count = sum(1 for p in general_warnings if re.search(p, text, re.IGNORECASE))
        high_risk_count = sum(1 for p in high_risk_warnings if re.search(p, text, re.IGNORECASE))

        total_warnings = general_count + high_risk_count

        # Assess adequacy
        if risk_level == 'high':
            required_warnings = 4
            adequate = total_warnings >= required_warnings and high_risk_count >= 2
        elif risk_level == 'medium':
            required_warnings = 2
            adequate = total_warnings >= required_warnings
        else:
            required_warnings = 1
            adequate = total_warnings >= required_warnings

        return {
            'total_warnings': total_warnings,
            'general_warnings': general_count,
            'high_risk_warnings': high_risk_count,
            'required_warnings': required_warnings,
            'adequate': adequate,
            'status': 'PASS' if adequate else 'FAIL',
            'message': f'Risk warnings {"adequate" if adequate else "inadequate"} for {risk_level} risk product'
        }

    def check_audience_appropriateness(self, text: str, risk_level: str) -> Dict:
        """Check if target audience is appropriate for risk level"""
        # Detect target audience
        audience_patterns = {
            'retail_mass_market': r'(?:all|any|everyone).*(?:customer|investor)',
            'retail_general': r'retail\s+(?:customer|investor|client)',
            'high_net_worth': r'high\s+net\s+worth',
            'sophisticated': r'(?:sophisticated|certified)\s+investor',
            'professional': r'professional\s+(?:client|investor)',
            'restricted': r'(?:restricted|limited)\s+to'
        }

        detected_audience = None
        for audience_type, pattern in audience_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected_audience = audience_type
                break

        if not detected_audience:
            return {
                'status': 'WARNING',
                'message': 'Target audience not clearly defined',
                'suggestion': f'For {risk_level} risk products, clearly define target audience'
            }

        # Check appropriateness
        if risk_level == 'high':
            # High-risk should be restricted
            if detected_audience in ['retail_mass_market', 'retail_general']:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'audience': detected_audience,
                    'message': 'High-risk product targeted at mass retail market',
                    'legal_source': 'FCA PS22/10',
                    'suggestion': 'High-risk investments must be restricted to: sophisticated investors, high net worth, or certified investors'
                }
            elif detected_audience in ['sophisticated', 'high_net_worth', 'professional', 'restricted']:
                return {
                    'status': 'PASS',
                    'audience': detected_audience,
                    'message': f'Audience appropriately restricted ({detected_audience})'
                }

        elif risk_level == 'medium':
            # Medium risk should have appropriateness assessment or be advised
            appropriateness_check = bool(re.search(r'appropriateness\s+(?:test|assessment|check)', text, re.IGNORECASE))
            advised = bool(re.search(r'advised\s+(?:basis|sale|only)', text, re.IGNORECASE))

            if detected_audience == 'retail_mass_market' and not (appropriateness_check or advised):
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'audience': detected_audience,
                    'message': 'Medium-risk to mass market without appropriateness check',
                    'suggestion': 'Consider appropriateness assessment or advised sale for medium-risk products'
                }

        # Default pass
        return {
            'status': 'PASS',
            'audience': detected_audience,
            'message': 'Audience targeting appears appropriate'
        }

    def generate_required_warnings(self, risk_level: str) -> Dict:
        """Generate list of required warnings based on risk level"""
        warnings = {
            'high': [
                'This is a high-risk investment',
                'You could lose all the money you invest',
                'This investment is unlikely to be protected if something goes wrong',
                'This investment is complex and difficult to understand',
                'Not suitable for all investors',
                'This investment may be illiquid (difficult to sell)',
                'Restricted to sophisticated/high net worth/professional investors only'
            ],
            'medium': [
                'The value of investments can go down as well as up',
                'You may get back less than you invest',
                'Past performance is not a guide to future returns',
                'Consider taking financial advice'
            ],
            'low': [
                'The value of investments can fluctuate',
                'Past performance is not a reliable indicator of future results'
            ]
        }

        return {
            'risk_level': risk_level,
            'required_warnings': warnings.get(risk_level, warnings['medium']),
            'count': len(warnings.get(risk_level, warnings['medium']))
        }

    def assess_document_risk_profile(self, text: str) -> Dict:
        """Comprehensive document risk profile assessment"""
        # Get base categorization
        base_assessment = self.categorize_risk(text)

        # Additional analyses
        complexity_score = self._assess_complexity(text)
        volatility_indicators = self._detect_volatility_mentions(text)
        liquidity_concerns = self._check_liquidity(text)
        leverage_usage = self._check_leverage(text)
        regulatory_status = self._check_regulatory_status(text)

        # Calculate overall risk score (0-100)
        risk_score = self._calculate_risk_score(
            base_assessment,
            complexity_score,
            len(volatility_indicators),
            liquidity_concerns,
            leverage_usage,
            regulatory_status
        )

        return {
            'base_assessment': base_assessment,
            'risk_score': risk_score,
            'complexity_score': complexity_score,
            'volatility_indicators': volatility_indicators,
            'liquidity_concerns': liquidity_concerns,
            'leverage_detected': leverage_usage,
            'regulatory_status': regulatory_status,
            'overall_risk_rating': self._score_to_rating(risk_score),
            'recommendations': self._generate_recommendations(risk_score, base_assessment)
        }

    def _assess_complexity(self, text: str) -> int:
        """Assess product complexity (0-10)"""
        complexity_terms = [
            r'complex',
            r'derivative',
            r'synthetic',
            r'structured',
            r'algorithm',
            r'(?:multi|multiple)[- ](?:layer|tier|strategy)',
            r'hedg(?:e|ing)',
            r'leverage(?:d)?',
            r'exotic',
            r'non[- ]linear'
        ]

        complexity_count = sum(1 for term in complexity_terms if re.search(term, text, re.IGNORECASE))
        return min(complexity_count, 10)

    def _detect_volatility_mentions(self, text: str) -> List[str]:
        """Detect volatility indicators"""
        volatility_patterns = [
            r'volatile|volatility',
            r'significant\s+(?:fluctuation|swing|movement)',
            r'price\s+(?:swing|movement|fluctuation)',
            r'rapid\s+(?:change|movement)',
            r'market\s+(?:volatility|turbulence)'
        ]

        found = []
        for pattern in volatility_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found.append(pattern)
        return found

    def _check_liquidity(self, text: str) -> bool:
        """Check for liquidity concerns"""
        liquidity_concerns = [
            r'illiquid',
            r'difficult\s+to\s+sell',
            r'no\s+(?:secondary|liquid)\s+market',
            r'lock[- ](?:in|up)\s+period',
            r'(?:minimum|notice)\s+period.*(?:withdraw|redeem)',
            r'cannot\s+(?:sell|exit|redeem)\s+(?:easily|quickly)'
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in liquidity_concerns)

    def _check_leverage(self, text: str) -> bool:
        """Check for leverage usage"""
        leverage_patterns = [
            r'leverage(?:d)?',
            r'gear(?:ed|ing)',
            r'margin\s+(?:trading|requirement)',
            r'borrow(?:ing)?\s+to\s+invest',
            r'\d+x\s+(?:leverage|exposure)',
            r'amplif(?:y|ied)\s+(?:gain|loss|return)'
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in leverage_patterns)

    def _check_regulatory_status(self, text: str) -> str:
        """Check regulatory status"""
        if re.search(r'(?:not|un)regulated', text, re.IGNORECASE):
            return 'unregulated'
        elif re.search(r'fca\s+(?:regulated|authorised)', text, re.IGNORECASE):
            return 'regulated'
        else:
            return 'unclear'

    def _calculate_risk_score(self, base_assessment: Dict, complexity: int,
                             volatility_count: int, liquidity: bool,
                             leverage: bool, reg_status: str) -> int:
        """Calculate overall risk score (0-100)"""
        score = 0

        # Base risk level
        risk_level = base_assessment.get('risk_level', 'medium')
        if risk_level == 'high':
            score += 60
        elif risk_level == 'medium':
            score += 35
        else:
            score += 10

        # Complexity
        score += complexity * 2  # max +20

        # Volatility
        score += volatility_count * 3  # max +15

        # Liquidity concerns
        if liquidity:
            score += 10

        # Leverage
        if leverage:
            score += 15

        # Regulatory status
        if reg_status == 'unregulated':
            score += 10
        elif reg_status == 'unclear':
            score += 5

        return min(score, 100)

    def _score_to_rating(self, score: int) -> str:
        """Convert risk score to rating"""
        if score >= 70:
            return 'VERY HIGH RISK'
        elif score >= 50:
            return 'HIGH RISK'
        elif score >= 30:
            return 'MEDIUM RISK'
        else:
            return 'LOW RISK'

    def _generate_recommendations(self, risk_score: int, base_assessment: Dict) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []

        if risk_score >= 70:
            recommendations.append('Restrict to sophisticated/high net worth/professional investors only')
            recommendations.append('Include comprehensive risk warnings')
            recommendations.append('Require appropriateness or suitability assessment')
            recommendations.append('Consider 24-hour cooling-off period')

        elif risk_score >= 50:
            recommendations.append('Consider restricting to experienced investors')
            recommendations.append('Include clear risk warnings')
            recommendations.append('Recommend appropriateness assessment')

        elif risk_score >= 30:
            recommendations.append('Include standard risk warnings')
            recommendations.append('Consider appropriateness for non-advised sales')

        else:
            recommendations.append('Include minimal risk warnings')
            recommendations.append('May be suitable for mass retail market')

        # Check if warnings are adequate
        warnings_analysis = base_assessment.get('warnings_analysis', {})
        if not warnings_analysis.get('adequate', True):
            recommendations.append('ADD MISSING RISK WARNINGS - Current warnings inadequate')

        # Check audience appropriateness
        audience_check = base_assessment.get('audience_check', {})
        if audience_check.get('status') == 'FAIL':
            recommendations.append('REVISE TARGET AUDIENCE - Current targeting inappropriate for risk level')

        return recommendations
