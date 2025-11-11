"""
PAYE and National Insurance Calculator
Comprehensive PAYE and NIC calculation and validation

Legal References:
- Income Tax (Earnings and Pensions) Act 2003 (ITEPA)
- Social Security Contributions and Benefits Act 1992
- HMRC PAYE Manual
- National Insurance Contributions Act 2014
- Finance Act 2024

2024/25 Rates:
- Personal Allowance: £12,570
- Basic rate (20%): £12,571 - £50,270
- Higher rate (40%): £50,271 - £125,140
- Additional rate (45%): Over £125,140
- Scottish rates differ
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from enum import Enum


class TaxRegion(Enum):
    """UK tax regions"""
    ENGLAND = "england"
    WALES = "wales"
    SCOTLAND = "scotland"
    NORTHERN_IRELAND = "northern_ireland"


class NICategory(Enum):
    """National Insurance categories"""
    A = "A"  # Standard employees
    B = "B"  # Married women/widows (reduced rate)
    C = "C"  # Employees over State Pension age
    H = "H"  # Apprentices under 25
    M = "M"  # Employees under 21


class PAYECalculator:
    """PAYE and National Insurance calculator"""

    # 2024/25 Income Tax rates (England, Wales, NI)
    PERSONAL_ALLOWANCE = Decimal('12570.00')
    BASIC_RATE_LIMIT = Decimal('50270.00')
    HIGHER_RATE_LIMIT = Decimal('125140.00')

    BASIC_RATE = Decimal('20.00')
    HIGHER_RATE = Decimal('40.00')
    ADDITIONAL_RATE = Decimal('45.00')

    # Scotland 2024/25 rates (different from rest of UK)
    SCOTLAND_RATES = [
        (Decimal('0.00'), Decimal('2162.00'), Decimal('19.00')),      # Starter rate
        (Decimal('2162.00'), Decimal('13118.00'), Decimal('20.00')),  # Basic rate
        (Decimal('13118.00'), Decimal('31092.00'), Decimal('21.00')), # Intermediate rate
        (Decimal('31092.00'), Decimal('125140.00'), Decimal('42.00')), # Higher rate
        (Decimal('125140.00'), None, Decimal('47.00')),               # Top rate
    ]

    # National Insurance 2024/25
    NI_EMPLOYEE_THRESHOLD = Decimal('12570.00')  # Primary Threshold (aligned with PA)
    NI_EMPLOYEE_UEL = Decimal('50270.00')  # Upper Earnings Limit
    NI_EMPLOYEE_RATE_MAIN = Decimal('12.00')
    NI_EMPLOYEE_RATE_ADDITIONAL = Decimal('2.00')

    NI_EMPLOYER_THRESHOLD = Decimal('9100.00')  # Secondary Threshold (annual)
    NI_EMPLOYER_RATE = Decimal('13.8')

    # Employment Allowance (2024/25)
    EMPLOYMENT_ALLOWANCE = Decimal('5000.00')

    def __init__(self):
        self.legal_source = "ITEPA 2003; SSCBA 1992; Finance Act 2024"

    def calculate_income_tax(
        self,
        annual_salary: Decimal,
        region: TaxRegion = TaxRegion.ENGLAND,
        personal_allowance: Optional[Decimal] = None,
        tax_code: Optional[str] = None
    ) -> Dict:
        """
        Calculate income tax on salary

        Args:
            annual_salary: Annual gross salary
            region: Tax region (affects rates)
            personal_allowance: Override PA if different
            tax_code: Tax code for validation

        Returns:
            Tax calculation breakdown

        Reference: ITEPA 2003, Part 2
        """
        if personal_allowance is None:
            personal_allowance = self.PERSONAL_ALLOWANCE

            # Taper personal allowance if over £100,000
            if annual_salary > Decimal('100000.00'):
                excess = annual_salary - Decimal('100000.00')
                reduction = excess / Decimal('2')
                personal_allowance = max(Decimal('0.00'), personal_allowance - reduction)

        taxable_income = max(Decimal('0.00'), annual_salary - personal_allowance)

        if region == TaxRegion.SCOTLAND:
            return self._calculate_scottish_tax(taxable_income, personal_allowance)
        else:
            return self._calculate_uk_tax(taxable_income, personal_allowance)

    def _calculate_uk_tax(self, taxable_income: Decimal, personal_allowance: Decimal) -> Dict:
        """Calculate tax for England, Wales, Northern Ireland"""
        tax = Decimal('0.00')
        breakdown = []

        # Basic rate band
        basic_band = min(taxable_income, self.BASIC_RATE_LIMIT - self.PERSONAL_ALLOWANCE)
        if basic_band > 0:
            basic_tax = basic_band * self.BASIC_RATE / Decimal('100')
            tax += basic_tax
            breakdown.append({
                'band': 'basic',
                'rate': float(self.BASIC_RATE),
                'income': float(basic_band),
                'tax': float(basic_tax)
            })

        # Higher rate band
        if taxable_income > (self.BASIC_RATE_LIMIT - self.PERSONAL_ALLOWANCE):
            higher_band = min(
                taxable_income - (self.BASIC_RATE_LIMIT - self.PERSONAL_ALLOWANCE),
                self.HIGHER_RATE_LIMIT - self.BASIC_RATE_LIMIT
            )
            higher_tax = higher_band * self.HIGHER_RATE / Decimal('100')
            tax += higher_tax
            breakdown.append({
                'band': 'higher',
                'rate': float(self.HIGHER_RATE),
                'income': float(higher_band),
                'tax': float(higher_tax)
            })

        # Additional rate band
        if taxable_income > (self.HIGHER_RATE_LIMIT - self.PERSONAL_ALLOWANCE):
            additional_band = taxable_income - (self.HIGHER_RATE_LIMIT - self.PERSONAL_ALLOWANCE)
            additional_tax = additional_band * self.ADDITIONAL_RATE / Decimal('100')
            tax += additional_tax
            breakdown.append({
                'band': 'additional',
                'rate': float(self.ADDITIONAL_RATE),
                'income': float(additional_band),
                'tax': float(additional_tax)
            })

        tax = tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'taxable_income': float(taxable_income),
            'personal_allowance': float(personal_allowance),
            'total_tax': float(tax),
            'effective_rate': float((tax / taxable_income * Decimal('100')).quantize(Decimal('0.01'))) if taxable_income > 0 else 0,
            'breakdown': breakdown,
            'region': 'England/Wales/NI',
            'legal_reference': 'ITEPA 2003, s10-13'
        }

    def _calculate_scottish_tax(self, taxable_income: Decimal, personal_allowance: Decimal) -> Dict:
        """Calculate Scottish income tax (different rates)"""
        tax = Decimal('0.00')
        breakdown = []
        remaining = taxable_income

        for lower, upper, rate in self.SCOTLAND_RATES:
            if remaining <= 0:
                break

            if upper is None:
                band_income = remaining
            else:
                band_income = min(remaining, upper - lower)

            if band_income > 0:
                band_tax = band_income * rate / Decimal('100')
                tax += band_tax

                band_names = ['starter', 'basic', 'intermediate', 'higher', 'top']
                band_idx = self.SCOTLAND_RATES.index((lower, upper, rate))

                breakdown.append({
                    'band': band_names[band_idx],
                    'rate': float(rate),
                    'income': float(band_income),
                    'tax': float(band_tax)
                })

                remaining -= band_income

        tax = tax.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'taxable_income': float(taxable_income),
            'personal_allowance': float(personal_allowance),
            'total_tax': float(tax),
            'effective_rate': float((tax / taxable_income * Decimal('100')).quantize(Decimal('0.01'))) if taxable_income > 0 else 0,
            'breakdown': breakdown,
            'region': 'Scotland',
            'legal_reference': 'Scottish Income Tax Act 2024'
        }

    def calculate_employee_ni(
        self,
        annual_salary: Decimal,
        category: NICategory = NICategory.A
    ) -> Dict:
        """
        Calculate employee National Insurance contributions

        Reference: SSCBA 1992, s1
        """
        if category in [NICategory.C]:
            # No NI for employees over State Pension age
            return {
                'annual_salary': float(annual_salary),
                'category': category.value,
                'total_ni': 0.00,
                'breakdown': [],
                'note': 'No NI contributions for employees over State Pension age',
                'legal_reference': 'SSCBA 1992, s6(1)'
            }

        ni = Decimal('0.00')
        breakdown = []

        # Main rate (12%) on earnings between PT and UEL
        if annual_salary > self.NI_EMPLOYEE_THRESHOLD:
            main_band = min(
                annual_salary - self.NI_EMPLOYEE_THRESHOLD,
                self.NI_EMPLOYEE_UEL - self.NI_EMPLOYEE_THRESHOLD
            )
            main_ni = main_band * self.NI_EMPLOYEE_RATE_MAIN / Decimal('100')
            ni += main_ni

            breakdown.append({
                'band': 'main',
                'rate': float(self.NI_EMPLOYEE_RATE_MAIN),
                'earnings': float(main_band),
                'ni': float(main_ni)
            })

        # Additional rate (2%) on earnings above UEL
        if annual_salary > self.NI_EMPLOYEE_UEL:
            additional_band = annual_salary - self.NI_EMPLOYEE_UEL
            additional_ni = additional_band * self.NI_EMPLOYEE_RATE_ADDITIONAL / Decimal('100')
            ni += additional_ni

            breakdown.append({
                'band': 'additional',
                'rate': float(self.NI_EMPLOYEE_RATE_ADDITIONAL),
                'earnings': float(additional_band),
                'ni': float(additional_ni)
            })

        ni = ni.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'annual_salary': float(annual_salary),
            'category': category.value,
            'total_ni': float(ni),
            'primary_threshold': float(self.NI_EMPLOYEE_THRESHOLD),
            'upper_earnings_limit': float(self.NI_EMPLOYEE_UEL),
            'breakdown': breakdown,
            'legal_reference': 'SSCBA 1992, s8; NIC Act 2014'
        }

    def calculate_employer_ni(
        self,
        annual_salary: Decimal,
        employment_allowance: bool = False
    ) -> Dict:
        """
        Calculate employer National Insurance contributions

        Reference: SSCBA 1992, s9
        """
        ni = Decimal('0.00')

        if annual_salary > self.NI_EMPLOYER_THRESHOLD:
            ni_earnings = annual_salary - self.NI_EMPLOYER_THRESHOLD
            ni = ni_earnings * self.NI_EMPLOYER_RATE / Decimal('100')
            ni = ni.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Apply Employment Allowance if applicable
        allowance_used = Decimal('0.00')
        if employment_allowance and ni > 0:
            allowance_used = min(ni, self.EMPLOYMENT_ALLOWANCE)
            ni = max(Decimal('0.00'), ni - allowance_used)

        return {
            'annual_salary': float(annual_salary),
            'secondary_threshold': float(self.NI_EMPLOYER_THRESHOLD),
            'rate': float(self.NI_EMPLOYER_RATE),
            'gross_ni': float(ni + allowance_used),
            'employment_allowance': float(allowance_used),
            'net_ni': float(ni),
            'legal_reference': 'SSCBA 1992, s9; Employment Allowance Regulations 2014'
        }

    def validate_tax_code(self, tax_code: str) -> Dict:
        """
        Validate PAYE tax code

        Reference: HMRC PAYE Manual, PAYE20000+
        """
        issues = []
        warnings = []

        if not tax_code:
            return {
                'valid': False,
                'issues': [{'message': 'No tax code provided'}]
            }

        tax_code = tax_code.strip().upper()

        # Common tax code patterns
        standard_pattern = r'^(\d{3,4})([LMNT])$'
        scottish_pattern = r'^S(\d{3,4})([LMNT])$'
        emergency_pattern = r'^(\d{3,4})([LM])1$'
        zero_pattern = r'^0T$'
        br_pattern = r'^BR$'
        nt_pattern = r'^NT$'

        # Check for standard tax code
        if re.match(standard_pattern, tax_code):
            match = re.match(standard_pattern, tax_code)
            number = int(match.group(1))
            suffix = match.group(2)

            # Check if allowance matches current year
            expected = int(self.PERSONAL_ALLOWANCE / Decimal('10'))
            if abs(number - expected) > 100:
                warnings.append({
                    'type': 'tax_code_outdated',
                    'severity': 'medium',
                    'message': f'Tax code {tax_code} may be outdated',
                    'expected_range': f'{expected-50} to {expected+50}',
                    'current_pa': f'£{self.PERSONAL_ALLOWANCE}'
                })

        # Check for Scottish tax code
        elif re.match(scottish_pattern, tax_code):
            match = re.match(scottish_pattern, tax_code)
            number = int(match.group(1))
            suffix = match.group(2)
            # Valid Scottish code

        # Emergency codes
        elif re.match(emergency_pattern, tax_code):
            warnings.append({
                'type': 'emergency_tax_code',
                'severity': 'high',
                'message': f'Emergency tax code {tax_code} in use',
                'action': 'Employee should provide P45 or complete Starter Checklist'
            })

        # Special codes
        elif tax_code in ['0T', 'BR', 'NT', 'D0', 'D1', 'K']:
            warnings.append({
                'type': 'special_tax_code',
                'severity': 'medium',
                'message': f'Special tax code {tax_code} in use',
                'meaning': self._explain_tax_code(tax_code)
            })

        else:
            issues.append({
                'type': 'invalid_tax_code',
                'severity': 'high',
                'message': f'Invalid tax code format: {tax_code}'
            })

        return {
            'valid': len(issues) == 0,
            'tax_code': tax_code,
            'issues': issues,
            'warnings': warnings
        }

    def _explain_tax_code(self, code: str) -> str:
        """Explain special tax codes"""
        explanations = {
            '0T': 'Personal allowance has been used up or employee started part way through year',
            'BR': 'All income taxed at basic rate (20%) - often second job',
            'NT': 'No tax to be deducted',
            'D0': 'All income taxed at higher rate (40%)',
            'D1': 'All income taxed at additional rate (45%)',
            'K': 'Deductions exceed allowances (tax on company benefits)'
        }
        return explanations.get(code, 'Special tax code')

    def validate_paye_rates(self, text: str, region: str = "england") -> Dict:
        """
        Validate PAYE rates mentioned in text

        Reference: ITEPA 2003
        """
        issues = []

        text_lower = text.lower()

        # Find rate mentions
        rate_pattern = r'(?:income\s+tax|tax\s+rate|paye).*?(\d+(?:\.\d+)?)\s*%'

        for match in re.finditer(rate_pattern, text_lower):
            try:
                rate = Decimal(match.group(1))
            except Exception:
                continue

            # Check if rate is valid
            if region == "scotland":
                valid_rates = [Decimal('19'), Decimal('20'), Decimal('21'), Decimal('42'), Decimal('47')]
            else:
                valid_rates = [self.BASIC_RATE, self.HIGHER_RATE, self.ADDITIONAL_RATE]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_income_tax_rate',
                    'severity': 'high',
                    'stated_rate': float(rate),
                    'valid_rates': [float(r) for r in valid_rates],
                    'region': region,
                    'message': f'Invalid income tax rate: {rate}% for {region}',
                    'legal_reference': 'ITEPA 2003, s10'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def validate_ni_rates(self, text: str) -> Dict:
        """
        Validate National Insurance rates mentioned in text

        Reference: SSCBA 1992
        """
        issues = []

        text_lower = text.lower()

        # Find NI rate mentions
        ni_pattern = r'(?:national\s+insurance|ni|nic).*?(\d+(?:\.\d+)?)\s*%'

        for match in re.finditer(ni_pattern, text_lower):
            try:
                rate = Decimal(match.group(1))
            except Exception:
                continue

            # Valid NI rates
            valid_rates = [
                self.NI_EMPLOYEE_RATE_MAIN,
                self.NI_EMPLOYEE_RATE_ADDITIONAL,
                self.NI_EMPLOYER_RATE
            ]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_ni_rate',
                    'severity': 'high',
                    'stated_rate': float(rate),
                    'valid_rates': [float(r) for r in valid_rates],
                    'message': f'Invalid NI rate: {rate}%',
                    'legal_reference': 'SSCBA 1992; NIC Rates Letter 2024/25'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def comprehensive_paye_check(
        self,
        text: str,
        region: str = "england"
    ) -> Dict:
        """
        Run comprehensive PAYE/NIC compliance check
        """
        results = {
            'paye_rates': self.validate_paye_rates(text, region),
            'ni_rates': self.validate_ni_rates(text),
        }

        all_issues = []
        for check_name, check_result in results.items():
            if 'issues' in check_result:
                all_issues.extend(check_result['issues'])

        return {
            'overall_valid': len(all_issues) == 0,
            'total_issues': len(all_issues),
            'detailed_results': results,
            'all_issues': all_issues,
            'legal_source': self.legal_source
        }
