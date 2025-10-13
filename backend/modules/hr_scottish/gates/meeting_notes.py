import re


class MeetingNotesGate:
    def __init__(self):
        self.name = "meeting_notes"
        self.severity = "low"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ['hearing', 'meeting', 'disciplinary'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not disciplinary meeting documentation',
                'legal_source': self.legal_source
            }
        
        notes_patterns = [r'minutes', r'notes.*meeting', r'record.*meeting', r'noted']
        
        for pattern in notes_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {'status': 'PASS', 'severity': 'none', 'message': 'Meeting recording mentioned', 'legal_source': self.legal_source}
        
        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'No mention of meeting notes/minutes',
            'suggestion': 'State: "A record of this meeting will be taken and provided to you."',
            'legal_source': self.legal_source
        }
