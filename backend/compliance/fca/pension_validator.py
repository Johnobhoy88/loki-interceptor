"""
FCA Pension Transfer Validation Module
Implements FCA pension transfer safeguards and warnings

Legal References:
- COBS 19.1 (Pension transfers, conversions and opt-outs)
- COBS 19.3 (Pension transfer specialist advice)
- PS17/16: Pension transfer advice
- PS20/6: British Steel Pension Scheme
"""

import re
from typing import Dict, List


class PensionTransferValidator:
    """
    Validates pension transfer documents and advice
    Critical safeguards for defined benefit pension transfers
    """

    def __init__(self):
        self.name = "pension_transfer_validator"
        self.legal_source = "FCA COBS 19.1 & 19.3"

    def check_pension_transfer(self, text: str) -> Dict:
        """Main pension transfer validation"""
        text_lower = text.lower()

        # Determine if this discusses pension transfers
        if not self._is_pension_transfer_doc(text):
            return {
                'status': 'N/A',
                'message': 'Not a pension transfer document',
                'legal_source': self.legal_source
            }

        results = {
            'starting_assumption': self.check_starting_assumption(text),
            'transfer_value_analysis': self.check_transfer_value_analysis(text),
            'death_benefits': self.check_death_benefits(text),
            'safeguarded_benefits': self.check_safeguarded_benefits(text),
            'specialist_requirement': self.check_specialist_requirement(text),
            'high_risk_warning': self.check_high_risk_investment_warning(text),
            'scam_warning': self.check_scam_warning(text),
            'tvas_requirement': self.check_tvas_requirement(text)
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
            'message': f'Pension transfer: {len(failures)} critical issues, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings
        }

    def _is_pension_transfer_doc(self, text: str) -> bool:
        """Detect if this is a pension transfer document"""
        pension_terms = [
            r'pension\s+transfer',
            r'defined\s+benefit',
            r'\bdb\s+pension\b',
            r'final\s+salary',
            r'safeguarded\s+benefits',
            r'transfer\s+value',
            r'cet[vx]\b',  # Cash Equivalent Transfer Value
            r'pension\s+(?:opt[- ]out|conversion)',
            r'transfer.*(?:to\s+)?(?:dc|defined\s+contribution)',
            r'sipp\s+transfer',
            r'qrops'  # Qualifying Recognised Overseas Pension Scheme
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in pension_terms)

    def check_starting_assumption(self, text: str) -> Dict:
        """
        Check for "starting assumption" statement
        COBS 19.1: Presumption that transfer is NOT suitable
        """
        starting_assumption_patterns = [
            r'starting\s+assumption',
            r'presume(?:d)?\s+(?:not\s+)?(?:in\s+your\s+)?(?:best\s+)?interest',
            r'assume.*transfer.*not\s+suitable',
            r'transfer.*(?:unlikely|not\s+expected)\s+to\s+be\s+suitable',
            r'default\s+(?:position|assumption).*(?:not\s+)?transfer'
        ]

        has_starting_assumption = any(re.search(p, text, re.IGNORECASE) for p in starting_assumption_patterns)

        # Check if it's a DB transfer (requires starting assumption)
        is_db_transfer = bool(re.search(r'(?:defined\s+benefit|db|final\s+salary|safeguarded)', text, re.IGNORECASE))

        if is_db_transfer and not has_starting_assumption:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Missing "starting assumption" for DB pension transfer',
                'legal_source': 'COBS 19.1.6G',
                'suggestion': 'Must state: starting assumption is that a DB transfer is unlikely to be in the client\'s best interests'
            }

        return {
            'status': 'PASS' if has_starting_assumption else 'N/A',
            'severity': 'none',
            'message': 'Starting assumption stated' if has_starting_assumption else 'Not DB transfer',
            'legal_source': 'COBS 19.1.6G'
        }

    def check_transfer_value_analysis(self, text: str) -> Dict:
        """Check for transfer value analysis (TVA/TVAS)"""
        tva_patterns = [
            r'transfer\s+value\s+(?:analysis|assessment|comparison)',
            r'\btva(?:s)?\b',
            r'(?:compare|comparison).*(?:transfer\s+value|benefits)',
            r'critical\s+yield',
            r'(?:equivalent|comparative)\s+(?:value|benefit)'
        ]

        has_tva = any(re.search(p, text, re.IGNORECASE) for p in tva_patterns)

        # Check for benefits comparison
        comparison_elements = [
            r'guaranteed\s+(?:income|benefits)',
            r'inflation\s+(?:protection|link|adjustment)',
            r'survivor(?:\'?s)?\s+(?:benefits|pension)',
            r'scheme\s+(?:protection|security)',
            r'transfer\s+value.*£[\d,]+'
        ]

        comparison_count = sum(1 for p in comparison_elements if re.search(p, text, re.IGNORECASE))

        if not has_tva and comparison_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No comprehensive transfer value analysis',
                'legal_source': 'COBS 19.1',
                'suggestion': 'Must provide TVAS comparing: guaranteed income, inflation protection, death benefits, scheme security'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Transfer value analysis present',
            'legal_source': 'COBS 19.1'
        }

    def check_death_benefits(self, text: str) -> Dict:
        """Check death benefits comparison"""
        death_benefit_patterns = [
            r'death\s+benefit',
            r'survivor(?:\'?s)?\s+(?:benefit|pension)',
            r'widow(?:er)?(?:\'?s)?\s+pension',
            r'dependant(?:\'?s)?\s+(?:benefit|pension)',
            r'beneficiar(?:y|ies)',
            r'(?:if|when)\s+you\s+die'
        ]

        has_death_benefits = any(re.search(p, text, re.IGNORECASE) for p in death_benefit_patterns)

        if not has_death_benefits:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No death benefits discussion',
                'legal_source': 'COBS 19.1',
                'suggestion': 'Must compare death benefits between DB scheme and proposed transfer destination'
            }

        # Check if comparison is made
        comparison_indicators = [
            r'(?:compared|comparison|versus|vs\.?).*death',
            r'death.*(?:db|defined\s+benefit|scheme).*(?:sipp|dc|personal\s+pension)',
            r'(?:better|worse|higher|lower).*death\s+benefit'
        ]

        has_comparison = any(re.search(p, text, re.IGNORECASE) for p in comparison_indicators)

        if not has_comparison:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Death benefits mentioned but not compared',
                'legal_source': 'COBS 19.1',
                'suggestion': 'Compare death benefits: DB scheme guaranteed vs DC pot residual value'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Death benefits compared',
            'legal_source': 'COBS 19.1'
        }

    def check_safeguarded_benefits(self, text: str) -> Dict:
        """Check explanation of safeguarded benefits"""
        safeguarded_patterns = [
            r'safeguarded\s+benefit',
            r'guaranteed\s+(?:for\s+)?life',
            r'guarantee(?:d)?\s+(?:income|payment|pension)',
            r'index[- ]linked',
            r'inflation\s+(?:protection|linked|adjusted)',
            r'pension\s+protection\s+fund',
            r'\bppf\b'
        ]

        safeguarded_count = sum(1 for p in safeguarded_patterns if re.search(p, text, re.IGNORECASE))

        if safeguarded_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Insufficient explanation of safeguarded benefits',
                'legal_source': 'COBS 19.1',
                'suggestion': 'Explain safeguarded benefits: guaranteed income, inflation protection, PPF protection, survivor benefits'
            }

        # Check for risk of losing benefits
        loss_warning_patterns = [
            r'(?:lose|losing|give\s+up).*(?:benefit|guarantee|protection)',
            r'no\s+longer\s+(?:have|receive).*guarantee',
            r'transfer.*means.*(?:lose|losing)',
            r'irrevocable',
            r'cannot\s+(?:be\s+)?(?:reversed|undone)'
        ]

        has_loss_warning = any(re.search(p, text, re.IGNORECASE) for p in loss_warning_patterns)

        if not has_loss_warning:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No clear warning about losing safeguarded benefits',
                'legal_source': 'COBS 19.1',
                'suggestion': 'Clearly warn: transferring means permanently giving up guaranteed benefits'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Safeguarded benefits explained with loss warning',
            'legal_source': 'COBS 19.1'
        }

    def check_specialist_requirement(self, text: str) -> Dict:
        """
        Check pension transfer specialist requirement
        Transfers >£30k from DB require specialist advice
        """
        specialist_patterns = [
            r'pension\s+transfer\s+specialist',
            r'\bpts\b',
            r'specialist\s+(?:advice|adviser|qualification)',
            r'af3\b',  # Pension Transfer Specialist qualification
            r'specialist.*(?:qualified|authorised)'
        ]

        has_specialist = any(re.search(p, text, re.IGNORECASE) for p in specialist_patterns)

        # Check transfer value
        value_match = re.search(r'£([\d,]+)k?', text, re.IGNORECASE)
        transfer_value = 0
        if value_match:
            value_str = value_match.group(1).replace(',', '')
            transfer_value = float(value_str)
            if 'k' in value_match.group(0).lower():
                transfer_value *= 1000

        # Check if DB/safeguarded benefits
        is_db_transfer = bool(re.search(r'(?:defined\s+benefit|db|safeguarded\s+benefit)', text, re.IGNORECASE))

        if is_db_transfer and transfer_value >= 30000 and not has_specialist:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'DB transfer ≥£30k requires pension transfer specialist',
                'legal_source': 'COBS 19.1.1R',
                'suggestion': 'Advice must be provided by FCA registered Pension Transfer Specialist (AF3 qualified)'
            }

        return {
            'status': 'PASS' if has_specialist or not is_db_transfer else 'N/A',
            'severity': 'none',
            'message': 'Specialist requirement met' if has_specialist else 'Not applicable',
            'legal_source': 'COBS 19.1.1R'
        }

    def check_high_risk_investment_warning(self, text: str) -> Dict:
        """Check for high-risk investment warnings post-transfer"""
        high_risk_indicators = [
            r'(?:high[- ]risk|speculative)\s+investment',
            r'(?:unregulated|overseas|exotic)\s+investment',
            r'(?:storage\s+pod|parking|hotel\s+room|care\s+home)\s+investment',
            r'(?:crypto|bitcoin)',
            r'(?:sto|carbon\s+credit|renewable\s+energy\s+bond)',
            r'(?:guarante|promise)(?:d)?\s+(?:return|yield).*\d+%'
        ]

        has_high_risk = any(re.search(p, text, re.IGNORECASE) for p in high_risk_indicators)

        if has_high_risk:
            # Check for warnings
            warning_patterns = [
                r'(?:high|significant)\s+risk',
                r'(?:could|may|might)\s+lose\s+(?:all|entire|whole)',
                r'not\s+(?:suitable|appropriate)\s+for\s+pension',
                r'(?:warning|caution|alert)'
            ]

            has_warning = any(re.search(p, text, re.IGNORECASE) for p in warning_patterns)

            if not has_warning:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'High-risk investments mentioned without adequate warnings',
                    'legal_source': 'COBS 19.1 & Consumer Duty',
                    'suggestion': 'Pension funds should not be invested in high-risk, unregulated investments. Clear warnings required.'
                }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No high-risk investment concerns',
            'legal_source': 'COBS 19.1'
        }

    def check_scam_warning(self, text: str) -> Dict:
        """Check for pension scam warnings"""
        scam_warning_patterns = [
            r'pension\s+scam',
            r'(?:free|complimentary)\s+pension\s+review',
            r'(?:unlock|release|liberate|free\s+up)\s+(?:your\s+)?(?:pension|cash)',
            r'(?:warning|alert|beware).*scam',
            r'too\s+good\s+to\s+be\s+true',
            r'(?:unexpected|unsolicited)\s+(?:contact|approach|offer)',
            r'pension\s+(?:wise|guidance)'
        ]

        has_scam_warning = any(re.search(p, text, re.IGNORECASE) for p in scam_warning_patterns)

        # Red flags for scams
        scam_red_flags = [
            r'(?:time[- ]limited|limited\s+time)\s+offer',
            r'act\s+(?:now|quickly|fast)',
            r'(?:upfront|advance)\s+fee',
            r'transfer.*(?:urgently|immediately|quickly)',
            r'(?:guaranteed|promise).*(?:high|exceptional)\s+return',
            r'(?:access|withdraw).*before\s+(?:55|age\s+55)'
        ]

        has_red_flags = any(re.search(p, text, re.IGNORECASE) for p in scam_red_flags)

        if has_red_flags and not has_scam_warning:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Pension scam red flags detected without warnings',
                'legal_source': 'FCA Pension Scam Guidance',
                'suggestion': 'Document contains pension scam indicators. Include warnings about pension scams and refer to Pension Wise.'
            }

        if not has_scam_warning:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No pension scam warning',
                'legal_source': 'FCA Pension Scam Guidance',
                'suggestion': 'Include warning about pension scams and direct to Pension Wise (gov.uk/pension-wise)'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Pension scam warnings present',
            'legal_source': 'FCA Pension Scam Guidance'
        }

    def check_tvas_requirement(self, text: str) -> Dict:
        """Check Transfer Value Analysis System (TVAS) requirement"""
        tvas_patterns = [
            r'tvas\b',
            r'transfer\s+value\s+(?:analysis|comparison)\s+system',
            r'appropriate\s+pension\s+transfer\s+analysis',
            r'\bapta\b'
        ]

        has_tvas = any(re.search(p, text, re.IGNORECASE) for p in tvas_patterns)

        # Critical yield is key TVAS output
        critical_yield_patterns = [
            r'critical\s+yield',
            r'growth\s+rate.*(?:required|needed|necessary)',
            r'\d+\.?\d*%\s+(?:per\s+)?(?:annum|year|pa)'
        ]

        has_critical_yield = any(re.search(p, text, re.IGNORECASE) for p in critical_yield_patterns)

        is_db_transfer = bool(re.search(r'(?:defined\s+benefit|db|safeguarded)', text, re.IGNORECASE))

        if is_db_transfer and not (has_tvas or has_critical_yield):
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'DB transfer requires TVAS/APTA',
                'legal_source': 'COBS 19.1.2R',
                'suggestion': 'Must provide Transfer Value Analysis System (TVAS) or Appropriate Pension Transfer Analysis (APTA) including critical yield'
            }

        return {
            'status': 'PASS' if (has_tvas or has_critical_yield) else 'N/A',
            'severity': 'none',
            'message': 'TVAS/APTA present' if has_tvas or has_critical_yield else 'Not required',
            'legal_source': 'COBS 19.1.2R'
        }
