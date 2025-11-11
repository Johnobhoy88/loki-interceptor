"""
Self-Assessment Tax Return Validator
Validation for Self-Assessment tax return compliance

Legal References:
- Taxes Management Act 1970 (TMA 1970)
- Income Tax Act 2007 (ITA 2007)
- HMRC Self Assessment Manual (SAM)
- Finance Act 2024

2024/25 Key Dates:
- Registration deadline: 5 October 2025
- Paper return deadline: 31 October 2025
- Online return deadline: 31 January 2026
- Payment deadline: 31 January 2026
- Second payment on account: 31 July 2026
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional


class SelfAssessmentValidator:
    """Self-Assessment tax return compliance validator"""

    # Key deadlines (for 2024/25 tax year)
    REGISTRATION_DEADLINE = date(2025, 10, 5)
    PAPER_DEADLINE = date(2025, 10, 31)
    ONLINE_DEADLINE = date(2026, 1, 31)
    PAYMENT_DEADLINE = date(2026, 1, 31)
    PAYMENT_ON_ACCOUNT_1 = date(2026, 1, 31)
    PAYMENT_ON_ACCOUNT_2 = date(2026, 7, 31)

    # Registration requirements
    REGISTRATION_THRESHOLDS = {
        'self_employed': Decimal('1000.00'),  # Trading allowance
        'rental_income': Decimal('1000.00'),  # Property allowance
        'untaxed_income': Decimal('2500.00'),
        'taxable_income': Decimal('100000.00'),  # High earners
    }

    def __init__(self):
        self.legal_source = "TMA 1970; ITA 2007; Finance Act 2024"

    def validate_registration_requirement(self, text: str) -> Dict:
        """
        Validate Self-Assessment registration requirements

        Reference: TMA 1970, s7
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for self-employment
        if re.search(r'self[-\s]employe|sole\s+trader|freelanc', text_lower):
            if not re.search(r'register|hmrc|self\s+assessment|sa', text_lower):
                warnings.append({
                    'type': 'sa_registration_required',
                    'severity': 'high',
                    'message': 'Self-employed individuals must register for Self-Assessment',
                    'deadline': '5 October after tax year end',
                    'legal_reference': 'TMA 1970, s7'
                })

        # Check for rental income
        if re.search(r'rental\s+income|property\s+income|letting', text_lower):
            if not re.search(r'property\s+allowance|£1,?000', text_lower):
                warnings.append({
                    'type': 'property_allowance_info',
                    'severity': 'medium',
                    'message': 'Property allowance (£1,000) available for rental income',
                    'note': 'If income exceeds £1,000, SA registration may be required',
                    'legal_reference': 'ITA 2007, s783A'
                })

        # Check for high earners (£100k+)
        if re.search(r'£\s*1[0-9]{2},?000|over\s+£100,?000', text_lower):
            if not re.search(r'self\s+assessment|tax\s+return', text_lower):
                warnings.append({
                    'type': 'high_earner_sa_required',
                    'severity': 'high',
                    'message': 'Individuals with income over £100,000 must complete Self-Assessment',
                    'reason': 'Personal allowance tapers between £100,000-£125,140',
                    'legal_reference': 'TMA 1970, s7; ITA 2007, s35'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_filing_deadlines(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Validate Self-Assessment filing deadlines

        Reference: TMA 1970, s8
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for incorrect deadline mentions
        deadline_patterns = {
            'registration': (r'register.*by.*(\d{1,2})\s+(january|october|november)', '5 October'),
            'paper_return': (r'paper.*return.*by.*(\d{1,2})\s+(january|october|november)', '31 October'),
            'online_return': (r'online.*return.*by.*(\d{1,2})\s+(january|february|march)', '31 January'),
            'payment': (r'payment.*due.*(\d{1,2})\s+(january|february|march)', '31 January and 31 July'),
        }

        for deadline_type, (pattern, correct_deadline) in deadline_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                day = match.group(1)
                month = match.group(2)

                # Validate specific deadlines
                if deadline_type == 'registration' and not (day == '5' and month == 'october'):
                    issues.append({
                        'type': f'incorrect_{deadline_type}_deadline',
                        'severity': 'high',
                        'stated_deadline': f'{day} {month}',
                        'correct_deadline': correct_deadline,
                        'message': f'Incorrect registration deadline: should be {correct_deadline}',
                        'legal_reference': 'TMA 1970, s7(1)'
                    })

                elif deadline_type == 'paper_return' and not (day == '31' and month == 'october'):
                    issues.append({
                        'type': f'incorrect_{deadline_type}_deadline',
                        'severity': 'high',
                        'stated_deadline': f'{day} {month}',
                        'correct_deadline': correct_deadline,
                        'message': f'Incorrect paper return deadline: should be {correct_deadline}',
                        'legal_reference': 'TMA 1970, s8(1D)'
                    })

                elif deadline_type == 'online_return' and not (day == '31' and month == 'january'):
                    issues.append({
                        'type': f'incorrect_{deadline_type}_deadline',
                        'severity': 'high',
                        'stated_deadline': f'{day} {month}',
                        'correct_deadline': correct_deadline,
                        'message': f'Incorrect online return deadline: should be {correct_deadline}',
                        'legal_reference': 'TMA 1970, s8(1E)'
                    })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'correct_deadlines': {
                'registration': '5 October',
                'paper_return': '31 October',
                'online_return': '31 January',
                'payment': '31 January'
            }
        }

    def validate_payment_on_account(self, text: str) -> Dict:
        """
        Validate Payment on Account information

        Reference: TMA 1970, s59A
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'payment on account' not in text_lower and 'poa' not in text_lower:
            return {'applicable': False}

        # Check for payment dates
        if not re.search(r'31\s+january.*31\s+july|two\s+payment', text_lower):
            warnings.append({
                'type': 'poa_dates_unclear',
                'severity': 'medium',
                'message': 'Payment on Account dates not specified',
                'clarification': 'POA payments due 31 January and 31 July',
                'legal_reference': 'TMA 1970, s59A(2)'
            })

        # Check for POA calculation explanation
        if not re.search(r'50%|half|previous\s+year', text_lower):
            warnings.append({
                'type': 'poa_calculation_unclear',
                'severity': 'medium',
                'message': 'Payment on Account calculation not explained',
                'clarification': 'Each POA is 50% of previous year\'s tax bill',
                'legal_reference': 'TMA 1970, s59A(3)'
            })

        # Check for POA exemption mention
        if re.search(r'exempt|not\s+required|do\s+not\s+pay', text_lower):
            if not re.search(r'£1,?000|80%|paye', text_lower):
                warnings.append({
                    'type': 'poa_exemption_incomplete',
                    'severity': 'medium',
                    'message': 'POA exemption criteria not fully explained',
                    'clarification': 'No POA if: (1) last year\'s tax under £1,000, or (2) 80%+ paid via PAYE',
                    'legal_reference': 'TMA 1970, s59A(4)'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_penalties(self, text: str) -> Dict:
        """
        Validate penalty information

        Reference: FA 2009, Schedule 55-56
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'penalt' not in text_lower and 'fine' not in text_lower:
            return {'applicable': False}

        # Late filing penalties
        if re.search(r'late.*(?:filing|return)', text_lower):
            penalty_structure = {
                '£100': r'£\s*100',
                '£10/day': r'£\s*10.*(?:per\s+)?day',
                '5%': r'5\s*%',
                '£300': r'£\s*300'
            }

            mentioned_penalties = []
            for penalty, pattern in penalty_structure.items():
                if re.search(pattern, text_lower):
                    mentioned_penalties.append(penalty)

            if len(mentioned_penalties) < 2 and 'late' in text_lower:
                warnings.append({
                    'type': 'incomplete_penalty_info',
                    'severity': 'medium',
                    'message': 'Late filing penalty structure incomplete',
                    'complete_structure': [
                        '£100 - 1 day late',
                        '£10/day - 3 months late (max £900)',
                        '£300 or 5% of tax - 6 months late',
                        '£300 or 5% of tax - 12 months late'
                    ],
                    'legal_reference': 'FA 2009, Schedule 55, Para 3-6'
                })

        # Late payment penalties
        if re.search(r'late.*payment', text_lower):
            if not re.search(r'30\s+days|5\s*%', text_lower):
                warnings.append({
                    'type': 'late_payment_penalty_info',
                    'severity': 'medium',
                    'message': 'Late payment penalty rates not specified',
                    'clarification': '5% at 30 days, 5% at 6 months, 5% at 12 months',
                    'legal_reference': 'FA 2009, Schedule 56, Para 3'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_allowances_and_reliefs(self, text: str) -> Dict:
        """
        Validate tax allowances and reliefs mentions

        Reference: ITA 2007, various sections
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Trading allowance
        if re.search(r'trading\s+allowance', text_lower):
            if not re.search(r'£1,?000', text_lower):
                issues.append({
                    'type': 'trading_allowance_amount_missing',
                    'severity': 'medium',
                    'message': 'Trading allowance amount not specified',
                    'correct_amount': '£1,000',
                    'legal_reference': 'ITA 2007, s783A'
                })

        # Property allowance
        if re.search(r'property\s+allowance', text_lower):
            if not re.search(r'£1,?000', text_lower):
                issues.append({
                    'type': 'property_allowance_amount_missing',
                    'severity': 'medium',
                    'message': 'Property allowance amount not specified',
                    'correct_amount': '£1,000',
                    'legal_reference': 'ITA 2007, s783A'
                })

        # Marriage Allowance
        if re.search(r'marriage\s+allowance', text_lower):
            if not re.search(r'£1,?260|10%', text_lower):
                warnings.append({
                    'type': 'marriage_allowance_details',
                    'severity': 'low',
                    'message': 'Marriage Allowance amount not specified',
                    'clarification': '£1,260 (10% of Personal Allowance) transferable to spouse',
                    'legal_reference': 'ITA 2007, s55A-55E'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_sa_check(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Run comprehensive Self-Assessment compliance check
        """
        results = {
            'registration': self.validate_registration_requirement(text),
            'deadlines': self.validate_filing_deadlines(text, tax_year),
            'payment_on_account': self.validate_payment_on_account(text),
            'penalties': self.validate_penalties(text),
            'allowances_reliefs': self.validate_allowances_and_reliefs(text)
        }

        all_issues = []
        all_warnings = []

        for check_name, check_result in results.items():
            if 'issues' in check_result:
                all_issues.extend(check_result['issues'])
            if 'warnings' in check_result:
                all_warnings.extend(check_result['warnings'])

        return {
            'overall_valid': len(all_issues) == 0,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings),
            'detailed_results': results,
            'all_issues': all_issues,
            'all_warnings': all_warnings,
            'legal_source': self.legal_source
        }
