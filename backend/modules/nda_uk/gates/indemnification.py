import re


class IndemnificationGate:
    def __init__(self):
        self.name = "indemnification"
        self.severity = "medium"
        self.legal_source = "Contract Law, Indemnity principles"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract', 'nda'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for indemnification clause
        indemnity_patterns = [
            r'indemni(?:fy|fies|fied|fication|ty)',
            r'hold\s+harmless',
            r'defend.*against.*(?:claim|loss|damage)',
            r'reimburse.*(?:loss|damage|cost)'
        ]

        has_indemnity = any(re.search(p, text, re.IGNORECASE) for p in indemnity_patterns)

        if not has_indemnity:
            return {
                'status': 'N/A',
                'message': 'No indemnification provisions',
                'legal_source': self.legal_source
            }

        # Check scope of indemnity
        scope_elements = {
            'breach': r'breach\s+of.*(?:agreement|obligation)',
            'losses': r'(?:loss|losses|damage|damages)',
            'costs': r'(?:cost|costs|expense|expenses)',
            'legal_fees': r'(?:legal|attorney|solicitor).*(?:fees?|costs?)',
            'third_party_claims': r'third\s+part(?:y|ies).*claim',
            'negligence': r'negligence|negligent',
            'wilful_misconduct': r'wilful.*(?:misconduct|default|breach)'
        }

        found_scope = {}
        for element, pattern in scope_elements.items():
            found_scope[element] = bool(re.search(pattern, text, re.IGNORECASE))

        # Check for limitations
        limitation_patterns = [
            r'except.*fraud',
            r'excluding.*(?:indirect|consequential)',
            r'limited\s+to',
            r'cap(?:ped)?.*amount'
        ]

        has_limitations = any(re.search(p, text, re.IGNORECASE) for p in limitation_patterns)

        # Check for defence obligations
        defence_patterns = [
            r'defend.*claim',
            r'control.*defence',
            r'conduct.*defence',
            r'right\s+to\s+defend'
        ]

        has_defence = any(re.search(p, text, re.IGNORECASE) for p in defence_patterns)

        # Check for notice requirements
        notice_patterns = [
            r'(?:prompt|immediate).*notice.*claim',
            r'notif(?:y|ication).*(?:claim|proceeding)',
            r'inform.*claim.*(?:promptly|immediately)'
        ]

        has_notice_requirement = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        # Check for mutual vs. unilateral indemnity
        mutual_patterns = [
            r'each\s+party.*indemni',
            r'mutual(?:ly)?.*indemni',
            r'parties.*indemni.*each\s+other'
        ]

        is_mutual = any(re.search(p, text, re.IGNORECASE) for p in mutual_patterns)

        # Check for unreasonable exclusions (e.g., excluding fraud)
        unreasonable_patterns = [
            r'(?:exclud|limit).*(?:all\s+)?liability.*fraud',
            r'indemni.*(?:not\s+apply|exclude).*fraud'
        ]

        has_unreasonable = any(re.search(p, text, re.IGNORECASE) for p in unreasonable_patterns)

        if has_unreasonable:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Indemnity attempts to exclude fraud - void under UK law',
                'legal_source': 'Unfair Contract Terms Act 1977',
                'penalty': 'Clause void and unenforceable',
                'suggestion': 'Remove exclusion of fraud liability'
            }

        scope_count = sum(found_scope.values())

        if scope_count >= 4 and has_notice_requirement:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive indemnification clause ({scope_count} scope elements)',
                'legal_source': self.legal_source,
                'is_mutual': is_mutual,
                'scope_elements': [k for k, v in found_scope.items() if v]
            }

        if scope_count >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic indemnification provisions',
                'legal_source': self.legal_source,
                'is_mutual': is_mutual,
                'suggestion': 'Consider adding notice requirements and defence provisions'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Indemnification clause lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Specify scope: losses, costs, legal fees, and notice requirements'
        }
