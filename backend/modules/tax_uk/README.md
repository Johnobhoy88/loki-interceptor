# Tax & Financial (UK SME) Module

This module validates UK tax and financial compliance patterns in documents and AI outputs. It follows the LOKI gate pattern (content‑aware, standardized returns, optional spans for inline highlighting).

## Production Gates (15)

1. vat_invoice_integrity (critical)
   - Ensures VAT invoices include required fields: unique invoice number, VAT number, date, supplier/customer details, VAT rate, net, VAT amount, total.
   - Legal: VAT Regulations 1995 (Reg. 14); HMRC VAT Notice 700/21

2. vat_number_format (critical)
   - Validates VAT number formats (GB123456789, GB123456789012, XI123456789); spans invalid matches.
   - Legal: HMRC VAT Registration Manual (VATREG03700)

3. vat_rate_accuracy (high)
   - Flags VAT rates outside the UK valid set: 20%, 5%, 0%; spans invalid rates.
   - Legal: VAT Act 1994; HMRC Guidance on VAT rates

4. vat_threshold (critical)
   - Checks the stated VAT registration threshold equals £90,000 (from April 2024) in registration context; spans incorrect amounts.
   - Legal: VAT Act 1994 §3; HMRC Guidance

5. invoice_legal_requirements (high)
   - Companies Act/GOV.UK required elements (unique number, supplier name & address, customer, date, description, total).
   - Legal: Companies Act 2006; GOV.UK Invoicing guidance

6. company_limited_suffix (high)
   - Warns when a company name near “Invoice/Company/Business” appears without Limited/Ltd/LLP/PLC suffix; spans company name.
   - Legal: Companies Act 2006; Trading Disclosures Regulations 2008

7. tax_deadline_accuracy (critical)
   - Flags common deadline errors (SA due 31 Jan; CT payment 9 months + 1 day) with spans; otherwise pass.
   - Legal: HMRC Self‑Assessment & Corporation Tax deadlines

8. mtd_compliance (high)
   - Fails if text implies MTD is optional or paper VAT returns accepted; otherwise pass.
   - Legal: Finance (No.2) Act 2017; HMRC MTD Regulations

9. allowable_expenses (high)
   - Fails when non‑allowable expenses are claimed (client entertainment, commuting, personal clothing, fines, large gifts); spans matches.
   - Legal: Income Tax Act 2005 §34; Corporation Tax Act 2009 §54

10. capital_revenue_distinction (high)
   - Fails when capital items are treated as revenue expenses; flags depreciation deduction; spans items.
   - Legal: Capital Allowances Act 2001; HMRC guidance

11. business_structure_consistency (medium)
   - Warns on terminology mismatches (sole trader ≠ directors/company; drawings ≠ salary/dividends).
   - Legal: Companies Act 2006; HMRC terminology

12. hmrc_scam_detection (critical)
   - Detects scam indicators (gift cards, crypto, “bank details changed”, non‑gov emails, refund via email/text); spans matches.
   - Legal: Fraud Act 2006; HMRC official scam guidance

13. scottish_tax_specifics (medium)
   - Warns if Scottish income tax is referenced without clarifying Scottish bands; pass if context clarified.
   - Legal: Scotland Act 2016; Scottish bands

14. invoice_numbering (medium)
   - Ensures invoice numbering is unique/sequential; fails on duplicates/gaps; spans numbers.
   - Legal: VAT Regulations 1995; HMRC Internal Manuals (VATREC5010)

15. payment_method_validation (critical)
   - Fails on suspicious payment methods (gift cards, crypto, personal accounts) and “bank details changed” messaging; spans matches.
   - Legal: GOV.UK guidance on paying HMRC

## Example Usage

Validate a document with only the tax module:

```
curl -X POST http://127.0.0.1:5000/validate-document \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Invoice No: INV-100... VAT Number: GB123456789...",
    "document_type": "invoice",
    "modules": ["tax_uk"]
  }'
```

Validate AI output via the Interceptor with all modules:

```
curl -X POST http://127.0.0.1:5000/v1/messages \
  -H "x-api-key: <ANTHROPIC_KEY>" -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 256,
    "messages": [{"role":"user","content":"..."}],
    "modules": ["hr_scottish","gdpr_uk","nda_uk","tax_uk"]
  }'
```

## Future Scope

The following areas are planned (out of scope for v1.0):
- PAYE Registration and RTI filings (FPS/EPS)
- CIS verification & deduction statements
- IR35/Off‑payroll working (SDS, reasonable care)
- CT600 filing details (file 12 months; pay 9 months + 1 day)
