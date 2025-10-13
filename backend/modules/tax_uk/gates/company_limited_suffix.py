import re


class CompanyLimitedSuffixGate:
    def __init__(self):
        self.name = "company_limited_suffix"
        self.severity = "high"
        self.legal_source = "Companies Act 2006; Companies (Trading Disclosures) Regulations 2008"
    
    def _is_relevant(self, text):
        t = text.lower()
        return any(k in t for k in ['invoice', 'ltd', 'limited', 'company', 'trading', 'business'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain company names or trading information',
                'legal_source': self.legal_source
            }
        
        # Find company names without proper suffix
        # Look for patterns like "ABC Trading" without Ltd/Limited
        company_pattern = r'\b([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*)\s+(?:Invoice|Company|Business)'
        
        spans = []
        for match in re.finditer(company_pattern, text):
            company_text = match.group(1)
            
            # Check if it has proper suffix nearby
            context_start = max(0, match.start() - 20)
            context_end = min(len(text), match.end() + 20)
            context = text[context_start:context_end]
            
            has_suffix = bool(re.search(r'\b(?:limited|ltd|llp|plc)\b', context, re.IGNORECASE))
            
            if not has_suffix and len(company_text.split()) > 1:
                spans.append({
                    'type': 'missing_ltd_suffix',
                    'start': match.start(1),
                    'end': match.end(1),
                    'text': company_text,
                    'severity': 'high'
                })
        
        if spans:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Company name may be missing "Limited" or "Ltd" suffix',
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Limited companies must display full registered name including "Limited", "Ltd", "LLP", or "PLC" on all business documents.'
            }
        
        return {'status': 'PASS', 'severity': 'none', 'message': 'Company naming compliant'}
