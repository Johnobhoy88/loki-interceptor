import re


class ClientMoneySegregationGate:
    def __init__(self):
        self.name = "client_money_segregation"
        self.severity = "critical"
        self.legal_source = "FCA CASS 7 (Client Money Rules)"

    def _is_relevant(self, text):
        """Check if document mentions holding client money"""
        text_lower = text.lower()
        keywords = [
            'client money', 'client fund', 'customer money', 'deposit',
            'hold', 'holding', 'segregate', 'separate', 'account'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not mention holding or handling client money',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check if firm holds client money
        holding_patterns = [
            r'(?:hold|holding|receive|accept)\s+(?:client|customer)\s+(?:money|fund)',
            r'(?:client|customer)\s+(?:money|fund)s?\s+(?:held|received|accepted)',
            r'(?:deposit|payment)\s+(?:held|kept|maintained)',
            r'(?:we|firm)\s+(?:hold|receive|accept).*(?:money|fund|payment)'
        ]

        holds_client_money = False
        for pattern in holding_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                holds_client_money = True
                for m in matches:
                    spans.append({
                        'type': 'client_money_holding',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        if not holds_client_money:
            return {'status': 'N/A'}

        # Check for segregation statement
        segregation_patterns = [
            r'segregate(?:d|s)?',
            r'separate(?:d|s)?\s+(?:account|bank\s+account)',
            r'client\s+(?:money|fund)\s+account',
            r'(?:held\s+in\s+)?(?:a\s+)?segregate(?:d)?\s+account',
            r'(?:ring-?fence|ringfence)(?:d)?',
            r'(?:protect|safeguard)(?:ed)?\s+(?:in\s+)?(?:separate|designated)\s+account'
        ]

        has_segregation = False
        for pattern in segregation_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_segregation = True
                for m in matches:
                    spans.append({
                        'type': 'segregation_statement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for CASS compliance reference
        cass_patterns = [
            r'\bcass\b',
            r'client\s+assets?\s+sourcebook',
            r'fca\s+(?:client\s+)?(?:money|asset)\s+rule',
            r'cass\s+[0-9]'
        ]

        has_cass_ref = False
        for pattern in cass_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_cass_ref = True
                for m in matches:
                    spans.append({
                        'type': 'cass_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for protection statements
        protection_patterns = [
            r'(?:protect|safe|secure)(?:ed)?\s+(?:from|in\s+the\s+event\s+of)',
            r'(?:insolvency|bankruptcy)\s+(?:protection|protection)',
            r'(?:not|never)\s+(?:mixed|commingled|combined)\s+(?:with|and)\s+(?:firm|our)',
            r'(?:your|client)\s+money.*(?:safe|protected|ring-?fenced)',
            r'fscs\s+(?:protection|protected|cover)'
        ]

        has_protection = False
        for pattern in protection_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_protection = True
                for m in matches:
                    spans.append({
                        'type': 'protection_statement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for reconciliation mention
        reconciliation_patterns = [
            r'(?:daily|regular|periodic)\s+reconciliation',
            r'reconcile(?:d)?\s+(?:daily|regularly)',
            r'(?:check|verify|confirm)\s+(?:balance|amount)s?',
            r'client\s+money\s+(?:reconciliation|calculation)'
        ]

        has_reconciliation = False
        for pattern in reconciliation_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_reconciliation = True
                for m in matches:
                    spans.append({
                        'type': 'reconciliation',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for negative indicators (red flags)
        negative_patterns = [
            r'(?:mixed|commingled|combined)\s+with\s+(?:firm|our)\s+(?:money|fund)',
            r'(?:firm|company)\s+(?:account|money|fund)',
            r'(?:not|no)\s+segregate(?:d)?',
            r'(?:held\s+in\s+)?(?:our|firm)\s+(?:general|own)\s+account'
        ]

        has_violations = []
        for pattern in negative_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches:
                    has_violations.append(m.group())
                    spans.append({
                        'type': 'cass_violation',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'critical'
                    })

        # Determine status
        # Critical failure: Violations detected
        if has_violations:
            details = []
            for violation in has_violations[:3]:
                details.append(f'Violation: {violation}')
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Critical CASS violation: Client money not properly segregated',
                'legal_source': self.legal_source,
                'suggestion': 'CASS 7 MANDATORY: Client money must be held in segregated client bank accounts, not mixed with firm money. This is a fundamental regulatory requirement.',
                'spans': spans,
                'details': details
            }

        # Critical failure: Holds client money but no segregation statement
        if holds_client_money and not has_segregation:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Client money held but no segregation statement',
                'legal_source': self.legal_source,
                'suggestion': 'CASS 7 requires explicit statement that client money is held in segregated client bank accounts separate from firm money.',
                'spans': spans
            }

        # Pass with good compliance indicators
        compliance_elements = []
        if has_segregation:
            compliance_elements.append('segregation stated')
        if has_cass_ref:
            compliance_elements.append('CASS referenced')
        if has_protection:
            compliance_elements.append('protection explained')
        if has_reconciliation:
            compliance_elements.append('reconciliation mentioned')

        if len(compliance_elements) >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Client money segregation requirements met ({len(compliance_elements)} elements: {", ".join(compliance_elements)})',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Marginal pass: Segregation stated but minimal detail
        if has_segregation:
            details = []
            details.append('Suggestion: Consider adding CASS compliance reference, insolvency protection statement, or reconciliation process')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Client money segregation stated (consider adding more detail)',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Should not reach here given earlier checks, but safety net
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Client money mentioned but segregation unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Explicitly state that client money is held in segregated accounts per CASS 7.',
            'spans': spans
        }
