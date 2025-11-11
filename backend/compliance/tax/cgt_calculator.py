"""
Capital Gains Tax Calculator
CGT calculation and validation for UK tax compliance

Legal References:
- Taxation of Chargeable Gains Act 1992 (TCGA 1992)
- Finance Act 2024
- HMRC Capital Gains Manual (CG)

2024/25 Rates:
- Annual Exempt Amount: £3,000 (reduced from £6,000)
- Basic rate taxpayers: 10% (18% for residential property)
- Higher/Additional rate: 20% (24% for residential property)
- Business Asset Disposal Relief: 10% (lifetime limit £1m)
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from enum import Enum


class AssetType(Enum):
    """Types of assets for CGT"""
    RESIDENTIAL_PROPERTY = "residential_property"
    OTHER_PROPERTY = "other_property"
    SHARES = "shares"
    BUSINESS_ASSETS = "business_assets"
    PERSONAL_POSSESSIONS = "personal_possessions"
    CRYPTOCURRENCY = "cryptocurrency"


class CGTCalculator:
    """Capital Gains Tax calculator and validator"""

    # 2024/25 rates and allowances
    ANNUAL_EXEMPT_AMOUNT = Decimal('3000.00')  # Reduced from £6,000
    BASIC_RATE = Decimal('10.00')
    HIGHER_RATE = Decimal('20.00')
    PROPERTY_BASIC_RATE = Decimal('18.00')
    PROPERTY_HIGHER_RATE = Decimal('24.00')

    # Business Asset Disposal Relief (formerly Entrepreneurs' Relief)
    BADR_RATE = Decimal('10.00')
    BADR_LIFETIME_LIMIT = Decimal('1000000.00')

    # Reporting thresholds
    PROPERTY_REPORTING_DAYS = 60  # Report and pay within 60 days
    GENERAL_REPORTING_THRESHOLD = Decimal('50000.00')

    def __init__(self):
        self.legal_source = "TCGA 1992; Finance Act 2024"

    def calculate_cgt(
        self,
        gain: Decimal,
        asset_type: AssetType,
        basic_rate_taxpayer: bool = True,
        other_gains: Decimal = Decimal('0.00'),
        annual_exempt_used: Decimal = Decimal('0.00')
    ) -> Dict:
        """
        Calculate Capital Gains Tax

        Args:
            gain: Capital gain amount
            asset_type: Type of asset
            basic_rate_taxpayer: Whether taxpayer is basic rate
            other_gains: Other gains in the tax year
            annual_exempt_used: AEA already used

        Reference: TCGA 1992, s1-4
        """
        # Apply Annual Exempt Amount
        total_gains = gain + other_gains
        available_aea = max(Decimal('0.00'), self.ANNUAL_EXEMPT_AMOUNT - annual_exempt_used)
        taxable_gain = max(Decimal('0.00'), gain - available_aea)

        # Determine rate based on asset type and taxpayer status
        if asset_type in [AssetType.RESIDENTIAL_PROPERTY, AssetType.OTHER_PROPERTY]:
            rate = self.PROPERTY_BASIC_RATE if basic_rate_taxpayer else self.PROPERTY_HIGHER_RATE
        else:
            rate = self.BASIC_RATE if basic_rate_taxpayer else self.HIGHER_RATE

        cgt = (taxable_gain * rate / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        return {
            'gross_gain': float(gain),
            'annual_exempt_amount': float(available_aea),
            'taxable_gain': float(taxable_gain),
            'rate': float(rate),
            'cgt': float(cgt),
            'asset_type': asset_type.value,
            'legal_reference': 'TCGA 1992, s1-4'
        }

    def calculate_badr(
        self,
        gain: Decimal,
        lifetime_badr_used: Decimal = Decimal('0.00')
    ) -> Dict:
        """
        Calculate Business Asset Disposal Relief

        Reference: TCGA 1992, s169H-169S
        """
        # Check remaining lifetime limit
        remaining_limit = self.BADR_LIFETIME_LIMIT - lifetime_badr_used

        if remaining_limit <= 0:
            return {
                'badr_available': False,
                'reason': 'Lifetime limit exhausted',
                'lifetime_limit': float(self.BADR_LIFETIME_LIMIT),
                'used': float(lifetime_badr_used)
            }

        # Calculate relief
        badr_gain = min(gain, remaining_limit)
        excess_gain = max(Decimal('0.00'), gain - remaining_limit)

        badr_tax = (badr_gain * self.BADR_RATE / Decimal('100')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        return {
            'badr_available': True,
            'gain_qualifying_for_badr': float(badr_gain),
            'excess_gain': float(excess_gain),
            'badr_rate': float(self.BADR_RATE),
            'badr_tax': float(badr_tax),
            'lifetime_limit': float(self.BADR_LIFETIME_LIMIT),
            'remaining_limit': float(remaining_limit),
            'legal_reference': 'TCGA 1992, s169H-169S'
        }

    def validate_cgt_rates(self, text: str) -> Dict:
        """
        Validate CGT rates mentioned in text

        Reference: TCGA 1992; Finance Act 2024
        """
        issues = []

        text_lower = text.lower()

        # Find CGT rate mentions
        rate_pattern = r'(?:capital\s+gains|cgt).*?(\d+(?:\.\d+)?)\s*%'

        for match in re.finditer(rate_pattern, text_lower):
            try:
                rate = Decimal(match.group(1))
            except Exception:
                continue

            # Valid CGT rates
            valid_rates = [
                self.BASIC_RATE,
                self.HIGHER_RATE,
                self.PROPERTY_BASIC_RATE,
                self.PROPERTY_HIGHER_RATE,
                self.BADR_RATE
            ]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_cgt_rate',
                    'severity': 'high',
                    'stated_rate': float(rate),
                    'valid_rates': [float(r) for r in valid_rates],
                    'message': f'Invalid CGT rate: {rate}%',
                    'legal_reference': 'TCGA 1992; Finance Act 2024'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def validate_annual_exempt_amount(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Validate Annual Exempt Amount mentions

        Reference: TCGA 1992, s3
        """
        issues = []

        text_lower = text.lower()

        # Historical AEA values for validation
        historical_aea = {
            '2024/25': Decimal('3000.00'),
            '2023/24': Decimal('6000.00'),
            '2022/23': Decimal('12300.00'),
        }

        correct_aea = historical_aea.get(tax_year, self.ANNUAL_EXEMPT_AMOUNT)

        # Find AEA mentions
        aea_pattern = r'(?:annual\s+exempt|cgt\s+allowance).*?£\s*(\d{1,2},?\d{3})'

        for match in re.finditer(aea_pattern, text_lower):
            amount_str = match.group(1).replace(',', '')
            try:
                stated_aea = Decimal(amount_str)
                if stated_aea != correct_aea:
                    issues.append({
                        'type': 'incorrect_aea',
                        'severity': 'high',
                        'stated_amount': float(stated_aea),
                        'correct_amount': float(correct_aea),
                        'tax_year': tax_year,
                        'message': f'Incorrect Annual Exempt Amount: stated £{stated_aea}, should be £{correct_aea}',
                        'legal_reference': 'TCGA 1992, s3'
                    })
            except Exception:
                continue

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'correct_aea': float(correct_aea)
        }

    def validate_property_reporting(self, text: str) -> Dict:
        """
        Validate property CGT reporting requirements

        Reference: FA 2019, Schedule 2 (Property Disposal Returns)
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if not any(word in text_lower for word in ['property', 'residential', 'house', 'flat']):
            return {'applicable': False}

        # Check for 60-day reporting requirement
        if re.search(r'(?:sale|disposal).*property', text_lower):
            if not re.search(r'60\s+day|two\s+month', text_lower):
                warnings.append({
                    'type': 'property_reporting_deadline_missing',
                    'severity': 'high',
                    'message': 'UK residential property disposals must be reported within 60 days',
                    'deadline': '60 days from completion',
                    'legal_reference': 'FA 2019, Schedule 2'
                })

        # Check for payment requirement
        if re.search(r'property.*(?:cgt|capital\s+gains)', text_lower):
            if not re.search(r'payment.*(?:account|advance|60\s+day)', text_lower):
                warnings.append({
                    'type': 'property_cgt_payment_missing',
                    'severity': 'high',
                    'message': 'CGT on UK property must be paid within 60 days',
                    'clarification': 'Report and pay CGT within 60 days, then report again in Self Assessment',
                    'legal_reference': 'FA 2019, Schedule 2'
                })

        # Check for private residence relief mention
        if 'property' in text_lower and 'cgt' in text_lower:
            if not re.search(r'private\s+residence|prr|main\s+home', text_lower):
                warnings.append({
                    'type': 'prr_not_mentioned',
                    'severity': 'low',
                    'message': 'Consider mentioning Private Residence Relief',
                    'clarification': 'Full relief for main home; partial relief for periods away',
                    'legal_reference': 'TCGA 1992, s222-226'
                })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_badr_conditions(self, text: str) -> Dict:
        """
        Validate Business Asset Disposal Relief conditions

        Reference: TCGA 1992, s169H-169S
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        badr_terms = ['business asset disposal relief', 'badr', 'entrepreneurs relief', 'entrepreneurs\' relief']
        if not any(term in text_lower for term in badr_terms):
            return {'applicable': False}

        # Check for ownership period
        if not re.search(r'(?:2|two)\s+year', text_lower):
            warnings.append({
                'type': 'badr_ownership_period',
                'severity': 'high',
                'message': 'BADR requires 2-year ownership period',
                'clarification': 'Must own business/shares for at least 2 years before disposal',
                'legal_reference': 'TCGA 1992, s169I(6)'
            })

        # Check for 5% shareholding requirement (for companies)
        if 'shares' in text_lower or 'company' in text_lower:
            if not re.search(r'5\s*%|five\s+percent', text_lower):
                warnings.append({
                    'type': 'badr_shareholding_requirement',
                    'severity': 'high',
                    'message': 'BADR for shares requires at least 5% shareholding',
                    'clarification': 'Must hold at least 5% of shares and voting rights',
                    'legal_reference': 'TCGA 1992, s169S(3)'
                })

        # Check for lifetime limit mention
        if not re.search(r'£1,?000,?000|£1m|one\s+million', text_lower):
            warnings.append({
                'type': 'badr_lifetime_limit',
                'severity': 'medium',
                'message': 'BADR lifetime limit not mentioned',
                'clarification': 'Lifetime limit of £1 million of gains',
                'legal_reference': 'TCGA 1992, s169N(3)'
            })

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_cgt_check(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Run comprehensive CGT compliance check
        """
        results = {
            'rate_validation': self.validate_cgt_rates(text),
            'aea_validation': self.validate_annual_exempt_amount(text, tax_year),
            'property_reporting': self.validate_property_reporting(text),
            'badr_conditions': self.validate_badr_conditions(text)
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
