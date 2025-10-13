"""
Gold Standard Edge Case Tests for UK Tax Module
Tests all 15 HMRC/tax compliance gates with optimized trigger patterns
"""

import sys
sys.path.insert(0, '/mnt/c/Users/jpmcm.DESKTOP-CQ0CL93/OneDrive/Desktop/HighlandAI/LOKI_INTERCEPTOR_CLAUDEV1/backend')

from modules.tax_uk.gates.allowable_expenses import AllowableExpensesGate
from modules.tax_uk.gates.business_structure_consistency import BusinessStructureConsistencyGate
from modules.tax_uk.gates.capital_revenue_distinction import CapitalRevenueDistinctionGate
from modules.tax_uk.gates.company_limited_suffix import CompanyLimitedSuffixGate
from modules.tax_uk.gates.hmrc_scam_detection import HmrcScamDetectionGate
from modules.tax_uk.gates.invoice_legal_requirements import InvoiceLegalRequirementsGate
from modules.tax_uk.gates.invoice_numbering import InvoiceNumberingGate
from modules.tax_uk.gates.mtd_compliance import MtdComplianceGate
from modules.tax_uk.gates.payment_method_validation import PaymentMethodValidationGate
from modules.tax_uk.gates.scottish_tax_specifics import ScottishTaxSpecificsGate
from modules.tax_uk.gates.tax_deadline_accuracy import TaxDeadlineAccuracyGate
from modules.tax_uk.gates.vat_invoice_integrity import VatInvoiceIntegrityGate
from modules.tax_uk.gates.vat_number_format import VatNumberFormatGate
from modules.tax_uk.gates.vat_rate_accuracy import VatRateAccuracyGate
from modules.tax_uk.gates.vat_threshold import VatThresholdGate


class TestTaxGatesGoldStandard:
    """Gold standard tests for all tax gates"""

    def test_allowable_expenses_gold(self):
        """GOLD: Non-allowable expense being claimed"""
        gate = AllowableExpensesGate()
        text = """
        Business Expense Report 2024

        We can claim client entertainment expenses for dinners with prospective customers.
        Also claiming commuting costs for daily travel from home to office.
        Personal clothing for work meetings is allowable.
        """
        result = gate.check(text, "expense_report")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ Allowable Expenses: {result['status']} - {result.get('message')}")

    def test_business_structure_consistency_gold(self):
        """GOLD: Terminology mismatch (sole trader called director)"""
        gate = BusinessStructureConsistencyGate()
        text = """
        Business Structure Guide

        As a sole trader, you are a director of your business and pay corporation tax.
        You can take drawings from the company like other directors do.
        """
        result = gate.check(text, "guide")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}: {result.get('message')}"
        print(f"✓ Business Structure: {result['status']} - {result.get('message')}")

    def test_capital_revenue_distinction_gold(self):
        """GOLD: Capital item treated as revenue expense"""
        gate = CapitalRevenueDistinctionGate()
        text = """
        Tax Planning Advice

        You can claim the full cost of the new company car as an expense this year.
        Equipment purchases like laptops are fully deductible as business expenses.
        Building improvements can be claimed in full as allowable expenses.
        """
        result = gate.check(text, "tax_advice")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ Capital/Revenue: {result['status']} - {result.get('message')}")

    def test_company_limited_suffix_gold(self):
        """GOLD: Company name missing Ltd suffix"""
        gate = CompanyLimitedSuffixGate()
        text = """
        Invoice
        From: Highland Trading Company
        Business Solutions Provider
        """
        result = gate.check(text, "invoice")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}: {result.get('message')}"
        print(f"✓ Company Suffix: {result['status']} - {result.get('message')}")

    def test_hmrc_scam_detection_gold(self):
        """GOLD: HMRC scam with gift card payment"""
        gate = HmrcScamDetectionGate()
        text = """
        URGENT: HMRC Tax Refund

        You have a tax refund of £856. To claim, purchase iTunes gift cards worth £100
        and send the codes to us immediately. Legal action will be taken if you don't
        respond within 24 hours.
        """
        result = gate.check(text, "email")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ HMRC Scam: {result['status']} - {result.get('message')}")

    def test_invoice_legal_requirements_gold(self):
        """GOLD: Invoice missing mandatory fields"""
        gate = InvoiceLegalRequirementsGate()
        text = """
        Invoice

        Some services provided
        £500
        """
        result = gate.check(text, "invoice")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ Invoice Legal: {result['status']} - {result.get('message')}")

    def test_invoice_numbering_gold(self):
        """GOLD: Invoice sequence with gaps"""
        gate = InvoiceNumberingGate()
        text = """
        Previous Invoices:
        Invoice No: INV-1001
        Invoice No: INV-1002
        Invoice No: INV-1005
        Invoice No: INV-1006
        """
        result = gate.check(text, "invoice_list")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}: {result.get('message')}"
        print(f"✓ Invoice Numbering: {result['status']} - {result.get('message')}")

    def test_mtd_compliance_gold(self):
        """GOLD: Outdated MTD information (claiming it's optional)"""
        gate = MtdComplianceGate()
        text = """
        Making Tax Digital for VAT

        MTD is voluntary and not required for most businesses. You can continue
        filing paper VAT returns if you prefer the traditional method.
        """
        result = gate.check(text, "guidance")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ MTD Compliance: {result['status']} - {result.get('message')}")

    def test_payment_method_validation_gold(self):
        """GOLD: Suspicious payment request (gift cards)"""
        gate = PaymentMethodValidationGate()
        text = """
        HMRC Payment Instructions

        Please pay your tax bill using Amazon gift cards or Google Play vouchers.
        Send the codes to this email address.
        """
        result = gate.check(text, "payment_request")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ Payment Method: {result['status']} - {result.get('message')}")

    def test_scottish_tax_specifics_gold(self):
        """GOLD: Scottish tax mentioned without rate clarification"""
        gate = ScottishTaxSpecificsGate()
        text = """
        Tax Information for Scotland

        Scottish residents pay income tax at the same rates as the rest of the UK.
        The tax bands are identical.
        """
        result = gate.check(text, "tax_guide")
        assert result['status'] in ['FAIL', 'WARNING'], f"Expected FAIL/WARNING, got {result['status']}: {result.get('message')}"
        print(f"✓ Scottish Tax: {result['status']} - {result.get('message')}")

    def test_tax_deadline_accuracy_gold(self):
        """GOLD: Incorrect self-assessment deadline"""
        gate = TaxDeadlineAccuracyGate()
        text = """
        Self-Assessment Deadlines

        Online return filing deadline is 30th November.
        Paper return filing is due by 15th December.
        Payment is due by 28th February.
        """
        result = gate.check(text, "deadline_guide")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ Tax Deadlines: {result['status']} - {result.get('message')}")

    def test_vat_invoice_integrity_gold(self):
        """GOLD: VAT invoice missing mandatory fields"""
        gate = VatInvoiceIntegrityGate()
        text = """
        Invoice

        Some products sold
        Total: £120.00
        """
        result = gate.check(text, "vat_invoice")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ VAT Invoice: {result['status']} - {result.get('message')}")

    def test_vat_number_format_gold(self):
        """GOLD: Invalid VAT number format"""
        gate = VatNumberFormatGate()
        text = """
        Company Details

        VAT Registration Number: GB12345
        Please quote this on all correspondence.
        """
        result = gate.check(text, "company_info")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ VAT Number: {result['status']} - {result.get('message')}")

    def test_vat_rate_accuracy_gold(self):
        """GOLD: Incorrect VAT rate"""
        gate = VatRateAccuracyGate()
        text = """
        VAT Information

        Standard VAT rate is 17.5%
        All sales are subject to this rate.
        """
        result = gate.check(text, "vat_guide")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ VAT Rate: {result['status']} - {result.get('message')}")

    def test_vat_threshold_gold(self):
        """GOLD: Outdated VAT threshold"""
        gate = VatThresholdGate()
        text = """
        VAT Registration Guide

        You must register for VAT if your turnover exceeds the threshold of £85,000
        in a rolling 12-month period.
        """
        result = gate.check(text, "vat_guide")
        assert result['status'] in ['FAIL'], f"Expected FAIL, got {result['status']}: {result.get('message')}"
        print(f"✓ VAT Threshold: {result['status']} - {result.get('message')}")


def main():
    """Run all gold standard tests"""
    print("=" * 80)
    print("TAX MODULE GOLD STANDARD TESTS")
    print("=" * 80)
    print()

    test_suite = TestTaxGatesGoldStandard()

    tests = [
        ("test_allowable_expenses_gold", "Allowable Expenses"),
        ("test_business_structure_consistency_gold", "Business Structure"),
        ("test_capital_revenue_distinction_gold", "Capital/Revenue"),
        ("test_company_limited_suffix_gold", "Company Suffix"),
        ("test_hmrc_scam_detection_gold", "HMRC Scam"),
        ("test_invoice_legal_requirements_gold", "Invoice Legal"),
        ("test_invoice_numbering_gold", "Invoice Numbering"),
        ("test_mtd_compliance_gold", "MTD Compliance"),
        ("test_payment_method_validation_gold", "Payment Method"),
        ("test_scottish_tax_specifics_gold", "Scottish Tax"),
        ("test_tax_deadline_accuracy_gold", "Tax Deadlines"),
        ("test_vat_invoice_integrity_gold", "VAT Invoice"),
        ("test_vat_number_format_gold", "VAT Number"),
        ("test_vat_rate_accuracy_gold", "VAT Rate"),
        ("test_vat_threshold_gold", "VAT Threshold"),
    ]

    passed = 0
    failed = 0

    for test_method, test_name in tests:
        try:
            getattr(test_suite, test_method)()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_name}: FAILED - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {str(e)}")
            failed += 1

    print()
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(tests)} tests passing ({100*passed//len(tests)}%)")
    print("=" * 80)

    if failed > 0:
        print(f"\n⚠️  {failed} test(s) need gate enhancements")
        return 1
    else:
        print("\n✅ 100% GOLD STANDARD ACHIEVED!")
        return 0


if __name__ == "__main__":
    exit(main())
