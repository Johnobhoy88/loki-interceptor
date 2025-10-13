import re


class ProtectedHarassmentGate:
    def __init__(self):
        self.name = "protected_harassment"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010; Employment Rights Bill Clause 22A"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return 'settlement' in text_lower or 'employment' in text_lower or 'nda' in text_lower
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a confidentiality or non-disclosure agreement',
                'legal_source': self.legal_source
            }
        
        # Check for harassment/discrimination silencing
        silencing_patterns = [
            r'not.*(?:make|discuss|disclose).*(?:allegation|complaint|information).*(?:company|employer|employment)',
            r'confidential.*includes.*(?:employment|workplace).*(?:conduct|behaviour)',
            r'negative.*statement.*about.*(?:company|colleagues)',
            r'never to discuss.*experience.*(?:at|with)',
            r'not.*disclose.*(?:allegations|information).*(?:harassment|discrimination)'
        ]
        
        has_silencing = any(re.search(p, text, re.IGNORECASE) for p in silencing_patterns)
        
        # Check for harassment exception
        harassment_exception = [
            r'equality act',
            r'discrimination.*harassment',
            r'nothing.*prevent.*(?:disclosure|allegation).*(?:harassment|discrimination)',
            r'protected.*characteristic'
        ]
        
        has_exception = any(re.search(p, text, re.IGNORECASE) for p in harassment_exception)
        
        if has_silencing and not has_exception:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'NDA may silence harassment/discrimination allegations',
                'legal_source': self.legal_source,
                'suggestion': 'Add: "Nothing prevents disclosure of conduct that may constitute harassment or discrimination under the Equality Act 2010."',
                'penalty': 'Clause void under Employment Rights Bill; SRA ethical violation'
            }
        
        if has_exception:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Harassment/discrimination protections stated', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'No explicit harassment/discrimination exception',
            'suggestion': 'Add carve-out for Equality Act 2010 disclosures'
        }
