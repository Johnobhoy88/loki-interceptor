import re


class MtdComplianceGate:
    def __init__(self):
        self.name = "mtd_compliance"
        self.severity = "high"
        self.legal_source = "Finance (No.2) Act 2017; HMRC MTD Regulations"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['making tax digital', 'mtd', 'digital record', 'vat return'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss Making Tax Digital or VAT returns',
                'legal_source': self.legal_source
            }
        
        # Check for outdated MTD information
        errors = []
        
        # MTD for VAT is mandatory for ALL VAT-registered businesses
        if re.search(r'mtd.*(?:optional|voluntary|not required)', text, re.IGNORECASE):
            errors.append('MTD for VAT is mandatory for ALL VAT-registered businesses')
        
        # Check for paper/manual filing claims
        if re.search(r'(?:paper|manual).*vat.*(?:return|filing)', text, re.IGNORECASE):
            errors.append('Paper VAT returns no longer accepted - must use MTD software')
        
        if errors:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': '; '.join(errors),
                'legal_source': self.legal_source,
                'suggestion': 'MTD for VAT: Mandatory for all VAT-registered businesses. Must keep digital records and file via MTD-compatible software.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'MTD information correct'}
