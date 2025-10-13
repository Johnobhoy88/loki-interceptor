import re


class ProtectedWhistleblowingGate:
    def __init__(self):
        self.name = "protected_whistleblowing"
        self.severity = "critical"
        self.legal_source = "Public Interest Disclosure Act 1998, Section 43J Employment Rights Act 1996"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential', 'agreement'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure agreement',
                'legal_source': self.legal_source
            }
        
        # Check for blanket prohibition on disclosure
        prohibition_patterns = [
            r'shall not disclose.*to any.*under any circumstances',
            r'not.*disclose.*(?:information|any).*to.*(?:third part(?:y|ies)|any)',
            r'no disclosure.*whatsoever',
            r'not.*disclose.*(?:to|any).*(?:third party|anyone)',
            r'shall not disclose any information'
        ]
        
        has_blanket_ban = any(re.search(p, text, re.IGNORECASE) for p in prohibition_patterns)
        
        # Check for whistleblowing carve-out
        carveout_patterns = [
            r'protected disclosure',
            r'public interest disclosure act',
            r'nothing.*prevent.*(?:making|reporting).*(?:disclosure|wrongdoing)',
            r'whistleblow'
        ]
        
        has_carveout = any(re.search(p, text, re.IGNORECASE) for p in carveout_patterns)
        
        if has_blanket_ban and not has_carveout:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'NDA contains blanket prohibition without whistleblowing exception',
                'legal_source': self.legal_source,
                'suggestion': 'Add: "Nothing in this Agreement prevents the disclosure of information protected under the Public Interest Disclosure Act 1998."',
                'penalty': 'Clause is void and unenforceable; SRA ethical breach'
            }
        
        if has_carveout:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Whistleblowing protections stated', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'No explicit whistleblowing carve-out',
            'suggestion': 'Add carve-out for protected disclosures under PIDA 1998'
        }
