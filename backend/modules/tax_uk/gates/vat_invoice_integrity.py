import re

class VatInvoiceIntegrityGate:
    def __init__(self):
        self.name = "vat_invoice_integrity"
        self.severity = "critical"
        self.legal_source = "VAT Regulations 1995 (Regulation 14); HMRC VAT Notice 700/21"

    def _is_relevant(self, text):
        """Check if the text is likely a VAT invoice."""
        text_lower = (text or '').lower()
        return 'invoice' in text_lower or 'vat' in text_lower

    def check(self, text, document_type):
        """
        Apply the gate logic to check for VAT invoice integrity per HMRC requirements.
        A valid VAT invoice MUST include all mandatory fields.
        """
        try:
            if not self._is_relevant(text):
                return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a VAT invoice',
                'legal_source': self.legal_source
            }

            if not isinstance(text, str):
                return {
                    'status': 'ERROR',
                    'message': 'Invalid input type for VAT integrity check.'
                }

            text_lower = text.lower()

            # Mandatory fields per VAT Regulation 14
            # BUG FIX: Enhanced regex patterns to handle more format variations
            mandatory_fields = {
                # Bug #1 Fix: Allow "Invoice Number:", "Invoice No.", etc.
                'invoice_number': r'invoice\s+(?:no\.?|number|#)\s*:?\s*[A-Z0-9-]+',
                # Bug #2 Fix: Allow standalone "Date:" label
                'invoice_date': r'(?:invoice\s+)?(?:date|dated)\s*:?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                'supplier_name': r'(?:from|supplier|sold by|invoice from)\s*:?\s*[A-Za-z\s&]+',
                'supplier_address': r'(?:address|located at)\s*:?',
                'vat_number': r'vat\s*(?:reg|registration)?\s*(?:no|number)?\s*:?\s*(?:GB)?\s*\d{9}',
                'customer_details': r'(?:to|bill to|customer|invoice to)\s*:?\s*[A-Za-z\s&]+',
                'net_amount': r'(?:net|subtotal)\s*:?\s*£?[0-9,]+\.[0-9]{2}',
                'vat_amount': r'vat\s*(?:\([^)]+\))?\s*:?\s*£?[0-9,]+\.[0-9]{2}',
                'total_amount': r'total\s*(?:due)?\s*:?\s*£?[0-9,]+\.[0-9]{2}'
            }

            missing_fields = []
            for field, pattern in mandatory_fields.items():
                if not re.search(pattern, text, re.IGNORECASE):
                    missing_fields.append(field.replace('_', ' ').title())

            # FAIL if ANY mandatory field is missing
            if missing_fields:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': f'VAT invoice missing {len(missing_fields)} mandatory field(s)',
                    'details': missing_fields,
                    'legal_source': self.legal_source,
                    'suggestion': 'Per HMRC VAT Notice 700/21, a valid VAT invoice must include: (1) unique invoice number, (2) invoice date, (3) supplier name and address, (4) supplier VAT number, (5) customer details, (6) description of goods/services, (7) net amount, (8) VAT amount, (9) total amount',
                    'penalty': 'Invalid VAT invoices can result in VAT reclaim being denied and penalties of up to 30% of VAT due'
                }

            # Check VAT calculation accuracy
            net_match = re.search(r'(?:net|subtotal)\s*:?\s*£?([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
            vat_match = re.search(r'vat\s*(?:\([^)]+\))?\s*:?\s*£?([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)
            total_match = re.search(r'total\s*(?:due)?\s*:?\s*£?([0-9,]+\.[0-9]{2})', text, re.IGNORECASE)

            if net_match and vat_match and total_match:
                try:
                    net = float(net_match.group(1).replace(',', ''))
                    vat = float(vat_match.group(1).replace(',', ''))
                    total = float(total_match.group(1).replace(',', ''))

                    calculated_total = net + vat
                    if abs(calculated_total - total) > 0.02:  # Allow 2p rounding difference
                        return {
                            'status': 'WARNING',
                            'severity': 'medium',
                            'message': 'VAT calculation mismatch',
                            'details': [f'Net (£{net}) + VAT (£{vat}) = £{calculated_total}, but Total shows £{total}'],
                            'suggestion': 'Verify arithmetic: Net + VAT should equal Total'
                        }
                except ValueError:
                    pass  # Can't parse numbers, skip calculation check

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'VAT invoice contains all mandatory fields'
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'severity': 'critical',
                'message': f'Gate execution error in {self.name}: {str(e)}'
            }

