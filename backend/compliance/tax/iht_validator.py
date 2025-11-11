"""
Inheritance Tax Validator
IHT validation for UK estate planning and tax compliance

Legal References:
- Inheritance Tax Act 1984 (IHTA 1984)
- Finance Act 2024
- HMRC Inheritance Tax Manual (IHTM)

2024/25 Thresholds:
- Nil Rate Band: £325,000 (frozen until 2028)
- Residence Nil Rate Band: £175,000 (frozen until 2028)
- Main rate: 40%
- Reduced rate (with charity donation): 36%
"""

import re
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional


class IHTValidator:
    """Inheritance Tax compliance validator"""

    # 2024/25 thresholds (frozen)
    NIL_RATE_BAND = Decimal('325000.00')  # Frozen until April 2028
    RESIDENCE_NIL_RATE_BAND = Decimal('175000.00')  # Frozen until April 2028
    RNRB_TAPER_THRESHOLD = Decimal('2000000.00')  # Taper by £1 for every £2 over

    # Rates
    MAIN_RATE = Decimal('40.00')
    REDUCED_RATE = Decimal('36.00')  # If 10%+ left to charity
    LIFETIME_RATE = Decimal('20.00')  # On chargeable lifetime transfers

    # Exemptions
    SPOUSE_EXEMPTION = True  # Unlimited
    CHARITY_EXEMPTION = True  # Unlimited
    ANNUAL_EXEMPTION = Decimal('3000.00')
    SMALL_GIFTS_EXEMPTION = Decimal('250.00')
    WEDDING_GIFT_CHILD = Decimal('5000.00')
    WEDDING_GIFT_GRANDCHILD = Decimal('2500.00')
    WEDDING_GIFT_OTHER = Decimal('1000.00')

    # Seven year rule
    POTENTIALLY_EXEMPT_TRANSFER_YEARS = 7
    TAPER_RELIEF_YEARS = [
        (3, Decimal('0')),    # 0-3 years: no relief
        (4, Decimal('20')),   # 3-4 years: 20% relief
        (5, Decimal('40')),   # 4-5 years: 40% relief
        (6, Decimal('60')),   # 5-6 years: 60% relief
        (7, Decimal('80')),   # 6-7 years: 80% relief
    ]

    def __init__(self):
        self.legal_source = "IHTA 1984; Finance Act 2024"

    def calculate_iht(
        self,
        estate_value: Decimal,
        residence_value: Decimal = Decimal('0.00'),
        charity_legacy: Decimal = Decimal('0.00'),
        spouse_legacy: Decimal = Decimal('0.00'),
        previous_nil_rate_band_used: Decimal = Decimal('0.00'),
        transferable_nrb: Decimal = Decimal('0.00')
    ) -> Dict:
        """
        Calculate Inheritance Tax liability

        Reference: IHTA 1984, s4
        """
        # Deduct spouse exemption (unlimited)
        taxable_estate = estate_value - spouse_legacy

        # Check for charity reduced rate (36% if 10%+ to charity)
        charity_percentage = (charity_legacy / estate_value * Decimal('100')) if estate_value > 0 else Decimal('0')
        qualifies_for_reduced_rate = charity_percentage >= Decimal('10.00')

        # Calculate available nil rate band
        available_nrb = self.NIL_RATE_BAND + transferable_nrb - previous_nil_rate_band_used

        # Calculate available RNRB
        available_rnrb = self._calculate_rnrb(estate_value, residence_value)

        # Total nil rate bands
        total_nrb = available_nrb + available_rnrb

        # Calculate taxable amount
        taxable_amount = max(Decimal('0.00'), taxable_estate - total_nrb)

        # Apply rate
        rate = self.REDUCED_RATE if qualifies_for_reduced_rate else self.MAIN_RATE
        iht = (taxable_amount * rate / Decimal('100')).quantize(Decimal('0.01'))

        return {
            'estate_value': float(estate_value),
            'taxable_estate': float(taxable_estate),
            'nil_rate_band': float(available_nrb),
            'residence_nil_rate_band': float(available_rnrb),
            'total_nil_rate_bands': float(total_nrb),
            'taxable_amount': float(taxable_amount),
            'rate': float(rate),
            'qualifies_for_reduced_rate': qualifies_for_reduced_rate,
            'charity_percentage': float(charity_percentage),
            'iht_due': float(iht),
            'legal_reference': 'IHTA 1984, s4-7'
        }

    def _calculate_rnrb(self, estate_value: Decimal, residence_value: Decimal) -> Decimal:
        """
        Calculate Residence Nil Rate Band

        Reference: IHTA 1984, s8D-8M
        """
        if residence_value == 0:
            return Decimal('0.00')

        # Taper if estate over £2m
        if estate_value > self.RNRB_TAPER_THRESHOLD:
            excess = estate_value - self.RNRB_TAPER_THRESHOLD
            reduction = excess / Decimal('2')
            rnrb = max(Decimal('0.00'), self.RESIDENCE_NIL_RATE_BAND - reduction)
        else:
            rnrb = self.RESIDENCE_NIL_RATE_BAND

        # RNRB limited to value of residence
        return min(rnrb, residence_value)

    def validate_nil_rate_bands(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Validate nil rate band amounts

        Reference: IHTA 1984, s7
        """
        issues = []

        text_lower = text.lower()

        # Find NRB mentions
        nrb_pattern = r'(?:nil\s+rate|nrb).*?£\s*(\d{1,3}(?:,\d{3})*)'

        for match in re.finditer(nrb_pattern, text_lower):
            amount_str = match.group(1).replace(',', '')
            try:
                stated_nrb = Decimal(amount_str)

                if stated_nrb != self.NIL_RATE_BAND:
                    issues.append({
                        'type': 'incorrect_nrb',
                        'severity': 'high',
                        'stated_amount': float(stated_nrb),
                        'correct_amount': float(self.NIL_RATE_BAND),
                        'message': f'Incorrect Nil Rate Band: stated £{stated_nrb}, should be £{self.NIL_RATE_BAND}',
                        'note': 'Frozen until April 2028',
                        'legal_reference': 'IHTA 1984, s7; FA 2024'
                    })
            except Exception:
                continue

        # Check RNRB
        rnrb_pattern = r'(?:residence|rnrb|home).*?£\s*(\d{1,3}(?:,\d{3})*)'

        for match in re.finditer(rnrb_pattern, text_lower):
            amount_str = match.group(1).replace(',', '')
            try:
                stated_rnrb = Decimal(amount_str)

                if stated_rnrb == Decimal('175000') or stated_rnrb == Decimal('175'):
                    # Correct
                    pass
                elif Decimal('100000') <= stated_rnrb <= Decimal('200000'):
                    issues.append({
                        'type': 'incorrect_rnrb',
                        'severity': 'high',
                        'stated_amount': float(stated_rnrb),
                        'correct_amount': float(self.RESIDENCE_NIL_RATE_BAND),
                        'message': f'Incorrect Residence NRB: stated £{stated_rnrb}, should be £{self.RESIDENCE_NIL_RATE_BAND}',
                        'note': 'Frozen until April 2028',
                        'legal_reference': 'IHTA 1984, s8D-8M'
                    })
            except Exception:
                continue

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'correct_nrb': float(self.NIL_RATE_BAND),
            'correct_rnrb': float(self.RESIDENCE_NIL_RATE_BAND)
        }

    def validate_iht_rates(self, text: str) -> Dict:
        """
        Validate IHT rates mentioned

        Reference: IHTA 1984, s7
        """
        issues = []

        text_lower = text.lower()

        # Find IHT rate mentions
        rate_pattern = r'(?:inheritance\s+tax|iht).*?(\d+(?:\.\d+)?)\s*%'

        for match in re.finditer(rate_pattern, text_lower):
            try:
                rate = Decimal(match.group(1))
            except Exception:
                continue

            # Valid IHT rates
            valid_rates = [self.MAIN_RATE, self.REDUCED_RATE, self.LIFETIME_RATE]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_iht_rate',
                    'severity': 'high',
                    'stated_rate': float(rate),
                    'valid_rates': [float(r) for r in valid_rates],
                    'message': f'Invalid IHT rate: {rate}%. Valid rates: 40%, 36% (charity), 20% (lifetime)',
                    'legal_reference': 'IHTA 1984, s7'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def validate_exemptions(self, text: str) -> Dict:
        """
        Validate exemption information

        Reference: IHTA 1984, Part II
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        # Spouse exemption
        if 'spouse' in text_lower or 'husband' in text_lower or 'wife' in text_lower:
            if not re.search(r'exempt|no\s+tax|unlimited', text_lower):
                warnings.append({
                    'type': 'spouse_exemption_not_mentioned',
                    'severity': 'medium',
                    'message': 'Spouse exemption not clearly stated',
                    'clarification': 'Gifts to spouse/civil partner are exempt from IHT',
                    'legal_reference': 'IHTA 1984, s18'
                })

        # Charity exemption
        if 'charity' in text_lower or 'charitable' in text_lower:
            if not re.search(r'exempt|no\s+tax|unlimited', text_lower):
                warnings.append({
                    'type': 'charity_exemption_not_mentioned',
                    'severity': 'medium',
                    'message': 'Charity exemption not clearly stated',
                    'clarification': 'Gifts to charity are exempt from IHT',
                    'legal_reference': 'IHTA 1984, s23'
                })

            # Check for reduced rate mention
            if not re.search(r'36\s*%|reduced\s+rate', text_lower):
                warnings.append({
                    'type': 'charity_reduced_rate_not_mentioned',
                    'severity': 'low',
                    'message': 'Consider mentioning 36% reduced rate',
                    'clarification': 'If 10%+ of estate to charity, IHT reduced to 36%',
                    'legal_reference': 'IHTA 1984, Schedule 1A'
                })

        # Annual exemption
        if 'annual' in text_lower and 'exempt' in text_lower:
            if not re.search(r'£3,?000|three\s+thousand', text_lower):
                issues.append({
                    'type': 'incorrect_annual_exemption',
                    'severity': 'medium',
                    'message': 'Annual exemption amount not correctly stated',
                    'correct_amount': '£3,000',
                    'note': 'Can carry forward unused exemption for 1 year',
                    'legal_reference': 'IHTA 1984, s19'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_seven_year_rule(self, text: str) -> Dict:
        """
        Validate seven-year rule and taper relief

        Reference: IHTA 1984, s3A, s7
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        seven_year_terms = ['seven year', '7 year', 'seven-year', '7-year', 'pet', 'potentially exempt']

        if any(term in text_lower for term in seven_year_terms):
            # Check for correct period
            if re.search(r'([3-6])\s+year', text_lower) and '7' not in text_lower:
                issues.append({
                    'type': 'incorrect_pet_period',
                    'severity': 'high',
                    'message': 'PET survival period incorrect',
                    'correct_period': '7 years',
                    'legal_reference': 'IHTA 1984, s3A'
                })

            # Check for taper relief mention
            if not re.search(r'taper|relief|reduce', text_lower):
                warnings.append({
                    'type': 'taper_relief_not_mentioned',
                    'severity': 'medium',
                    'message': 'Taper relief for gifts 3-7 years before death not mentioned',
                    'clarification': 'IHT reduced by 20%-80% for gifts made 3-7 years before death',
                    'legal_reference': 'IHTA 1984, s7(4)'
                })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def comprehensive_iht_check(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Run comprehensive IHT compliance check
        """
        results = {
            'nil_rate_bands': self.validate_nil_rate_bands(text, tax_year),
            'rates': self.validate_iht_rates(text),
            'exemptions': self.validate_exemptions(text),
            'seven_year_rule': self.validate_seven_year_rule(text)
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
