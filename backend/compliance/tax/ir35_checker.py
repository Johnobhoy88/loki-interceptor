"""
IR35 Off-Payroll Working Rules Checker
Validation for IR35 compliance in contractor relationships

Legal References:
- Finance Act 2017 (Public sector rules)
- Finance Act 2021 (Private sector rules)
- ITEPA 2003, Chapter 8 (Intermediaries legislation)
- HMRC Employment Status Manual (ESM)
- CEST (Check Employment Status for Tax) criteria

2024/25 Rules:
- Medium/large private sector clients responsible for status determination
- Small company exemption still applies
- Status Determination Statement (SDS) required
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional


class IR35Checker:
    """IR35 off-payroll working rules checker"""

    # Small company thresholds (2 of 3 criteria)
    SMALL_COMPANY_TURNOVER = Decimal('10200000.00')
    SMALL_COMPANY_ASSETS = Decimal('5100000.00')
    SMALL_COMPANY_EMPLOYEES = 50

    def __init__(self):
        self.legal_source = "FA 2017/2021; ITEPA 2003, Chapter 8"

    def assess_control(self, text: str) -> Dict:
        """
        Assess control indicators (key IR35 factor)

        Reference: ESM0522 (Control test)
        """
        control_indicators = []
        text_lower = text.lower()

        # Control indicators (suggesting employment)
        employment_indicators = [
            (r'must\s+work\s+(?:specific|set)\s+hours', 'Fixed working hours'),
            (r'supervised|line\s+manager|report\s+to', 'Supervision'),
            (r'client\s+(?:direct|control|instruct|manage)', 'Client direction'),
            (r'cannot\s+(?:substitute|send\s+someone)', 'No substitution right'),
            (r'must\s+work\s+at\s+client\s+premises', 'Location control'),
            (r'client\s+provides\s+equipment', 'Equipment provided'),
        ]

        # Self-employment indicators
        self_employment_indicators = [
            (r'control\s+(?:how|when|where).*work', 'Contractor controls work method'),
            (r'right\s+(?:of\s+)?substitution', 'Substitution rights'),
            (r'own\s+equipment', 'Provides own equipment'),
            (r'multiple\s+clients', 'Multiple clients'),
            (r'business\s+risk', 'Takes business risk'),
        ]

        employment_score = 0
        self_employment_score = 0

        for pattern, indicator in employment_indicators:
            if re.search(pattern, text_lower):
                employment_score += 1
                control_indicators.append({
                    'type': 'employment_indicator',
                    'indicator': indicator,
                    'direction': 'employment'
                })

        for pattern, indicator in self_employment_indicators:
            if re.search(pattern, text_lower):
                self_employment_score += 1
                control_indicators.append({
                    'type': 'self_employment_indicator',
                    'indicator': indicator,
                    'direction': 'self_employment'
                })

        # Assessment
        if employment_score > self_employment_score + 1:
            assessment = 'likely_inside_ir35'
            risk = 'high'
        elif self_employment_score > employment_score + 1:
            assessment = 'likely_outside_ir35'
            risk = 'low'
        else:
            assessment = 'borderline'
            risk = 'medium'

        return {
            'control_assessment': assessment,
            'risk_level': risk,
            'employment_indicators': employment_score,
            'self_employment_indicators': self_employment_score,
            'indicators_found': control_indicators,
            'legal_reference': 'ESM0522'
        }

    def assess_substitution(self, text: str) -> Dict:
        """
        Assess right of substitution (key IR35 factor)

        Reference: ESM0531 (Substitution test)
        """
        text_lower = text.lower()

        # Strong substitution indicators
        has_unrestricted_right = re.search(
            r'(?:unrestricted|unfettered).*substitut|substitut.*without.*(?:approval|consent)',
            text_lower
        )

        has_conditional_right = re.search(
            r'substitut.*(?:with|subject\s+to).*approval|client\s+approval.*substitut',
            text_lower
        )

        no_substitution = re.search(
            r'(?:no|cannot|must\s+not|prohibited).*substitut|must\s+(?:personally|you)\s+perform',
            text_lower
        )

        if no_substitution:
            return {
                'substitution_right': 'none',
                'ir35_impact': 'strongly_suggests_employment',
                'risk_level': 'high',
                'note': 'Personal service requirement indicates employment',
                'legal_reference': 'ESM0531'
            }
        elif has_unrestricted_right:
            return {
                'substitution_right': 'unrestricted',
                'ir35_impact': 'suggests_self_employment',
                'risk_level': 'low',
                'note': 'Genuine unfettered substitution right indicates self-employment',
                'legal_reference': 'ESM0531'
            }
        elif has_conditional_right:
            return {
                'substitution_right': 'conditional',
                'ir35_impact': 'weak_indicator',
                'risk_level': 'medium',
                'note': 'Conditional substitution has limited weight',
                'legal_reference': 'ESM0531'
            }
        else:
            return {
                'substitution_right': 'unclear',
                'ir35_impact': 'needs_clarification',
                'risk_level': 'medium',
                'note': 'Substitution rights should be clearly stated',
                'legal_reference': 'ESM0531'
            }

    def assess_mutuality_of_obligation(self, text: str) -> Dict:
        """
        Assess mutuality of obligation (key IR35 factor)

        Reference: ESM0540 (MOO test)
        """
        text_lower = text.lower()

        # MOO indicators
        obligation_to_provide_work = re.search(
            r'(?:must|obliged\s+to).*(?:provide|offer)\s+work',
            text_lower
        )

        obligation_to_accept_work = re.search(
            r'(?:must|obliged\s+to).*accept.*work',
            text_lower
        )

        project_basis = re.search(
            r'project\s+basis|specific\s+assignment|no\s+ongoing\s+obligation',
            text_lower
        )

        if obligation_to_provide_work and obligation_to_accept_work:
            return {
                'mutuality_of_obligation': 'present',
                'ir35_impact': 'suggests_employment',
                'risk_level': 'high',
                'note': 'Mutual obligations indicate employment relationship',
                'legal_reference': 'ESM0540'
            }
        elif project_basis:
            return {
                'mutuality_of_obligation': 'minimal',
                'ir35_impact': 'suggests_self_employment',
                'risk_level': 'low',
                'note': 'Project-based work with no ongoing obligations indicates self-employment',
                'legal_reference': 'ESM0540'
            }
        else:
            return {
                'mutuality_of_obligation': 'unclear',
                'ir35_impact': 'needs_clarification',
                'risk_level': 'medium',
                'note': 'Mutuality of obligation should be clarified',
                'legal_reference': 'ESM0540'
            }

    def validate_sds_requirements(self, text: str) -> Dict:
        """
        Validate Status Determination Statement requirements

        Reference: FA 2021, s15; SI 2017/1015, Reg 13B
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'medium' not in text_lower and 'large' not in text_lower:
            return {'applicable': False}

        # Check for SDS mention
        sds_mentioned = re.search(
            r'status\s+determination|sds|employment\s+status\s+(?:statement|determination)',
            text_lower
        )

        if not sds_mentioned:
            issues.append({
                'type': 'sds_not_mentioned',
                'severity': 'critical',
                'message': 'Status Determination Statement (SDS) requirement not mentioned',
                'requirement': 'Medium/large clients must provide SDS before contract starts',
                'legal_reference': 'FA 2021, s15; SI 2017/1015, Reg 13B'
            })

        # Check for SDS content requirements
        sds_elements = {
            'status_conclusion': r'inside\s+ir35|outside\s+ir35|employment\s+status',
            'reasons': r'reason|rationale|because|due\s+to',
            'right_to_disagree': r'disagree|challenge|dispute',
        }

        if sds_mentioned:
            missing_elements = []
            for element, pattern in sds_elements.items():
                if not re.search(pattern, text_lower):
                    missing_elements.append(element)

            if missing_elements:
                warnings.append({
                    'type': 'incomplete_sds',
                    'severity': 'high',
                    'message': 'SDS requirements incomplete',
                    'missing_elements': missing_elements,
                    'required_content': [
                        'Employment status conclusion',
                        'Reasons for determination',
                        'Right to disagree process'
                    ],
                    'legal_reference': 'SI 2017/1015, Reg 13B'
                })

        # Check for small company exemption mention
        if 'small' in text_lower and 'company' in text_lower:
            if not re.search(r'exempt|does\s+not\s+apply|outside\s+scope', text_lower):
                warnings.append({
                    'type': 'small_company_exemption_unclear',
                    'severity': 'medium',
                    'message': 'Small company IR35 exemption should be clarified',
                    'note': 'Small companies exempt from off-payroll rules',
                    'legal_reference': 'FA 2021, s15(10)'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_deemed_payment(self, text: str) -> Dict:
        """
        Validate deemed payment calculation references

        Reference: ITEPA 2003, s61N
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'inside ir35' not in text_lower and 'deemed payment' not in text_lower:
            return {'applicable': False}

        # Check for deemed payment calculation
        if not re.search(r'deemed\s+payment|deem(?:ed)?\s+employment', text_lower):
            warnings.append({
                'type': 'deemed_payment_not_mentioned',
                'severity': 'high',
                'message': 'Deemed payment calculation not mentioned',
                'note': 'If inside IR35, deemed payment calculation applies',
                'legal_reference': 'ITEPA 2003, s61N'
            })

        # Check for tax/NIC treatment
        if 'inside ir35' in text_lower:
            if not re.search(r'(?:paye|income\s+tax).*(?:national\s+insurance|nic)', text_lower):
                warnings.append({
                    'type': 'tax_nic_treatment_missing',
                    'severity': 'medium',
                    'message': 'Tax and NIC treatment not specified',
                    'note': 'Inside IR35: taxed as employment income with PAYE and NIC',
                    'legal_reference': 'ITEPA 2003, s61N'
                })

        # Check for 5% expense allowance
        if 'deemed payment' in text_lower or 'inside ir35' in text_lower:
            if not re.search(r'5\s*%|five\s+percent', text_lower):
                warnings.append({
                    'type': 'expense_allowance_not_mentioned',
                    'severity': 'low',
                    'message': '5% expense allowance not mentioned',
                    'note': '5% flat rate expense allowance for deemed payments',
                    'legal_reference': 'ITEPA 2003, s61N(5)'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_ir35_check(self, text: str) -> Dict:
        """
        Run comprehensive IR35 compliance check
        """
        results = {
            'control_assessment': self.assess_control(text),
            'substitution_assessment': self.assess_substitution(text),
            'moo_assessment': self.assess_mutuality_of_obligation(text),
            'sds_validation': self.validate_sds_requirements(text),
            'deemed_payment_validation': self.validate_deemed_payment(text)
        }

        all_issues = []
        all_warnings = []

        for check_name, check_result in results.items():
            if 'issues' in check_result:
                all_issues.extend(check_result['issues'])
            if 'warnings' in check_result:
                all_warnings.extend(check_result['warnings'])

        # Overall IR35 risk assessment
        control_risk = results['control_assessment'].get('risk_level', 'medium')
        substitution_risk = results['substitution_assessment'].get('risk_level', 'medium')
        moo_risk = results['moo_assessment'].get('risk_level', 'medium')

        risk_scores = {'low': 1, 'medium': 2, 'high': 3}
        avg_risk_score = (
            risk_scores.get(control_risk, 2) +
            risk_scores.get(substitution_risk, 2) +
            risk_scores.get(moo_risk, 2)
        ) / 3

        if avg_risk_score <= 1.5:
            overall_assessment = 'likely_outside_ir35'
        elif avg_risk_score >= 2.5:
            overall_assessment = 'likely_inside_ir35'
        else:
            overall_assessment = 'borderline_case'

        return {
            'overall_assessment': overall_assessment,
            'overall_valid': len(all_issues) == 0,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings),
            'detailed_results': results,
            'all_issues': all_issues,
            'all_warnings': all_warnings,
            'recommendation': 'Use HMRC CEST tool for formal determination',
            'legal_source': self.legal_source
        }
