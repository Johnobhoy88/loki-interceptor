"""
VAT Calculator and Validator
Comprehensive VAT validation for UK tax compliance

Legal References:
- VAT Act 1994
- Value Added Tax Regulations 1995
- HMRC Notice 700: The VAT Guide
- HMRC Notice 700/1: Who should be registered for VAT?
- Finance Act 2024 - VAT rate confirmations

2024/25 Rates:
- Standard rate: 20%
- Reduced rate: 5%
- Zero rate: 0%
- Registration threshold: £90,000 (from April 2024)
- Deregistration threshold: £88,000
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from enum import Enum


class VATRate(Enum):
    """VAT rate categories"""
    STANDARD = Decimal('20.00')
    REDUCED = Decimal('5.00')
    ZERO = Decimal('0.00')
    EXEMPT = None


class VATScheme(Enum):
    """VAT accounting schemes"""
    STANDARD = "standard"
    CASH_ACCOUNTING = "cash_accounting"
    FLAT_RATE = "flat_rate"
    ANNUAL_ACCOUNTING = "annual_accounting"
    RETAIL = "retail"


class VATCalculator:
    """VAT calculation and validation"""

    # Current thresholds (2024/25)
    REGISTRATION_THRESHOLD = Decimal('90000.00')  # From April 2024
    DEREGISTRATION_THRESHOLD = Decimal('88000.00')
    DISTANCE_SELLING_THRESHOLD = Decimal('8818.00')  # Northern Ireland only

    # Historical thresholds for validation
    HISTORICAL_THRESHOLDS = {
        '2024/25': Decimal('90000.00'),
        '2023/24': Decimal('85000.00'),
        '2022/23': Decimal('85000.00'),
        '2021/22': Decimal('85000.00'),
    }

    # VAT rates
    STANDARD_RATE = Decimal('20.00')
    REDUCED_RATE = Decimal('5.00')
    ZERO_RATE = Decimal('0.00')

    # Flat Rate Scheme percentages (2024/25)
    FLAT_RATE_PERCENTAGES = {
        'accounting': Decimal('14.5'),
        'advertising': Decimal('11.0'),
        'agriculture': Decimal('6.5'),
        'architect': Decimal('14.5'),
        'boarding_kennel': Decimal('12.0'),
        'business_services': Decimal('12.0'),
        'catering': Decimal('12.5'),
        'computer_repair': Decimal('10.5'),
        'computer_services': Decimal('14.5'),
        'construction': Decimal('9.5'),
        'entertainment': Decimal('13.5'),
        'farming': Decimal('6.5'),
        'financial_services': Decimal('13.5'),
        'hairdressing': Decimal('13.0'),
        'hotel': Decimal('10.5'),
        'investigation_security': Decimal('12.0'),
        'labour_only': Decimal('14.5'),
        'laundry': Decimal('12.0'),
        'lawyer': Decimal('14.5'),
        'library': Decimal('9.5'),
        'management_consultant': Decimal('14.0'),
        'manufacturing': Decimal('9.5'),
        'membership_org': Decimal('8.0'),
        'mining': Decimal('10.0'),
        'packing': Decimal('9.0'),
        'photography': Decimal('11.0'),
        'post_office': Decimal('5.0'),
        'printer': Decimal('8.5'),
        'publishing': Decimal('11.0'),
        'real_estate': Decimal('14.0'),
        'repairing_vehicles': Decimal('8.5'),
        'retailing_food': Decimal('4.0'),
        'retailing_pharmacy': Decimal('8.0'),
        'retailing': Decimal('7.5'),
        'secretarial': Decimal('13.0'),
        'social_work': Decimal('11.0'),
        'sport': Decimal('8.5'),
        'transport': Decimal('10.0'),
        'travel_agency': Decimal('10.5'),
        'veterinary': Decimal('11.0'),
        'wholesaling_food': Decimal('9.5'),
        'wholesaling': Decimal('8.5'),
    }

    def __init__(self):
        self.legal_source = "VAT Act 1994; HMRC Notice 700"

    def calculate_vat(
        self,
        net_amount: Decimal,
        rate: VATRate = VATRate.STANDARD,
        round_result: bool = True
    ) -> Dict:
        """
        Calculate VAT amount

        Args:
            net_amount: Net amount (excluding VAT)
            rate: VAT rate to apply
            round_result: Round to 2 decimal places

        Returns:
            Dictionary with VAT amount and gross amount
        """
        if rate == VATRate.EXEMPT:
            return {
                'net': net_amount,
                'vat': Decimal('0.00'),
                'gross': net_amount,
                'rate': 'Exempt',
                'rate_percentage': None
            }

        rate_decimal = rate.value / Decimal('100')
        vat_amount = net_amount * rate_decimal

        if round_result:
            vat_amount = vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        gross_amount = net_amount + vat_amount

        return {
            'net': net_amount,
            'vat': vat_amount,
            'gross': gross_amount,
            'rate': rate.name,
            'rate_percentage': rate.value
        }

    def calculate_vat_from_gross(
        self,
        gross_amount: Decimal,
        rate: VATRate = VATRate.STANDARD
    ) -> Dict:
        """
        Calculate VAT and net from gross amount

        Args:
            gross_amount: Gross amount (including VAT)
            rate: VAT rate applied

        Returns:
            Dictionary with net amount and VAT amount
        """
        if rate == VATRate.EXEMPT:
            return {
                'net': gross_amount,
                'vat': Decimal('0.00'),
                'gross': gross_amount,
                'rate': 'Exempt',
                'rate_percentage': None
            }

        rate_decimal = rate.value / Decimal('100')
        vat_multiplier = Decimal('1') + rate_decimal

        net_amount = gross_amount / vat_multiplier
        vat_amount = gross_amount - net_amount

        # Round to 2 decimal places
        net_amount = net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        vat_amount = vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'net': net_amount,
            'vat': vat_amount,
            'gross': gross_amount,
            'rate': rate.name,
            'rate_percentage': rate.value
        }

    def validate_vat_rate(self, text: str) -> Dict:
        """
        Validate VAT rates mentioned in text

        Reference: VAT Act 1994, Schedule 7A, 8, 9
        """
        issues = []
        mentions = []

        # Find VAT rate mentions
        rate_pattern = r'(?:vat|tax).*?(\d+(?:\.\d+)?)\s*%|(\d+(?:\.\d+)?)\s*%.*?(?:vat|tax)'

        for match in re.finditer(rate_pattern, text, re.IGNORECASE):
            rate_str = match.group(1) or match.group(2)
            try:
                rate = Decimal(rate_str)
            except Exception:
                continue

            mention = {
                'rate': rate,
                'text': match.group(0),
                'position': (match.start(), match.end())
            }

            # Check if rate is valid
            valid_rates = [
                self.STANDARD_RATE,
                self.REDUCED_RATE,
                self.ZERO_RATE
            ]

            if rate not in valid_rates:
                issues.append({
                    'type': 'invalid_vat_rate',
                    'severity': 'high',
                    'rate': float(rate),
                    'message': f'Invalid VAT rate: {rate}%',
                    'valid_rates': [float(r) for r in valid_rates],
                    'legal_reference': 'VAT Act 1994, Schedule 7A'
                })

            mentions.append(mention)

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'mentions': mentions
        }

    def validate_vat_registration_threshold(
        self,
        text: str,
        tax_year: str = "2024/25"
    ) -> Dict:
        """
        Validate VAT registration threshold mentions

        Reference: VAT Act 1994, Schedule 1; HMRC Notice 700/1
        """
        issues = []

        text_lower = text.lower()

        # Find threshold mentions
        threshold_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:k)?)'

        thresholds_found = []
        for match in re.finditer(threshold_pattern, text_lower):
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

        # Get correct threshold for tax year
        correct_threshold = self.HISTORICAL_THRESHOLDS.get(
            tax_year,
            self.REGISTRATION_THRESHOLD
        )

        # Check for registration/threshold keywords nearby
        if 'registration' in text_lower or 'threshold' in text_lower:
            for threshold_data in thresholds_found:
                if threshold_data['amount'] != correct_threshold:
                    issues.append({
                        'type': 'incorrect_vat_threshold',
                        'severity': 'high',
                        'stated_threshold': float(threshold_data['amount']),
                        'correct_threshold': float(correct_threshold),
                        'tax_year': tax_year,
                        'message': f'Incorrect VAT threshold: stated £{threshold_data["amount"]}, should be £{correct_threshold} for {tax_year}',
                        'legal_reference': 'VAT Act 1994, Schedule 1, Para 1'
                    })

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'correct_threshold': float(correct_threshold),
            'tax_year': tax_year
        }

    def determine_vat_category(self, goods_or_services: str) -> Dict:
        """
        Determine likely VAT category for goods/services

        Reference: VAT Act 1994, Schedules 7A, 8, 9
        """

        text_lower = goods_or_services.lower()

        # Zero-rated items (0%)
        zero_rated_keywords = [
            'food', 'book', 'newspaper', 'magazine', 'children.*cloth',
            'children.*shoe', 'children.*boot', 'disabled.*equipment',
            'motorcycle helmet', 'bike helmet', 'prescription',
            'export', 'international.*service'
        ]

        # Reduced rate items (5%)
        reduced_rate_keywords = [
            'domestic.*fuel', 'domestic.*power', 'electricity.*domestic',
            'gas.*domestic', 'children.*car.*seat', 'mobility aid',
            'home.*energy', 'smoking.*cessation', 'nicotine.*replacement',
            'contraceptive'
        ]

        # Exempt items
        exempt_keywords = [
            'insurance', 'finance', 'financial.*service', 'loan',
            'credit', 'education', 'training.*course', 'health.*service',
            'medical.*service', 'doctor', 'hospital', 'dental',
            'postal.*service', 'stamp', 'burial', 'cremation',
            'gambling', 'lottery', 'betting'
        ]

        # Check categories
        for keyword in zero_rated_keywords:
            if re.search(keyword, text_lower):
                return {
                    'category': 'zero_rated',
                    'rate': VATRate.ZERO,
                    'rate_percentage': 0.0,
                    'schedule': 'Schedule 8 (Zero-rated)',
                    'note': 'Zero-rated supply - VAT at 0%'
                }

        for keyword in reduced_rate_keywords:
            if re.search(keyword, text_lower):
                return {
                    'category': 'reduced_rate',
                    'rate': VATRate.REDUCED,
                    'rate_percentage': 5.0,
                    'schedule': 'Schedule 7A (Reduced rate)',
                    'note': 'Reduced rate supply - VAT at 5%'
                }

        for keyword in exempt_keywords:
            if re.search(keyword, text_lower):
                return {
                    'category': 'exempt',
                    'rate': VATRate.EXEMPT,
                    'rate_percentage': None,
                    'schedule': 'Schedule 9 (Exempt)',
                    'note': 'Exempt supply - no VAT charged or recovered'
                }

        # Default: standard rate
        return {
            'category': 'standard_rated',
            'rate': VATRate.STANDARD,
            'rate_percentage': 20.0,
            'schedule': 'Standard rate',
            'note': 'Standard rate supply - VAT at 20%'
        }

    def validate_flat_rate_scheme(
        self,
        text: str,
        business_category: Optional[str] = None
    ) -> Dict:
        """
        Validate Flat Rate Scheme information

        Reference: HMRC Notice 733: Flat Rate Scheme
        """
        issues = []
        warnings = []

        text_lower = text.lower()

        if 'flat rate' not in text_lower:
            return {'applicable': False}

        # Check turnover limit (£150,000)
        FLAT_RATE_LIMIT = Decimal('150000.00')

        turnover_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:k)?)'
        for match in re.finditer(turnover_pattern, text):
            turnover_str = match.group(1).replace(',', '').replace('k', '000')
            try:
                turnover = Decimal(turnover_str)
                if turnover > FLAT_RATE_LIMIT:
                    if 'flat rate' in text_lower[max(0, match.start()-100):match.end()+100].lower():
                        issues.append({
                            'type': 'flat_rate_turnover_exceeded',
                            'severity': 'high',
                            'turnover': float(turnover),
                            'limit': float(FLAT_RATE_LIMIT),
                            'message': 'Flat Rate Scheme only available for turnover up to £150,000',
                            'legal_reference': 'HMRC Notice 733, Section 4'
                        })
            except Exception:
                continue

        # Check limited cost trader status (16.5% rate)
        if 'limited cost trader' in text_lower or '16.5%' in text_lower:
            warnings.append({
                'type': 'limited_cost_trader',
                'severity': 'medium',
                'message': 'Limited Cost Trader flat rate (16.5%) applies if goods cost less than 2% of turnover or £1,000/year',
                'legal_reference': 'HMRC Notice 733, Section 6.5'
            })

        # Validate flat rate percentage if business category known
        if business_category and business_category in self.FLAT_RATE_PERCENTAGES:
            correct_rate = self.FLAT_RATE_PERCENTAGES[business_category]

            rate_pattern = r'(\d+(?:\.\d+)?)\s*%'
            for match in re.finditer(rate_pattern, text):
                try:
                    stated_rate = Decimal(match.group(1))
                    if abs(stated_rate - correct_rate) > Decimal('0.1'):
                        issues.append({
                            'type': 'incorrect_flat_rate',
                            'severity': 'medium',
                            'stated_rate': float(stated_rate),
                            'correct_rate': float(correct_rate),
                            'business_category': business_category,
                            'message': f'Flat rate should be {correct_rate}% for {business_category}',
                            'legal_reference': 'HMRC Notice 733, Section 6'
                        })
                except Exception:
                    continue

        return {
            'applicable': True,
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

    def validate_vat_invoice_requirements(self, text: str) -> Dict:
        """
        Validate VAT invoice requirements

        Reference: VAT Act 1994, s13; HMRC Notice 700, Section 16
        """
        issues = []

        text_lower = text.lower()

        if 'invoice' not in text_lower and 'receipt' not in text_lower:
            return {'applicable': False}

        # Required elements for full VAT invoice
        required_elements = {
            'unique_number': (r'(?:invoice|receipt)\s+(?:number|no\.?|#)', 'Unique sequential invoice number'),
            'supplier_name': (r'(?:supplier|seller|vendor|from).*name', 'Supplier name and address'),
            'supplier_vat': (r'vat\s+(?:registration\s+)?(?:number|no\.?)', 'Supplier VAT registration number'),
            'customer_name': (r'(?:customer|buyer|bill\s+to|sold\s+to)', 'Customer name and address'),
            'date': (r'(?:date|dated|issued)', 'Tax point (date of supply)'),
            'description': (r'description|item|product|service', 'Description of goods/services'),
            'unit_price': (r'(?:unit\s+)?price|rate|cost', 'Unit price excluding VAT'),
            'vat_rate': (r'vat\s+rate|rate\s+of\s+vat', 'VAT rate for each item'),
            'vat_amount': (r'vat\s+amount|vat\s+charged', 'VAT amount for each rate'),
            'total': (r'total|amount\s+(?:due|payable)', 'Total amount payable')
        }

        missing_elements = []
        for element_name, (pattern, description) in required_elements.items():
            if not re.search(pattern, text_lower):
                missing_elements.append(description)

        if missing_elements and len(missing_elements) >= 3:
            issues.append({
                'type': 'incomplete_vat_invoice',
                'severity': 'high',
                'missing_elements': missing_elements,
                'message': 'VAT invoice missing required elements',
                'legal_reference': 'VAT Act 1994, Section 13; HMRC Notice 700, Section 16.3'
            })

        # Check for simplified invoice conditions (under £250)
        simplified_pattern = r'(?:simplified|less detailed).*invoice'
        if re.search(simplified_pattern, text_lower):
            amount_pattern = r'£\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            for match in re.finditer(amount_pattern, text):
                try:
                    amount = Decimal(match.group(1).replace(',', ''))
                    if amount > Decimal('250.00'):
                        issues.append({
                            'type': 'simplified_invoice_limit_exceeded',
                            'severity': 'medium',
                            'amount': float(amount),
                            'limit': 250.00,
                            'message': 'Simplified VAT invoice only allowed for supplies under £250',
                            'legal_reference': 'HMRC Notice 700, Section 16.4'
                        })
                except Exception:
                    continue

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def comprehensive_vat_check(self, text: str, tax_year: str = "2024/25") -> Dict:
        """
        Run comprehensive VAT compliance check
        """
        results = {
            'rate_validation': self.validate_vat_rate(text),
            'threshold_validation': self.validate_vat_registration_threshold(text, tax_year),
            'flat_rate_validation': self.validate_flat_rate_scheme(text),
            'invoice_validation': self.validate_vat_invoice_requirements(text)
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
