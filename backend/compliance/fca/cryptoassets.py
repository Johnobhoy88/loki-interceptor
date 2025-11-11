"""
FCA Cryptoasset Promotion Rules Validator
Implements FCA PS22/10 and FS23/1 (October 2023 rules)

Legal References:
- PS22/10: Strengthening our financial promotion rules for high-risk investments
- FS23/1: Financial promotion rules for cryptoassets
- COBS 4.12A-4.12C (Cryptoasset financial promotions)
- Effective from October 8, 2023
"""

import re
from typing import Dict, List


class CryptoPromotionValidator:
    """
    Validates cryptoasset promotions against FCA October 2023 rules
    """

    def __init__(self):
        self.name = "cryptoasset_promotion"
        self.legal_source = "FCA COBS 4.12A-C (Cryptoasset Promotions)"

    def check_crypto_promotion(self, text: str) -> Dict:
        """Main validation for cryptoasset promotions"""
        text_lower = text.lower()

        # First, determine if this is a crypto promotion
        if not self._is_crypto_promotion(text):
            return {
                'status': 'N/A',
                'message': 'Not a cryptoasset promotion',
                'legal_source': self.legal_source
            }

        results = {
            'risk_warning': self.check_risk_warning(text),
            'complexity_warning': self.check_complexity_warning(text),
            'no_protection_warning': self.check_no_protection_warning(text),
            'unregulated_warning': self.check_unregulated_warning(text),
            'target_restriction': self.check_target_restriction(text),
            'cooling_off': self.check_cooling_off_requirement(text),
            'direct_offer': self.check_direct_offer_restriction(text),
            'incentives_ban': self.check_incentives_ban(text)
        }

        # Count failures
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
            'message': f'Cryptoasset promotion: {len(failures)} critical issues, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings,
            'summary': f'{len(results) - len(failures) - len(warnings)} of {len(results)} requirements met'
        }

    def _is_crypto_promotion(self, text: str) -> bool:
        """Detect if this is a cryptoasset promotion"""
        crypto_terms = [
            r'\bcrypto(?:currency|asset|token)s?\b',
            r'\bbitcoin\b',
            r'\bethereum\b',
            r'\baltcoin\b',
            r'\bblockchain\s+(?:token|asset|investment)',
            r'\bdigital\s+(?:currency|asset|token)',
            r'\bdefi\b',
            r'\bnft\b',
            r'\bico\b',  # Initial Coin Offering
            r'\bsto\b',  # Security Token Offering
            r'\b(?:buy|invest|trade).*(?:crypto|bitcoin|ethereum)',
            r'\bcrypto\s+(?:exchange|platform|wallet)',
            r'\bstablecoin\b',
            r'\bweb3\b'
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in crypto_terms)

    def check_risk_warning(self, text: str) -> Dict:
        """
        Check for mandatory risk warning
        COBS 4.12B: "Don't invest unless you're prepared to lose all the money you invest"
        """
        # Exact or near-exact FCA prescribed warning
        prescribed_warning_patterns = [
            r"don'?t\s+invest\s+unless\s+you'?re\s+prepared\s+to\s+lose\s+all\s+(?:the\s+)?money\s+you\s+invest",
            r"don'?t\s+invest\s+unless\s+prepared\s+to\s+lose\s+all\s+your\s+investment",
            r"(?:could|may|might)\s+lose\s+all\s+(?:the\s+)?money\s+you\s+invest"
        ]

        has_risk_warning = False
        for pattern in prescribed_warning_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                has_risk_warning = True
                break

        if not has_risk_warning:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing mandatory cryptoasset risk warning',
                'legal_source': 'COBS 4.12B',
                'suggestion': 'Must include: "Don\'t invest unless you\'re prepared to lose all the money you invest. This is a high-risk investment and you are unlikely to be protected if something goes wrong."'
            }

        # Check if warning is prominent
        warning_position = text.lower().find("don't invest")
        if warning_position < 0:
            warning_position = text.lower().find("lose all")

        # Warning should appear in first 30% of document
        if warning_position > len(text) * 0.3:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Risk warning present but not prominent',
                'legal_source': 'COBS 4.12B',
                'suggestion': 'Risk warning must be prominent - move to beginning of promotion'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Mandatory risk warning present and prominent',
            'legal_source': 'COBS 4.12B'
        }

    def check_complexity_warning(self, text: str) -> Dict:
        """Check for complexity warning"""
        complexity_patterns = [
            r'(?:complex|difficult\s+to\s+understand)',
            r'high(?:-| )risk\s+(?:investment|asset)',
            r'speculative',
            r'(?:understand|know)\s+(?:the\s+)?risks?'
        ]

        has_complexity = any(re.search(p, text, re.IGNORECASE) for p in complexity_patterns)

        if not has_complexity:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No complexity warning',
                'legal_source': 'COBS 4.12B',
                'suggestion': 'Explain that cryptoassets are complex and high-risk'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Complexity warning present',
            'legal_source': 'COBS 4.12B'
        }

    def check_no_protection_warning(self, text: str) -> Dict:
        """
        Check for "no protection" warning
        Must state: unlikely to be protected if something goes wrong
        """
        protection_patterns = [
            r'(?:unlikely|not\s+likely)\s+to\s+be\s+protected',
            r'no\s+(?:protection|compensation|recourse)',
            r'not\s+protected\s+(?:by|under)\s+(?:fscs|financial\s+services\s+compensation)',
            r'(?:will\s+not|won\'?t)\s+be\s+protected'
        ]

        has_protection_warning = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)

        if not has_protection_warning:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing "no protection" warning',
                'legal_source': 'COBS 4.12B',
                'suggestion': 'Must state: "you are unlikely to be protected if something goes wrong"'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No protection warning present',
            'legal_source': 'COBS 4.12B'
        }

    def check_unregulated_warning(self, text: str) -> Dict:
        """Check if promotion clarifies regulatory status"""
        unregulated_patterns = [
            r'(?:not|un)regulated',
            r'(?:outside|beyond)\s+(?:fca|regulatory)\s+(?:scope|protection)',
            r'no\s+regulatory\s+oversight'
        ]

        has_regulatory_warning = any(re.search(p, text, re.IGNORECASE) for p in unregulated_patterns)

        # Also check for false regulated claims
        false_claims = [
            r'fca\s+(?:regulated|approved)',
            r'regulated\s+(?:by\s+)?fca'
        ]

        has_false_claim = any(re.search(p, text, re.IGNORECASE) for p in false_claims)

        if has_false_claim:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'False claim: cryptoassets are not FCA regulated',
                'legal_source': 'FSMA s.21 & COBS 4.12',
                'suggestion': 'Remove false regulatory claims. Cryptoassets are largely unregulated.'
            }

        if not has_regulatory_warning:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No unregulated warning',
                'legal_source': 'COBS 4.12B',
                'suggestion': 'Clarify that cryptoassets are not regulated by the FCA'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Regulatory status clarified',
            'legal_source': 'COBS 4.12B'
        }

    def check_target_restriction(self, text: str) -> Dict:
        """
        Check target audience restrictions
        Crypto can only be promoted to certain categories
        """
        restriction_patterns = [
            r'(?:certified|sophisticated)\s+investor',
            r'high\s+net\s+worth',
            r'professional\s+(?:client|investor)',
            r'restricted\s+to',
            r'only\s+(?:for|available\s+to)'
        ]

        has_restriction = any(re.search(p, text, re.IGNORECASE) for p in restriction_patterns)

        # Red flags - promoting to mass market
        mass_market_flags = [
            r'(?:anyone|everyone|all)\s+can\s+(?:invest|buy)',
            r'open\s+to\s+(?:all|public)',
            r'no\s+(?:restriction|requirement|minimum)'
        ]

        has_mass_market = any(re.search(p, text, re.IGNORECASE) for p in mass_market_flags)

        if has_mass_market:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Cryptoassets cannot be promoted to mass market',
                'legal_source': 'COBS 4.12A',
                'suggestion': 'Restrict to: certified sophisticated investors, high net worth, professionals, or existing investors'
            }

        # Check for appropriateness assessment
        assessment_patterns = [
            r'appropriateness\s+(?:test|assessment)',
            r'knowledge\s+and\s+experience\s+(?:test|check|assessment)',
            r'understand\s+the\s+risks?'
        ]

        has_assessment = any(re.search(p, text, re.IGNORECASE) for p in assessment_patterns)

        if not has_restriction and not has_assessment:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No target restriction or appropriateness assessment mentioned',
                'legal_source': 'COBS 4.12A',
                'suggestion': 'State target audience restrictions or appropriateness assessment requirement'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Target restrictions present',
            'legal_source': 'COBS 4.12A'
        }

    def check_cooling_off_requirement(self, text: str) -> Dict:
        """
        Check for 24-hour cooling-off period
        COBS 4.12C: Must wait 24 hours after risk warning before proceeding
        """
        cooling_off_patterns = [
            r'(?:24|twenty[- ]four)\s+hour',
            r'cooling[- ]off\s+period',
            r'wait\s+(?:24|one\s+day)',
            r'24[- ]hour\s+(?:delay|wait|period)',
            r'must\s+wait.*(?:day|24)'
        ]

        has_cooling_off = any(re.search(p, text, re.IGNORECASE) for p in cooling_off_patterns)

        # Red flags - immediate purchase
        immediate_flags = [
            r'(?:buy|invest)\s+now',
            r'immediate(?:ly)?\s+(?:purchase|access|invest)',
            r'instant\s+(?:access|registration)',
            r'(?:sign\s+up|register).*(?:now|today|immediately)'
        ]

        has_immediate = any(re.search(p, text, re.IGNORECASE) for p in immediate_flags)

        if has_immediate and not has_cooling_off:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing 24-hour cooling-off period',
                'legal_source': 'COBS 4.12C',
                'suggestion': 'Must impose 24-hour delay between risk warning and investment decision'
            }

        if not has_cooling_off:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No mention of cooling-off period',
                'legal_source': 'COBS 4.12C',
                'suggestion': 'Include 24-hour cooling-off period after risk warning'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': '24-hour cooling-off period mentioned',
            'legal_source': 'COBS 4.12C'
        }

    def check_direct_offer_restriction(self, text: str) -> Dict:
        """
        Check for direct offer restrictions
        Cannot directly offer cryptoassets in mass marketing
        """
        direct_offer_patterns = [
            r'(?:buy|purchase|invest).*(?:here|now|click)',
            r'(?:order|buy)\s+(?:button|link)',
            r'(?:click|tap)\s+(?:to|here).*(?:buy|invest|purchase)',
            r'(?:download|install).*(?:app|wallet).*(?:buy|invest)'
        ]

        has_direct_offer = any(re.search(p, text, re.IGNORECASE) for p in direct_offer_patterns)

        if has_direct_offer:
            # Check if appropriately restricted
            restriction_check = [
                r'(?:after|following)\s+(?:appropriateness|assessment)',
                r'(?:certified|sophisticated|professional)\s+investor',
                r'subject\s+to\s+(?:checks|assessment|verification)'
            ]

            has_restriction = any(re.search(p, text, re.IGNORECASE) for p in restriction_check)

            if not has_restriction:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Direct offer without restrictions',
                    'legal_source': 'COBS 4.12A',
                    'suggestion': 'Cannot directly offer crypto without appropriateness assessment or investor certification'
                }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Direct offer restrictions complied with',
            'legal_source': 'COBS 4.12A'
        }

    def check_incentives_ban(self, text: str) -> Dict:
        """
        Check for banned incentives
        FCA bans refer-a-friend bonuses and volume bonuses
        """
        incentive_patterns = [
            r'refer[- ]a[- ]friend',
            r'referral\s+(?:bonus|reward|benefit)',
            r'(?:bring|introduce)\s+a\s+friend',
            r'volume\s+(?:bonus|discount|benefit)',
            r'trade\s+more.*(?:bonus|benefit|reward)',
            r'(?:free|bonus)\s+(?:crypto|token|coin)',
            r'sign[- ]up\s+bonus'
        ]

        has_banned_incentive = False
        found_incentives = []

        for pattern in incentive_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                has_banned_incentive = True
                found_incentives.append(match.group())

        if has_banned_incentive:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Banned incentive detected',
                'legal_source': 'COBS 4.12A.4R',
                'suggestion': 'Remove refer-a-friend bonuses, volume bonuses, and similar incentives - explicitly banned for crypto promotions',
                'violations': found_incentives
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No banned incentives detected',
            'legal_source': 'COBS 4.12A.4R'
        }

    def get_crypto_promotion_summary(self, text: str) -> Dict:
        """Generate comprehensive crypto promotion compliance summary"""
        result = self.check_crypto_promotion(text)

        if result['status'] == 'N/A':
            return result

        # Add examples and guidance
        result['guidance'] = {
            'mandatory_warning': 'Don\'t invest unless you\'re prepared to lose all the money you invest. This is a high-risk investment and you are unlikely to be protected if something goes wrong.',
            'required_elements': [
                'Risk of losing all money',
                'High-risk investment warning',
                'No protection warning',
                'Unregulated status clarification',
                '24-hour cooling-off period',
                'Target audience restriction',
                'No banned incentives'
            ],
            'reference': 'FCA PS22/10 and COBS 4.12A-C (Effective October 8, 2023)'
        }

        return result
