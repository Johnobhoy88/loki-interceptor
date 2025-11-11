"""Investment Research Requirements Gate - COBS 12.2"""
import re

class InvestmentResearchGate:
    def __init__(self):
        self.name = "investment_research"
        self.severity = "medium"
        self.legal_source = "FCA COBS 12.2 (Investment Research)"

    def _is_relevant(self, text):
        research_terms = ['research', 'analysis', 'recommendation', 'analyst', 'investment view']
        return any(term in text.lower() for term in research_terms)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'legal_source': self.legal_source}

        disclosures = {
            'conflicts': r'conflict(?:s)?\s+of\s+interest',
            'independence': r'independent\s+research',
            'methodology': r'(?:research\s+)?methodology',
            'disclaimer': r'(?:this\s+is\s+)?(?:not\s+)?(?:personal\s+)?recommendation'
        }

        found = [disc for disc, pattern in disclosures.items() if re.search(pattern, text, re.IGNORECASE)]

        if len(found) < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Investment research lacks required disclosures',
                'legal_source': self.legal_source,
                'suggestion': 'Include: conflicts of interest, independence, methodology, disclaimers'
            }

        return {'status': 'PASS', 'message': f'Research disclosures present ({len(found)} elements)', 'legal_source': self.legal_source}
