import re


class ProtectedCrimeReportingGate:
    def __init__(self):
        self.name = "protected_crime_reporting"
        self.severity = "critical"
        self.legal_source = "Victims and Prisoners Act 2024 (effective 1 Oct 2025)"
    
    def _is_relevant(self, text):
        return any(kw in (text or '').lower() for kw in ['nda', 'confidential', 'settlement'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure agreement',
                'legal_source': self.legal_source
            }
        
        # Check for crime reporting prohibition (broad blanket bans also apply)
        crime_prohibition = [
            r'not.*disclose.*to.*(?:police|law enforcement|authorities|regulatory)',
            r'confidential.*includes.*(?:criminal|offence|incident)',
            r'must not.*report.*to.*authorities',
            r'shall not disclose.*to any.*(?:third party|one)'  # Catches blanket bans
        ]
        
        has_prohibition = any(re.search(p, text, re.IGNORECASE) for p in crime_prohibition)
        
        # Check for crime reporting exception
        crime_exception = [
            r'report.*criminal.*(?:act|offence).*to.*police',
            r'nothing.*prevent.*reporting.*crime',
            r'victims and prisoners act',
            r'disclose.*(?:lawyer|medical|family).*for.*support'
        ]
        
        has_exception = any(re.search(p, text, re.IGNORECASE) for p in crime_exception)
        
        if has_prohibition:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'NDA attempts to prevent crime reporting',
                'legal_source': self.legal_source,
                'suggestion': 'Remove prohibition. Add: "Nothing prevents reporting criminal offences to police or seeking support from lawyers, medical professionals, or family."',
                'penalty': 'Clause is void under common law and Victims and Prisoners Act 2024'
            }
        
        if has_exception:
            return {'status': 'PASS', 'severity': 'none', 'message': 'Crime reporting rights protected', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'No explicit crime reporting protection',
            'suggestion': 'Add exception for reporting criminal conduct'
        }
