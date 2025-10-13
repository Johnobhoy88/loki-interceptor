"""
Enhance Tax Gates with Helpful N/A Messages
Adds informative N/A messages to all 15 tax gates
"""

import re
import os

# Define helpful N/A messages for each tax gate
NA_MESSAGES = {
    'allowable_expenses.py': 'Not applicable - document does not discuss business expenses or tax deductions',
    'business_structure_consistency.py': 'Not applicable - document does not reference business structures (sole trader, limited company, partnership)',
    'capital_revenue_distinction.py': 'Not applicable - document does not discuss capital or revenue expenditure',
    'company_limited_suffix.py': 'Not applicable - document does not contain company names or trading information',
    'hmrc_scam_detection.py': 'Not applicable - document does not contain HMRC, tax, or payment-related content',
    'invoice_legal_requirements.py': 'Not applicable - document is not an invoice',
    'invoice_numbering.py': 'Not applicable - document does not contain invoice numbers',
    'mtd_compliance.py': 'Not applicable - document does not discuss Making Tax Digital or VAT returns',
    'payment_method_validation.py': 'Not applicable - document does not contain payment instructions or bank details',
    'scottish_tax_specifics.py': 'Not applicable - document does not reference Scottish tax or Scotland-specific tax rules',
    'tax_deadline_accuracy.py': 'Not applicable - document does not mention tax deadlines or filing dates',
    'vat_invoice_integrity.py': 'Not applicable - document is not a VAT invoice',
    'vat_number_format.py': 'Not applicable - document does not reference VAT numbers',
    'vat_rate_accuracy.py': 'Not applicable - document does not mention VAT rates',
    'vat_threshold.py': 'Not applicable - document does not discuss VAT registration thresholds or turnover limits',
}

def enhance_gate(file_path, na_message):
    """Add helpful N/A message to a gate file"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Pattern 1: return {'status': 'N/A'}
    pattern1 = r"return \{'status': 'N/A'\}"
    replacement1 = f"""return {{
                'status': 'N/A',
                'message': '{na_message}',
                'legal_source': self.legal_source
            }}"""

    # Check if already has message
    if "'message':" in content and "'status': 'N/A'" in content:
        print(f"  ⏭️  Skipping (already has N/A message)")
        return False

    if pattern1 in content:
        content = re.sub(pattern1, replacement1, content)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Enhanced")
        return True
    else:
        print(f"  ⚠️  Pattern not found")
        return False

def main():
    """Enhance all tax gates"""
    print("=" * 80)
    print("ENHANCING TAX GATES WITH N/A MESSAGES")
    print("=" * 80)
    print()

    gates_dir = 'modules/tax_uk/gates'
    enhanced = 0
    skipped = 0

    for filename, message in NA_MESSAGES.items():
        file_path = os.path.join(gates_dir, filename)
        gate_name = filename.replace('.py', '').replace('_', ' ').title()

        print(f"{gate_name}:")
        if enhance_gate(file_path, message):
            enhanced += 1
        else:
            skipped += 1

    print()
    print("=" * 80)
    print(f"COMPLETE: {enhanced} gates enhanced, {skipped} skipped")
    print("=" * 80)

if __name__ == "__main__":
    os.chdir('/mnt/c/Users/jpmcm.DESKTOP-CQ0CL93/OneDrive/Desktop/HighlandAI/LOKI_INTERCEPTOR_CLAUDEV1/backend')
    main()
