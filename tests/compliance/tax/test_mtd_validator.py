"""Tests for MTD Validator"""
import pytest
from decimal import Decimal
from backend.compliance.tax.mtd_validator import MTDValidator


class TestMTDValidator:
    def setup_method(self):
        self.validator = MTDValidator()

    def test_vat_mtd_mandatory(self):
        """Test MTD for VAT mandatory status"""
        text = "MTD for VAT is optional for small businesses"
        result = self.validator.validate_vat_mtd_compliance(text, vat_registered=True)

        assert not result['compliant']
        assert len(result['issues']) > 0
        assert any('mandatory' in issue['message'].lower() for issue in result['issues'])

    def test_vat_mtd_paper_returns(self):
        """Test paper return error detection"""
        text = "You can submit your VAT return by paper"
        result = self.validator.validate_vat_mtd_compliance(text, vat_registered=True)

        assert not result['compliant']
        assert any('paper' in issue['message'].lower() for issue in result['issues'])

    def test_vat_mtd_compliant(self):
        """Test compliant MTD statement"""
        text = """All VAT-registered businesses must use Making Tax Digital.
        Digital records must be kept and submitted via MTD-compatible software."""
        result = self.validator.validate_vat_mtd_compliance(text, vat_registered=True)

        assert result['compliant'] or len(result['issues']) == 0

    def test_itsa_mtd_thresholds(self):
        """Test MTD for ITSA threshold validation"""
        text = "MTD for ITSA applies from April 2024"
        result = self.validator.validate_itsa_mtd_compliance(text)

        assert not result['compliant']
        assert any('2026' in issue.get('correction', '') or '2027' in issue.get('correction', '')
                  for issue in result['issues'])

    def test_itsa_correct_thresholds(self):
        """Test correct ITSA thresholds"""
        text = "MTD for ITSA: £50,000+ from April 2026, £30,000+ from April 2027"
        result = self.validator.validate_itsa_mtd_compliance(text)

        assert result['compliant'] or len(result['issues']) == 0

    def test_digital_records_requirement(self):
        """Test digital records validation"""
        text = "We keep paper records for our VAT"
        result = self.validator.validate_digital_records_requirement(text)

        assert not result['compliant']
        assert len(result['issues']) > 0

    def test_digital_links_manual_intervention(self):
        """Test digital links validation"""
        text = "Data is manually entered from spreadsheet to software"
        result = self.validator.validate_digital_links(text)

        assert not result['compliant']
        assert any('manual' in issue['message'].lower() for issue in result['issues'])

    def test_comprehensive_check(self):
        """Test comprehensive MTD check"""
        text = """MTD for VAT is mandatory. All businesses must keep digital records,
        use digital links, and submit via compatible software."""
        result = self.validator.comprehensive_mtd_check(text, vat_registered=True)

        assert 'overall_compliant' in result
        assert 'total_issues' in result
        assert 'detailed_results' in result
