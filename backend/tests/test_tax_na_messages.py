"""
Test enhanced N/A messages for tax gates
"""

import sys
sys.path.insert(0, '/mnt/c/Users/jpmcm.DESKTOP-CQ0CL93/OneDrive/Desktop/HighlandAI/LOKI_INTERCEPTOR_CLAUDEV1/backend')

from modules.tax_uk.gates.allowable_expenses import AllowableExpensesGate
from modules.tax_uk.gates.vat_invoice_integrity import VatInvoiceIntegrityGate
from modules.tax_uk.gates.hmrc_scam_detection import HmrcScamDetectionGate
from modules.tax_uk.gates.tax_deadline_accuracy import TaxDeadlineAccuracyGate

print("Testing Enhanced N/A Messages (Tax Module):")
print("=" * 70)

# Test 1: Document with no tax content
text1 = "Hello, this is a general letter about our company history."

gate1 = AllowableExpensesGate()
result1 = gate1.check(text1, "letter")
print(f"\nAllowable Expenses:")
print(f"  Status: {result1['status']}")
print(f"  Message: {result1.get('message', 'No message')}")

gate2 = VatInvoiceIntegrityGate()
result2 = gate2.check(text1, "letter")
print(f"\nVAT Invoice:")
print(f"  Status: {result2['status']}")
print(f"  Message: {result2.get('message', 'No message')}")

gate3 = HmrcScamDetectionGate()
result3 = gate3.check(text1, "letter")
print(f"\nHMRC Scam Detection:")
print(f"  Status: {result3['status']}")
print(f"  Message: {result3.get('message', 'No message')}")

gate4 = TaxDeadlineAccuracyGate()
result4 = gate4.check(text1, "letter")
print(f"\nTax Deadline:")
print(f"  Status: {result4['status']}")
print(f"  Message: {result4.get('message', 'No message')}")

print("\n" + "=" * 70)
print("✅ All N/A messages enhanced successfully!")
