import re

from modules.tax_uk.gates.vat_number_format import VatNumberFormatGate
from modules.tax_uk.gates.vat_rate_accuracy import VatRateAccuracyGate
from modules.tax_uk.gates.vat_threshold import VatThresholdGate
from modules.tax_uk.gates.vat_invoice_integrity import VatInvoiceIntegrityGate
from modules.tax_uk.gates.invoice_legal_requirements import InvoiceLegalRequirementsGate
from modules.tax_uk.gates.company_limited_suffix import CompanyLimitedSuffixGate
from modules.tax_uk.gates.tax_deadline_accuracy import TaxDeadlineAccuracyGate
from modules.tax_uk.gates.mtd_compliance import MtdComplianceGate
from modules.tax_uk.gates.allowable_expenses import AllowableExpensesGate
from modules.tax_uk.gates.capital_revenue_distinction import CapitalRevenueDistinctionGate
from modules.tax_uk.gates.business_structure_consistency import BusinessStructureConsistencyGate
from modules.tax_uk.gates.hmrc_scam_detection import HmrcScamDetectionGate
from modules.tax_uk.gates.scottish_tax_specifics import ScottishTaxSpecificsGate
from modules.tax_uk.gates.invoice_numbering import InvoiceNumberingGate
from modules.tax_uk.gates.payment_method_validation import PaymentMethodValidationGate


def test_vat_number_format():
    gate = VatNumberFormatGate()
    # PASS
    assert gate.check("VAT No: GB123456789", "invoice")["status"] == "PASS"
    # FAIL
    r = gate.check("VAT: 12345678", "invoice")
    assert r["status"] == "FAIL" and r["severity"] == "critical"
    assert isinstance(r.get("spans"), list)
    # N/A
    assert gate.check("This has no tax content", "letter")["status"] == "N/A"


def test_vat_rate_accuracy():
    gate = VatRateAccuracyGate()
    # PASS
    assert gate.check("VAT charged at 20%", "invoice")["status"] == "PASS"
    # FAIL invalid rate
    r = gate.check("VAT rate is 17%.", "invoice")
    assert r["status"] == "FAIL" and r["severity"] == "high"
    # N/A
    assert gate.check("No rates here", "memo")["status"] == "N/A"


def test_vat_threshold():
    gate = VatThresholdGate()
    # PASS (correct threshold)
    assert gate.check("register for VAT if turnover exceeds £90,000", "info")["status"] == "PASS"
    # FAIL incorrect threshold
    r = gate.check("You must register if turnover exceeds £85,000 threshold", "info")
    assert r["status"] == "FAIL" and r["severity"] == "critical"
    # N/A
    assert gate.check("We discuss sales figures only", "report")["status"] == "N/A"


def test_vat_invoice_integrity():
    gate = VatInvoiceIntegrityGate()
    # PASS: include required fields
    text = (
        "Invoice Number: 12345\n"
        "VAT Registration Number: GB123456789\n"
        "Date: 01/02/2024\n"
        "From Supplier Ltd\n"
        "To Customer Ltd\n"
        "VAT 20%\n"
        "Net Subtotal\n"
        "VAT Amount: £20\n"
        "Total £120\n"
    )
    assert gate.check(text, "invoice")["status"] == "PASS"
    # FAIL: VAT context but missing fields
    r = gate.check("VAT invoice", "invoice")
    assert r["status"] == "FAIL" and r["severity"] == "critical"
    # N/A
    assert gate.check("Quote document", "quote")["status"] == "N/A"


def test_invoice_legal_requirements():
    gate = InvoiceLegalRequirementsGate()
    # PASS
    text = (
        "Invoice No: 10001\nfrom Supplier Ltd\n123 High Street\n"
        "to Customer Ltd\ndate 01/02/2024\ndescription Services\ntotal £123"
    )
    assert gate.check(text, "invoice")["status"] == "PASS"
    # FAIL
    r = gate.check("Invoice issued to customer without totals", "invoice")
    assert r["status"] == "FAIL" and r["severity"] == "high"
    # N/A
    assert gate.check("Meeting minutes", "notes")["status"] == "N/A"


def test_company_limited_suffix():
    gate = CompanyLimitedSuffixGate()
    # WARNING (missing suffix)
    r = gate.check("ABC Trading Invoice", "invoice")
    assert r["status"] == "WARNING"
    # PASS (with suffix nearby)
    assert gate.check("ABC Ltd Invoice", "invoice")["status"] == "PASS"
    # N/A
    assert gate.check("Memo text only", "memo")["status"] == "N/A"


def test_tax_deadline_accuracy():
    gate = TaxDeadlineAccuracyGate()
    # FAIL cases
    r = gate.check("Self-assessment deadline 30 Jan", "notice")
    assert r["status"] == "FAIL"
    r = gate.check("Corporation tax payment due 6 months", "notice")
    assert r["status"] == "FAIL"
    # PASS (no errors stated)
    assert gate.check("General info only", "memo")["status"] == "PASS"


def test_mtd_compliance():
    gate = MtdComplianceGate()
    # FAIL (claims optional/paper)
    r = gate.check("MTD for VAT is optional. Paper VAT returns allowed.", "info")
    assert r["status"] == "FAIL" and r["severity"] == "high"
    # PASS
    assert gate.check("MTD for VAT is mandatory and uses software.", "info")["status"] == "PASS"
    # N/A
    assert gate.check("No tax tech mentioned", "memo")["status"] == "N/A"


def test_allowable_expenses():
    gate = AllowableExpensesGate()
    # FAIL: client entertainment claimed
    r = gate.check("We will claim client entertainment expense this year", "advice")
    assert r["status"] == "FAIL" and r["severity"] == "high"
    # PASS: neutral text
    assert gate.check("Office supplies expense recorded", "memo")["status"] in ("PASS", "N/A")
    # N/A
    assert gate.check("No expenses here", "memo")["status"] == "N/A"


def test_capital_revenue_distinction():
    gate = CapitalRevenueDistinctionGate()
    # FAIL: expensing capital item without mention of capital/allowance
    r = gate.check("We will expense the computer immediately", "advice")
    assert r["status"] == "FAIL" and r["severity"] == "high"
    # PASS: capital allowances context
    assert gate.check("Purchased computer; claim capital allowances.", "advice")["status"] in ("PASS",)
    # N/A
    assert gate.check("General discussion", "memo")["status"] == "N/A"


def test_business_structure_consistency():
    gate = BusinessStructureConsistencyGate()
    # WARNING: mismatched terminology
    r = gate.check("Sole trader director", "advice")
    assert r["status"] == "WARNING"
    # PASS: correct
    assert gate.check("Company director pays corporation tax", "advice")["status"] in ("PASS","N/A")
    # N/A
    assert gate.check("No business terms", "memo")["status"] == "N/A"


def test_hmrc_scam_detection():
    gate = HmrcScamDetectionGate()
    # FAIL: scam indicator
    r = gate.check("HMRC refund; pay with Amazon gift cards", "email")
    assert r["status"] == "FAIL" and r["severity"] == "critical"
    # PASS
    assert gate.check("HMRC official portal notice", "email")["status"] in ("PASS","N/A")
    # N/A
    assert gate.check("No hmrc mentioned", "memo")["status"] == "N/A"


def test_scottish_tax_specifics():
    gate = ScottishTaxSpecificsGate()
    # WARNING: missing rate context
    r = gate.check("Scottish income tax applies", "advice")
    assert r["status"] in ("WARNING","PASS")
    # PASS: mentions starter rate
    assert gate.check("Scottish income tax starter rate is 19%", "advice")["status"] in ("PASS","N/A")
    # N/A
    assert gate.check("England only", "memo")["status"] == "N/A"


def test_invoice_numbering():
    gate = InvoiceNumberingGate()
    # PASS
    text = "Invoice No: INV-100 Invoice No: INV-101 Invoice No: INV-102"
    assert gate.check(text, "invoice")["status"] == "PASS"
    # FAIL: gap + duplicate
    text = "Invoice No: INV-100 Invoice No: INV-102 Invoice No: INV-102"
    r = gate.check(text, "invoice")
    assert r["status"] == "FAIL" and r["severity"] == "medium"
    assert isinstance(r.get("spans"), list)
    # N/A
    assert gate.check("Memo", "memo")["status"] == "N/A"


def test_payment_method_validation():
    gate = PaymentMethodValidationGate()
    # FAIL
    r = gate.check("Please pay with iTunes gift cards; bank details changed.", "email")
    assert r["status"] == "FAIL" and r["severity"] == "critical"
    # PASS
    assert gate.check("Pay via HMRC portal or Direct Debit", "email")["status"] in ("PASS","N/A")
    # N/A
    assert gate.check("No payment context here", "memo")["status"] == "N/A"

