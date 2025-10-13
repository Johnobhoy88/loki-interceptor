import re


class TaxDeadlineAccuracyGate:
    def __init__(self):
        self.name = "tax_deadline_accuracy"
        self.severity = "critical"
        self.legal_source = "HMRC Self-Assessment and Corporation Tax deadlines"
    
    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['deadline', 'due', 'file', 'return', 'tax'])
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not mention tax deadlines or filing dates',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()

        # Check for common deadline errors
        errors = []
        spans = []

        # Self-assessment online - should be 31 January
        sa_online_pattern = r'online.*(?:return|filing|file).*?(?:by|deadline|due).*?(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)'
        for match in re.finditer(sa_online_pattern, text, re.IGNORECASE):
            day = int(match.group(1))
            month = match.group(2).lower()
            if month == 'january' and day == 31:
                continue  # Correct
            if 'self' in text_lower[max(0,match.start()-100):match.start()].lower() or \
               'assessment' in text_lower[max(0,match.start()-100):match.start()].lower():
                errors.append('Self-assessment online deadline is 31 January')
                spans.append({
                    'type': 'incorrect_sa_deadline',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })

        # Self-assessment paper - should be 31 October
        sa_paper_pattern = r'paper.*(?:return|filing|file).*?(?:by|deadline|due).*?(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)'
        for match in re.finditer(sa_paper_pattern, text, re.IGNORECASE):
            day = int(match.group(1))
            month = match.group(2).lower()
            if month == 'october' and day == 31:
                continue  # Correct
            if 'self' in text_lower[max(0,match.start()-100):match.start()].lower() or \
               'assessment' in text_lower[max(0,match.start()-100):match.start()].lower():
                errors.append('Self-assessment paper deadline is 31 October')
                spans.append({
                    'type': 'incorrect_sa_paper_deadline',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })

        # Payment deadline - should be 31 January for SA
        payment_pattern = r'payment.*(?:is\s+)?due.*?(?:by)?\s*(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)'
        for match in re.finditer(payment_pattern, text, re.IGNORECASE):
            day = int(match.group(1))
            month = match.group(2).lower()
            if month == 'january' and day == 31:
                continue  # Correct
            if 'self' in text_lower[max(0,match.start()-150):match.start()].lower() or \
               'assessment' in text_lower[max(0,match.start()-150):match.start()].lower() or \
               'tax' in text_lower[max(0,match.start()-100):match.start()].lower():
                errors.append('Self-assessment payment deadline is 31 January')
                spans.append({
                    'type': 'incorrect_payment_deadline',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })

        # Corporation Tax payment - 9 months + 1 day
        ct_pattern = r'corporation tax.*(?:payment|due).*?(\d+\s+months?)'
        for match in re.finditer(ct_pattern, text, re.IGNORECASE):
            months_str = match.group(1)
            if '9' not in months_str and '12' not in months_str:
                errors.append('Corporation Tax payment due 9 months + 1 day after year-end')
                spans.append({
                    'type': 'incorrect_ct_deadline',
                    'start': match.start(1),
                    'end': match.end(1),
                    'text': match.group(1),
                    'severity': 'critical'
                })

        if errors:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': '; '.join(set(errors)),  # Remove duplicates
                'spans': spans,
                'legal_source': self.legal_source,
                'suggestion': 'Key deadlines: Self-assessment paper 31 Oct, online 31 Jan, payment 31 Jan; Corporation Tax payment 9 months + 1 day, return 12 months'
            }

        return {'status': 'PASS', 'severity': 'none', 'message': 'Tax deadline information correct'}
