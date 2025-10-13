import re


class TimeframesGate:
    def __init__(self):
        self.name = "timeframes"
        self.severity = "medium"
        self.legal_source = "ACAS Code of Practice (Disciplinary & Grievance)"
    
    def _is_relevant(self, text):
        text_lower = text.lower()
        # Check for outcome letters or anything mentioning warnings/timeframes
        has_outcome = any(kw in text_lower for kw in ['warning', 'outcome', 'decision', 'dismissal'])
        has_timeframe = any(kw in text_lower for kw in ['within', 'days', 'deadline', 'file', 'remain'])
        return has_outcome or (has_timeframe and 'appeal' in text_lower)
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not specify disciplinary process timeframes',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check if this is a warning/outcome letter
        is_outcome = any(kw in text_lower for kw in ['warning', 'outcome', 'decision'])

        # Check for unreasonably short appeal timeframes
        short_rx = r'within\s+(?:1|2|24|48)\s+(?:hours?|days?)'
        if re.search(short_rx, text, re.IGNORECASE):
            spans = []
            for m in re.finditer(short_rx, text, re.IGNORECASE):
                spans.append({'type': 'short_timeframe', 'start': m.start(), 'end': m.end(), 'text': m.group(), 'severity': 'medium'})
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Very short appeal timeframe detected',
                'spans': spans,
                'suggestion': 'ACAS recommends 5-10 working days for appeals.',
                'legal_source': self.legal_source
            }

        # If it's an outcome letter, check for warning expiry timeframe
        if is_outcome and 'warning' in text_lower:
            # Missing timeframe for warning
            has_expiry = re.search(r'(?:for|valid for|remain.*for|expire|removed after)\s+(?:\d+)\s+(?:months?|years?)', text, re.IGNORECASE)
            if not has_expiry and 'remain' in text_lower:
                return {
                    'status': 'FAIL',
                    'severity': 'medium',
                    'message': 'Warning duration/expiry timeframe not specified',
                    'suggestion': 'State how long the warning will remain on file (e.g., "This warning will remain on your file for 12 months")',
                    'legal_source': self.legal_source
                }

        # Check for reasonable appeal timeframe
        if re.search(r'within\s+(?:[5-9]|1[0-4])\s+(?:working\s+)?days?', text, re.IGNORECASE):
            return {'status': 'PASS', 'severity': 'none', 'message': 'Reasonable timeframe specified', 'spans': [], 'legal_source': self.legal_source}

        return {'status': 'PASS', 'severity': 'none', 'message': 'No timeframe issues detected', 'spans': [], 'legal_source': self.legal_source}
