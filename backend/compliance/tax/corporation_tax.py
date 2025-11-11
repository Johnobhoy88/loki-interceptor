"""
Corporation Tax Validator
Comprehensive Corporation Tax compliance validation for UK companies

Legal References:
- Corporation Tax Act 2009
- Corporation Tax Act 2010
- Finance Act 2024
- HMRC Corporation Tax Manual (CTM)

2024/25 Rates:
- Main rate: 25% (profits over £250,000)
- Small profits rate: 19% (profits up to £50,000)
- Marginal relief: Between £50,000 and £250,000
- Financial year runs: 1 April to 31 March
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple


class CorporationTaxValidator:
    """Corporation Tax computation and compliance validator"""

    # 2024/25 rates and thresholds
    MAIN_RATE = Decimal('25.00')  # From April 2023
    SMALL_PROFITS_RATE = Decimal('19.00')
    LOWER_LIMIT = Decimal('50000.00')
    UPPER_LIMIT = Decimal('250000.00')

    # Marginal relief fraction
    MARGINAL_RELIEF_FRACTION = Decimal('3') / Decimal('200')

    # Historical rates for validation
    HISTORICAL_RATES = {
        '2024/25': {'main': Decimal('25.00'), 'small': Decimal('19.00')},
        '2023/24': {'main': Decimal('25.00'), 'small': Decimal('19.00')},
        '2022/23': {'main': Decimal('19.00'), 'small': Decimal('19.00')},
        '2021/22': {'main': Decimal('19.00'), 'small': Decimal('19.00')},
    }

    # Allowable deductions categories
    ALLOWABLE_EXPENSES = [
        'employee_costs',
        'premises_costs',
        'travel_costs',
        'stock_inventory',
        'legal_professional_fees',
        'marketing',
        'phone_internet',
        'finance_charges',
        'depreciation_allowances',
        'research_development'
    ]

    # Non-allowable expenses
    NON_ALLOWABLE_EXPENSES = [
        'entertaining',
        'tax_penalties',
        'legal_costs_capital',
        'political_donations',
        'depreciation',
        'dividends',
        'corporation_tax'
    ]

    def __init__(self):
        self.legal_source = "Corporation Tax Act 2009/2010; Finance Act 2024"

    def calculate_corporation_tax(
        self,
        taxable_profits: Decimal,
        financial_year: str = "2024/25",
        associated_companies: int = 0
    ) -> Dict:
        """
        Calculate Corporation Tax liability

        Args:
            taxable_profits: Taxable profits for the period
            financial_year: Financial year (e.g., "2024/25")
            associated_companies: Number of associated companies (affects limits)

        Returns:
            Dictionary with tax calculation details

        Reference: CTA 2010, Part 3, Chapter 3A
        """
        # Adjust limits for associated companies
        divisor = Decimal(associated_companies + 1)
        adjusted_lower = self.LOWER_LIMIT / divisor
        adjusted_upper = self.UPPER_LIMIT / divisor

        # Determine applicable rate
        if taxable_profits <= adjusted_lower:
            # Small profits rate
            rate = self.SMALL_PROFITS_RATE
            tax = (taxable_profits * rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            relief = Decimal('0.00')
            effective_rate = rate

        elif taxable_profits >= adjusted_upper:
            # Main rate
            rate = self.MAIN_RATE
            tax = (taxable_profits * rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            relief = Decimal('0.00')
            effective_rate = rate

        else:
            # Marginal relief applies
            rate = self.MAIN_RATE
            tax_at_main_rate = (taxable_profits * rate / Decimal('100'))

            # Marginal relief calculation
            # Relief = (Upper Limit - Profits) × Profits / Upper Limit × 3/200
            relief = (
                (adjusted_upper - taxable_profits) *
                taxable_profits /
                adjusted_upper *
                self.MARGINAL_RELIEF_FRACTION
            )

            tax = (tax_at_main_rate - relief).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            effective_rate = (tax / taxable_profits * Decimal('100')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        return {
            'taxable_profits': float(taxable_profits),
            'corporation_tax': float(tax),
            'rate_applied': float(rate),
            'effective_rate': float(effective_rate),
            'marginal_relief': float(relief),
            'lower_limit': float(adjusted_lower),
            'upper_limit': float(adjusted_upper),
            'associated_companies': associated_companies,
            'financial_year': financial_year,
            'legal_reference': 'CTA 2010, s18A-18F (Marginal Relief)'
        }

    def validate_ct_rates(self, text: str, financial_year: str = "2024/25") -> Dict:
        """
        Validate Corporation Tax rates mentioned in text

        Reference: Finance Act 2024
        """
        issues = []
        mentions = []

        text_lower = text.lower()

        # Find rate mentions
        rate_pattern = r'(?:corporation\s+tax|ct).*?(\d+(?:\.\d+)?)\s*%|(\d+(?:\.\d+)?)\s*%.*?(?:corporation\s+tax|ct)'

        correct_rates = self.HISTORICAL_RATES.get(
            financial_year,
            {'main': self.MAIN_RATE, 'small': self.SMALL_PROFITS_RATE}
        )

        for match in re.finditer(rate_pattern, text_lower):
            rate_str = match.group(1) or match.group(2)
            try:
                rate = Decimal(rate_str)
            except Exception:
                continue

            mention = {
                'rate': float(rate),
                'text': match.group(0),
                'position': (match.start(), match.end())
            }
            mentions.append(mention)

            # Check if rate is valid for the financial year
            valid_rates = [correct_rates['main'], correct_rates['small']]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_ct_rate',
                    'severity': 'high',
                    'stated_rate': float(rate),
                    'valid_rates': [float(r) for r in valid_rates],
                    'financial_year': financial_year,
                    'message': f'Invalid CT rate: {rate}%. Valid rates for {financial_year}: {", ".join(str(float(r)) + "%" for r in valid_rates)}',
                    'legal_reference': 'Finance Act 2024; CTA 2010, s4'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'mentions': mentions,
            'correct_rates': {
                'main_rate': float(correct_rates['main']),
                'small_profits_rate': float(correct_rates['small'])
            }
        }

    def validate_profit_thresholds(self, text: str) -> Dict:
        """
        Validate profit threshold mentions

        Reference: CTA 2010, s18A
        """
        issues = []

        text_lower = text.lower()

        # Find threshold mentions
        threshold_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:k)?)'

        thresholds_found = []
        for match in re.finditer(threshold_pattern, text):
            threshold_str = match.group(1).replace(',', '').replace('k', '000')
            try:
                threshold = Decimal(threshold_str)
                thresholds_found.append({
                    'amount': threshold,
                    'text': match.group(0),
                    'position': (match.start(), match.end())
                })
            except Exception:
                continue

        # Check for incorrect thresholds
        for threshold_data in thresholds_found:
            amount = threshold_data['amount']

            # Check if near lower limit
            if Decimal('40000') <= amount <= Decimal('60000'):
                if amount != self.LOWER_LIMIT:
                    issues.append({
                        'type': 'incorrect_lower_limit',
                        'severity': 'high',
                        'stated_amount': float(amount),
                        'correct_amount': float(self.LOWER_LIMIT),
                        'message': f'Incorrect lower limit: stated £{amount}, should be £{self.LOWER_LIMIT}',
                        'legal_reference': 'CTA 2010, s18A(2)'
                    })

            # Check if near upper limit
            if Decimal('200000') <= amount <= Decimal('300000'):
                if amount != self.UPPER_LIMIT:
                    issues.append({
                        'type': 'incorrect_upper_limit',
                        'severity': 'high',
                        'stated_amount': float(amount),
                        'correct_amount': float(self.UPPER_LIMIT),
                        'message': f'Incorrect upper limit: stated £{amount}, should be £{self.UPPER_LIMIT}',
                        'legal_reference': 'CTA 2010, s18A(3)'
                    })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'correct_thresholds': {
                'lower_limit': float(self.LOWER_LIMIT),
                'upper_limit': float(self.UPPER_LIMIT)
            }
        }

    def validate_allowable_expenses(self, text: str) -> Dict:
        """
        Validate expense deductibility claims

        Reference: CTA 2009, Part 3 (Trading Income)
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Check for non-allowable expenses being claimed as deductible
        non_allowable_patterns = {
            'entertaining': (r'entertainment|client\s+entertainment|hospitality', 'CTA 2009, s45-47'),
            'depreciation': (r'depreciation|depreciated', 'CTA 2009, s53'),
            'capital_items': (r'capital\s+(?:item|expenditure|asset)', 'CTA 2009, s53'),
            'tax_penalties': (r'(?:tax\s+)?penalt(?:y|ies)|hmrc\s+fine', 'CTA 2009, s54'),
            'dividends': (r'dividend\s+payment|dividend\s+distribution', 'CTA 2009, s1285'),
            'political_donations': (r'political\s+donation|party\s+donation', 'CTA 2009, s54'),
        }

        for expense_type, (pattern, reference) in non_allowable_patterns.items():
            if re.search(pattern, text_lower):
                # Check if being claimed as deductible
                if re.search(r'(?:deduct|allowable|claim|expense)', text_lower):
                    issues.append({
                        'type': f'non_allowable_{expense_type}',
                        'severity': 'high',
                        'expense_type': expense_type,
                        'message': f'{expense_type.replace("_", " ").title()} is not allowable for Corporation Tax',
                        'legal_reference': reference
                    })

        # Check for capital allowances confusion
        if 'capital allowance' in text_lower or 'plant and machinery' in text_lower:
            if 'depreciation' in text_lower:
                warnings.append({
                    'type': 'capital_allowance_depreciation',
                    'severity': 'medium',
                    'message': 'Capital allowances replace depreciation for tax purposes',
                    'clarification': 'Claim capital allowances on qualifying assets, not accounting depreciation',
                    'legal_reference': 'CAA 2001'
                })

        # Check for wholly and exclusively test
        if re.search(r'(?:expense|deduction|claim)', text_lower):
            if not re.search(r'wholly.*exclusively|exclusively.*wholly|business\s+purpose', text_lower):
                warnings.append({
                    'type': 'wholly_exclusively_test_missing',
                    'severity': 'medium',
                    'message': 'Should reference "wholly and exclusively" test for expenses',
                    'clarification': 'Expenses must be incurred wholly and exclusively for business purposes',
                    'legal_reference': 'CTA 2009, s54'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_accounting_period(self, text: str) -> Dict:
        """
        Validate accounting period references

        Reference: CTA 2009, s10
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'accounting period' not in text_lower:
            return {'applicable': False}

        # Check for period length over 12 months
        period_pattern = r'(\d+)\s*(?:month|mon|mo)s?'

        for match in re.finditer(period_pattern, text_lower):
            try:
                months = int(match.group(1))
                if months > 12:
                    issues.append({
                        'type': 'accounting_period_too_long',
                        'severity': 'high',
                        'stated_months': months,
                        'message': 'Accounting period cannot exceed 12 months',
                        'correction': 'Period over 12 months must be split',
                        'legal_reference': 'CTA 2009, s10(3)'
                    })
            except Exception:
                continue

        # Check for straddling periods mention
        if re.search(r'straddle|spans|crosses.*(?:year|period)', text_lower):
            if not re.search(r'apportion|split|divide', text_lower):
                warnings.append({
                    'type': 'straddling_apportionment',
                    'severity': 'medium',
                    'message': 'Straddling periods require profit apportionment',
                    'clarification': 'Profits must be apportioned between financial years if period straddles year end',
                    'legal_reference': 'CTA 2010, s8'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_associated_companies(self, text: str) -> Dict:
        """
        Validate associated companies treatment

        Reference: CTA 2010, s25
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'associated' not in text_lower and 'group' not in text_lower:
            return {'applicable': False}

        # Check for control definition
        if 'associated compan' in text_lower:
            if not re.search(r'(?:control|51%|majority|parent)', text_lower):
                warnings.append({
                    'type': 'associated_definition_unclear',
                    'severity': 'medium',
                    'message': 'Should define associated companies',
                    'clarification': 'Companies are associated if one controls the other, or both controlled by the same person/company',
                    'legal_reference': 'CTA 2010, s25'
                })

        # Check for threshold adjustment mention
        if 'associated compan' in text_lower:
            if not re.search(r'(?:divide|adjust|split).*(?:threshold|limit)', text_lower):
                warnings.append({
                    'type': 'threshold_adjustment_missing',
                    'severity': 'high',
                    'message': 'Should mention threshold adjustment for associated companies',
                    'clarification': 'Profit limits must be divided by (number of associated companies + 1)',
                    'legal_reference': 'CTA 2010, s18A(4)'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_payment_deadlines(self, text: str) -> Dict:
        """
        Validate Corporation Tax payment deadline information

        Reference: TMA 1970, s59D; FA 1998, Schedule 18
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'payment' not in text_lower and 'deadline' not in text_lower:
            return {'applicable': False}

        # Standard payment deadline: 9 months and 1 day after period end
        if re.search(r'payment.*(?:deadline|due)', text_lower):
            if not re.search(r'9\s*month|nine\s*month', text_lower):
                warnings.append({
                    'type': 'payment_deadline_unclear',
                    'severity': 'medium',
                    'message': 'Should specify payment deadline',
                    'clarification': 'CT due 9 months and 1 day after accounting period end (small companies)',
                    'legal_reference': 'TMA 1970, s59D'
                })

        # Quarterly instalments for large companies
        large_company_pattern = r'large\s+compan(?:y|ies)|£1\.?5m|1\.5\s*million'
        if re.search(large_company_pattern, text_lower):
            if not re.search(r'quarterly\s+(?:instalment|payment)', text_lower):
                warnings.append({
                    'type': 'quarterly_instalments_missing',
                    'severity': 'high',
                    'message': 'Large companies must pay CT in quarterly instalments',
                    'clarification': 'Companies with profits over £1.5m pay in 4 quarterly instalments',
                    'legal_reference': 'SI 1998/3175 (Corporation Tax Instalments Regulations)'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_ct600_filing(self, text: str) -> Dict:
        """
        Validate CT600 tax return filing requirements

        Reference: FA 1998, Schedule 18, Para 14
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'ct600' not in text_lower and 'tax return' not in text_lower:
            return {'applicable': False}

        # Filing deadline: 12 months after period end
        if re.search(r'filing.*deadline|return.*due', text_lower):
            if not re.search(r'12\s*month|twelve\s*month|year', text_lower):
                warnings.append({
                    'type': 'filing_deadline_unclear',
                    'severity': 'medium',
                    'message': 'Should specify filing deadline',
                    'clarification': 'CT600 due 12 months after accounting period end',
                    'legal_reference': 'FA 1998, Schedule 18, Para 14'
                })

        # Online filing requirement
        if re.search(r'filing|submit|return', text_lower):
            if not re.search(r'online|hmrc\s+online|digital', text_lower):
                warnings.append({
                    'type': 'online_filing_not_mentioned',
                    'severity': 'low',
                    'message': 'Should mention online filing requirement',
                    'clarification': 'CT600 must be filed online via HMRC Online Services or compatible software',
                    'legal_reference': 'FA 1998, Schedule 18, Para 14(3A)'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_ct_check(
        self,
        text: str,
        financial_year: str = "2024/25"
    ) -> Dict:
        """
        Run comprehensive Corporation Tax compliance check
        """
        results = {
            'rate_validation': self.validate_ct_rates(text, financial_year),
            'threshold_validation': self.validate_profit_thresholds(text),
            'expense_validation': self.validate_allowable_expenses(text),
            'accounting_period': self.validate_accounting_period(text),
            'associated_companies': self.validate_associated_companies(text),
            'payment_deadlines': self.validate_payment_deadlines(text),
            'ct600_filing': self.validate_ct600_filing(text)
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
