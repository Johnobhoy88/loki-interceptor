"""
Bulk enhance all tax gates with N/A messages
"""
import re

# Map of file paths to their N/A messages
GATES = [
    ('modules/tax_uk/gates/business_structure_consistency.py',
     'Not applicable - document does not reference business structures (sole trader, limited company, partnership)'),
    ('modules/tax_uk/gates/capital_revenue_distinction.py',
     'Not applicable - document does not discuss capital or revenue expenditure'),
    ('modules/tax_uk/gates/company_limited_suffix.py',
     'Not applicable - document does not contain company names or trading information'),
    ('modules/tax_uk/gates/hmrc_scam_detection.py',
     'Not applicable - document does not contain HMRC, tax, or payment-related content'),
    ('modules/tax_uk/gates/invoice_legal_requirements.py',
     'Not applicable - document is not an invoice'),
    ('modules/tax_uk/gates/invoice_numbering.py',
     'Not applicable - document does not contain invoice numbers'),
    ('modules/tax_uk/gates/mtd_compliance.py',
     'Not applicable - document does not discuss Making Tax Digital or VAT returns'),
    ('modules/tax_uk/gates/payment_method_validation.py',
     'Not applicable - document does not contain payment instructions or bank details'),
    ('modules/tax_uk/gates/scottish_tax_specifics.py',
     'Not applicable - document does not reference Scottish tax or Scotland-specific tax rules'),
    ('modules/tax_uk/gates/tax_deadline_accuracy.py',
     'Not applicable - document does not mention tax deadlines or filing dates'),
    ('modules/tax_uk/gates/vat_invoice_integrity.py',
     'Not applicable - document is not a VAT invoice'),
    ('modules/tax_uk/gates/vat_number_format.py',
     'Not applicable - document does not reference VAT numbers'),
    ('modules/tax_uk/gates/vat_rate_accuracy.py',
     'Not applicable - document does not mention VAT rates'),
    ('modules/tax_uk/gates/vat_threshold.py',
     'Not applicable - document does not discuss VAT registration thresholds or turnover limits'),
]

for filepath, message in GATES:
    print(f"Processing {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    # Replace basic N/A returns with enhanced ones
    old_pattern = r"return \{'status': 'N/A'\}"
    new_return = f"""return {{
                'status': 'N/A',
                'message': '{message}',
                'legal_source': self.legal_source
            }}"""

    # Count replacements
    count = len(re.findall(old_pattern, content))

    if count > 0:
        content = re.sub(old_pattern, new_return, content)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Enhanced {count} N/A return(s)")
    else:
        print(f"  ⏭️  Already enhanced")

print("\n✅ All tax gates enhanced!")
