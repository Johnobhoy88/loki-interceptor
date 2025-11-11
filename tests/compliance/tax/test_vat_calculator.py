"""Tests for VAT Calculator"""
import pytest
from decimal import Decimal
from backend.compliance.tax.vat_calculator import VATCalculator, VATRate


class TestVATCalculator:
    def setup_method(self):
        self.calc = VATCalculator()

    def test_standard_rate_calculation(self):
        """Test standard rate VAT calculation"""
        result = self.calc.calculate_vat(
            Decimal('100.00'),
            VATRate.STANDARD
        )

        assert result['net'] == Decimal('100.00')
        assert result['vat'] == Decimal('20.00')
        assert result['gross'] == Decimal('120.00')
        assert result['rate_percentage'] == Decimal('20.00')

    def test_reduced_rate_calculation(self):
        """Test reduced rate VAT calculation"""
        result = self.calc.calculate_vat(
            Decimal('100.00'),
            VATRate.REDUCED
        )

        assert result['vat'] == Decimal('5.00')
        assert result['gross'] == Decimal('105.00')

    def test_zero_rate_calculation(self):
        """Test zero rate VAT calculation"""
        result = self.calc.calculate_vat(
            Decimal('100.00'),
            VATRate.ZERO
        )

        assert result['vat'] == Decimal('0.00')
        assert result['gross'] == Decimal('100.00')

    def test_calculate_from_gross(self):
        """Test calculating VAT from gross amount"""
        result = self.calc.calculate_vat_from_gross(
            Decimal('120.00'),
            VATRate.STANDARD
        )

        assert result['net'] == Decimal('100.00')
        assert result['vat'] == Decimal('20.00')

    def test_invalid_vat_rate(self):
        """Test invalid VAT rate detection"""
        text = "VAT at 17.5% will be charged"
        result = self.calc.validate_vat_rate(text)

        assert not result['valid']
        assert len(result['issues']) > 0

    def test_valid_vat_rates(self):
        """Test valid VAT rates"""
        text = "Standard rate 20%, Reduced rate 5%, Zero rate 0%"
        result = self.calc.validate_vat_rate(text)

        assert result['valid']

    def test_registration_threshold_2024_25(self):
        """Test VAT registration threshold for 2024/25"""
        text = "VAT registration threshold is £85,000"
        result = self.calc.validate_vat_registration_threshold(text, "2024/25")

        assert not result['valid']
        assert result['correct_threshold'] == 90000.0

    def test_correct_registration_threshold(self):
        """Test correct VAT registration threshold"""
        text = "VAT registration threshold is £90,000 for 2024/25"
        result = self.calc.validate_vat_registration_threshold(text, "2024/25")

        assert result['valid'] or len(result['issues']) == 0

    def test_flat_rate_scheme_validation(self):
        """Test Flat Rate Scheme validation"""
        text = "Flat Rate Scheme available with turnover of £200,000"
        result = self.calc.validate_flat_rate_scheme(text)

        assert len(result['issues']) > 0

    def test_flat_rate_within_limit(self):
        """Test Flat Rate Scheme within limits"""
        text = "Flat Rate Scheme for business with £100,000 turnover"
        result = self.calc.validate_flat_rate_scheme(text)

        assert result['valid'] or len(result['issues']) == 0

    def test_vat_category_determination(self):
        """Test VAT category determination"""

        # Food (zero-rated)
        result = self.calc.determine_vat_category("Fresh food supplies")
        assert result['rate'] == VATRate.ZERO

        # Domestic fuel (reduced rate)
        result = self.calc.determine_vat_category("Domestic electricity")
        assert result['rate'] == VATRate.REDUCED

        # Insurance (exempt)
        result = self.calc.determine_vat_category("Insurance services")
        assert result['rate'] == VATRate.EXEMPT

        # General goods (standard)
        result = self.calc.determine_vat_category("Office furniture")
        assert result['rate'] == VATRate.STANDARD
