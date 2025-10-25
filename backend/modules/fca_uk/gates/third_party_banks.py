import re


class ThirdPartyBanksGate:
    def __init__(self):
        self.name = "third_party_banks"
        self.severity = "high"
        self.legal_source = "FCA CASS 7.13 (Selection and Monitoring of Third Party Banks)"

    def _is_relevant(self, text):
        """Check if document mentions banks or where money is held"""
        text_lower = text.lower()
        keywords = [
            'bank', 'banking', 'third party', 'deposit', 'account',
            'financial institution', 'held with', 'held at'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not reference third-party banking arrangements',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        negative_indicators = [
            r'preferred\s+banking\s+partners?\s+\(list\s+(?:kept\s+)?confidential',
            r'we\s+do\s+not\s+(?:publish|disclose)\s+the\s+list\s+of\s+banks',
            r'formal\s+cass\s+segregation\s+is\s+unnecessary',
            r'daily\s+reconciliation\s+(?:is\s+)?(?:optional|not\s+required)',
            r'client\s+money\s+.*(?:our|firm)\s+(?:master|operations?)\s+account'
        ]

        for pattern in negative_indicators:
            match = re.search(pattern, text_lower)
            if match:
                spans.append({
                    'type': 'cass_713_violation',
                    'start': match.start(),
                    'end': match.end(),
                    'text': text[match.start():match.end()],
                    'severity': 'critical'
                })
                return {
                    'status': 'FAIL',
                    'severity': 'high',
                    'message': 'Third-party bank arrangements described without required due diligence or segregation',
                    'legal_source': self.legal_source,
                    'suggestion': 'CASS 7.13 requires identifying approved banks, documenting selection criteria, and confirming segregation/monitoring arrangements.',
                    'spans': spans
                }

        # Check if client money is held at third party banks
        third_party_patterns = [
            r'(?:held|deposited|kept|maintained)\s+(?:with|at|in)\s+(?:a\s+)?(?:third[\s-]party|external|separate)\s+bank',
            r'(?:third[\s-]party|external)\s+(?:bank|banking|financial\s+institution)',
            r'client\s+(?:money|fund)\s+(?:account|held).*(?:bank|institution)',
            r'(?:deposited|held)\s+with.*(?:bank|institution)'
        ]

        uses_third_party_banks = False
        for pattern in third_party_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                uses_third_party_banks = True
                for m in matches:
                    spans.append({
                        'type': 'third_party_bank_usage',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Also check for specific bank mentions (implies third party)
        bank_name_patterns = [
            r'\b(?:barclays|hsbc|lloyds|natwest|santander|rbs|metro\s+bank)\b',
            r'(?:with|at)\s+(?:a\s+)?(?:uk|authorised|regulated)\s+bank'
        ]

        for pattern in bank_name_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if in context of client money
                for m in matches:
                    context_start = max(0, m.start() - 200)
                    context_end = min(len(text), m.end() + 200)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['client money', 'client fund', 'segregated', 'account']):
                        uses_third_party_banks = True
                        spans.append({
                            'type': 'specific_bank_mention',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'medium'
                        })

        if not uses_third_party_banks:
            return {'status': 'N/A'}

        # Check for due diligence statement
        due_diligence_patterns = [
            r'due\s+diligence',
            r'(?:assess|evaluate|review|monitor)(?:ed|ing)?\s+(?:the\s+)?(?:bank|institution)',
            r'selection\s+(?:of|criteria|process)',
            r'(?:careful|thorough|appropriate)(?:ly)?\s+(?:select|chosen|assess)',
            r'(?:credit)?worthiness',
            r'financial\s+(?:strength|stability|soundness)'
        ]

        has_due_diligence = False
        for pattern in due_diligence_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_due_diligence = True
                for m in matches:
                    spans.append({
                        'type': 'due_diligence',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for authorization/regulation mention
        authorization_patterns = [
            r'(?:fca|pra)[\s-]?(?:authorised|regulated|approved)',
            r'(?:authorised|regulated|licensed)\s+(?:by\s+)?(?:the\s+)?(?:fca|pra)',
            r'uk\s+(?:authorised|regulated)\s+bank',
            r'prudential\s+regulation',
            r'deposit\s+protection'
        ]

        has_authorization = False
        for pattern in authorization_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_authorization = True
                for m in matches:
                    spans.append({
                        'type': 'bank_authorization',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for ongoing monitoring
        monitoring_patterns = [
            r'(?:ongoing|regular|periodic|continuous)\s+(?:monitoring|review|assessment)',
            r'monitor(?:ed|ing)?\s+(?:on\s+)?(?:an\s+)?ongoing',
            r'(?:review|assess)(?:ed|ing)?\s+(?:regularly|periodically|annually)',
            r'(?:annual|quarterly)\s+(?:review|assessment)'
        ]

        has_monitoring = False
        for pattern in monitoring_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if in context of banks
                for m in matches:
                    context_start = max(0, m.start() - 150)
                    context_end = min(len(text), m.end() + 150)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['bank', 'institution', 'third party', 'deposit']):
                        has_monitoring = True
                        spans.append({
                            'type': 'bank_monitoring',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for diversification mention
        diversification_patterns = [
            r'(?:spread|diversif|distribut)(?:ed|ing|ion)?\s+(?:across|among|between)',
            r'(?:multiple|several|more\s+than\s+one)\s+(?:bank|institution)',
            r'(?:not|no)\s+(?:single|one)\s+bank',
            r'risk\s+(?:spread|diversification)'
        ]

        has_diversification = False
        for pattern in diversification_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_diversification = True
                for m in matches:
                    spans.append({
                        'type': 'bank_diversification',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for FSCS mention
        fscs_patterns = [
            r'\bfscs\b',
            r'financial\s+services\s+compensation\s+scheme',
            r'deposit\s+(?:insurance|protection|guarantee)',
            r'£85,?000\s+(?:protected|covered|guaranteed)'
        ]

        has_fscs = False
        for pattern in fscs_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_fscs = True
                for m in matches:
                    spans.append({
                        'type': 'fscs_protection',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        protection_elements = []
        missing_elements = []

        if has_due_diligence:
            protection_elements.append('due diligence')
        else:
            missing_elements.append('due diligence on bank selection')

        if has_authorization:
            protection_elements.append('FCA/PRA authorization confirmed')

        if has_monitoring:
            protection_elements.append('ongoing monitoring')
        else:
            missing_elements.append('ongoing monitoring of banks')

        if has_diversification:
            protection_elements.append('diversification across banks')

        if has_fscs:
            protection_elements.append('FSCS protection')

        # Fail: Uses third party banks but no due diligence statement
        if not has_due_diligence and not has_authorization:
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Third-party banks used but no due diligence statement',
                'legal_source': self.legal_source,
                'suggestion': 'CASS 7.13 requires firms to exercise due diligence in selecting banks. State that banks are FCA/PRA authorised and subject to selection criteria and ongoing review.',
                'spans': spans
            }

        # Warning: Due diligence mentioned but no ongoing monitoring
        if has_due_diligence and not has_monitoring:
            details = []
            for element in protection_elements:
                details.append(element)
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Bank selection mentioned but ongoing monitoring not stated',
                'legal_source': self.legal_source,
                'suggestion': 'CASS 7.13 requires ongoing monitoring of third-party banks, not just initial selection.',
                'spans': spans,
                'details': details
            }

        # Pass: Good coverage
        if len(protection_elements) >= 2:
            details = []
            for element in protection_elements:
                details.append(element)
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Third-party bank safeguards in place ({len(protection_elements)} elements: {", ".join(protection_elements)})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Marginal pass
        details = []
        for element in protection_elements:
            details.append(element)
        for element in missing_elements:
            details.append(f'Consider adding: {element}')
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Some third-party bank controls mentioned',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
