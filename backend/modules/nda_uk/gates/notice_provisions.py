import re


class NoticeProvisionsGate:
    def __init__(self):
        self.name = "notice_provisions"
        self.severity = "low"
        self.legal_source = "Contract Law, Communication principles"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for notice provisions
        notice_patterns = [
            r'notice(?:s)?(?:\s+under\s+this\s+agreement)?',
            r'communicat(?:ion|e).*(?:between|to)\s+(?:the\s+)?parties',
            r'served\s+(?:by|on)',
            r'deliver(?:y|ed).*notice'
        ]

        has_notice_clause = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        if not has_notice_clause:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No notice provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding notice clause specifying addresses and delivery methods'
            }

        # Check for addresses
        address_patterns = [
            r'address(?:es)?.*(?:set\s+out|specified)',
            r'(?:registered\s+office|principal\s+place\s+of\s+business)',
            r'at\s+the\s+(?:address|email)',
            r'\d+.*(?:street|road|avenue|lane)'
        ]

        has_addresses = any(re.search(p, text, re.IGNORECASE) for p in address_patterns)

        # Check for delivery methods
        delivery_methods = {
            'hand_delivery': r'(?:by\s+)?hand|personal\s+deliver',
            'post': r'(?:by\s+)?(?:post|mail|recorded\s+delivery|registered\s+post)',
            'courier': r'courier|overnight',
            'email': r'(?:by\s+)?(?:e-?mail|electronic)',
            'fax': r'(?:by\s+)?(?:fax|facsimile)'
        }

        found_methods = []
        for method, pattern in delivery_methods.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_methods.append(method)

        # Check for deemed receipt provisions
        receipt_patterns = [
            r'deemed.*(?:receiv|deliver)',
            r'(?:shall\s+be\s+)?deemed.*given',
            r'effective.*(?:upon|on).*(?:receipt|delivery)',
            r'business\s+days?.*after'
        ]

        has_receipt = any(re.search(p, text, re.IGNORECASE) for p in receipt_patterns)

        # Check for change of address provisions
        change_patterns = [
            r'change\s+of\s+address',
            r'notify.*new\s+address',
            r'update.*contact\s+details'
        ]

        has_change_provision = any(re.search(p, text, re.IGNORECASE) for p in change_patterns)

        score = 0
        if has_addresses:
            score += 1
        if len(found_methods) >= 2:
            score += 1
        if has_receipt:
            score += 1
        if has_change_provision:
            score += 1

        if score >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive notice provisions',
                'legal_source': self.legal_source,
                'delivery_methods': found_methods
            }

        if score >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Adequate notice provisions',
                'legal_source': self.legal_source,
                'delivery_methods': found_methods,
                'suggestion': 'Consider adding deemed receipt provisions'
            }

        missing = []
        if not has_addresses:
            missing.append('addresses')
        if len(found_methods) < 2:
            missing.append('delivery methods')
        if not has_receipt:
            missing.append('deemed receipt provisions')

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Notice provisions incomplete',
            'legal_source': self.legal_source,
            'missing': missing,
            'suggestion': 'Add: addresses, delivery methods (post, email), and deemed receipt provisions'
        }
