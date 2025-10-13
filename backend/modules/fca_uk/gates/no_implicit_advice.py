import re


class NoImplicitAdviceGate:
    def __init__(self):
        self.name = "no_implicit_advice"
        self.severity = "critical"
        self.legal_source = "FCA COBS 2.1 & 9 (Acting Honestly, Fairly and Professionally / Suitability)"

    def _is_relevant(self, text):
        """Check if document contains recommendations or suggestions"""
        text_lower = text.lower()
        keywords = [
            'recommend', 'suggest', 'should', 'could', 'consider',
            'suitable', 'appropriate', 'right for you', 'best',
            'invest', 'buy', 'apply', 'choose'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not contain recommendation or advisory language',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for advice/recommendation language
        # ENHANCED: Added softer advisory language patterns
        advice_patterns = [
            r'\b(?:recommend|recommending|recommendation)s?\b',
            r'\b(?:suggest|suggesting|suggestion)s?\b',
            r'(?:you\s+)?should\s+(?:invest|buy|apply|consider|choose)',
            r'(?:we\s+)?(?:advise|advice)\s+(?:you\s+)?(?:to)?',
            r'(?:best|right|suitable|ideal|perfect)\s+(?:for\s+you|choice|option)',
            r'(?:this|that)\s+(?:is|would\s+be)\s+(?:suitable|appropriate|right)\s+for\s+you',
            r'(?:tailored|personalised|personal)\s+(?:recommendation|advice|suggestion)',
            # Softer advisory language patterns:
            r'(?:you\s+)?(?:might|may|could)\s+(?:want\s+to|wish\s+to)?\s*consider',
            r'it\s+(?:might|may|could|would)\s+be\s+(?:beneficial|worth|wise|good)',
            r'perhaps\s+(?:you\s+)?(?:should|could|might)',
            r'(?:you\s+)?(?:might|may|could)\s+(?:look\s+at|think\s+about)',
            r'(?:beneficial|worthwhile|advisable)\s+(?:to|for\s+you\s+to)'
        ]

        gives_advice = False
        for pattern in advice_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                gives_advice = True
                for m in matches:
                    spans.append({
                        'type': 'advice_language',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high'
                    })

        if not gives_advice:
            return {'status': 'N/A'}

        # Check for KYC/suitability assessment indicators
        kyc_patterns = [
            r'(?:know\s+your\s+customer|kyc)',
            r'suitability\s+(?:assessment|report|analysis)',
            r'(?:assess|assessed|assessing)\s+(?:your\s+)?(?:needs|circumstances|objectives|situation)',
            r'(?:financial\s+)?(?:questionnaire|fact[\s-]find)',
            r'(?:your\s+)?(?:risk\s+)?(?:profile|appetite|tolerance)',
            r'(?:understanding|knowledge)\s+(?:of|and)\s+experience',
            r'(?:information\s+)?(?:about|on)\s+(?:your\s+)?(?:financial\s+)?(?:situation|circumstances|position)'
        ]

        has_kyc = False
        for pattern in kyc_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_kyc = True
                for m in matches:
                    spans.append({
                        'type': 'kyc_indicator',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for disclaimer (that it's not advice)
        disclaimer_patterns = [
            r'(?:this\s+is\s+)?not\s+(?:financial\s+)?(?:advice|a\s+recommendation)',
            r'(?:not\s+)?(?:personal|personalised)\s+advice',
            r'(?:general|generic)\s+(?:information|guidance)\s+only',
            r'(?:does\s+not\s+constitute|should\s+not\s+be\s+(?:considered|treated)\s+as)\s+(?:financial\s+)?advice',
            r'(?:seek|obtain|take)\s+(?:professional|independent|financial)\s+advice',
            r'(?:speak\s+to|consult)\s+(?:a\s+)?(?:financial\s+)?(?:adviser|advisor)',
            r'(?:information|guidance)\s+(?:purposes\s+)?only'
        ]

        has_disclaimer = False
        for pattern in disclaimer_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_disclaimer = True
                for m in matches:
                    spans.append({
                        'type': 'advice_disclaimer',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for execution-only language
        execution_only_patterns = [
            r'execution[\s-]only',
            r'(?:non-?advised|without\s+advice)\s+(?:sale|basis|service)',
            r'(?:you\s+)?(?:are\s+)?making\s+your\s+own\s+(?:decision|choice)',
            r'(?:decision|choice)\s+is\s+yours',
            r'(?:we\s+)?(?:do\s+not|cannot)\s+(?:advise|provide\s+advice)'
        ]

        is_execution_only = False
        for pattern in execution_only_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                is_execution_only = True
                for m in matches:
                    spans.append({
                        'type': 'execution_only',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for authorization to provide advice
        authorization_patterns = [
            r'(?:authorised|licensed)\s+(?:to\s+)?(?:provide|give)\s+(?:financial\s+)?advice',
            r'fca\s+(?:authorised|regulated)\s+(?:adviser|advisor|firm)',
            r'(?:independent|restricted)\s+financial\s+(?:adviser|advisor)',
            r'(?:we\s+are\s+)?(?:authorised|permitted)\s+(?:by\s+the\s+fca\s+)?to\s+(?:advise|provide\s+advice)'
        ]

        is_authorized = False
        for pattern in authorization_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                is_authorized = True
                for m in matches:
                    spans.append({
                        'type': 'advice_authorization',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        # Critical: Gives advice without KYC AND without disclaimer
        if gives_advice and not has_kyc and not has_disclaimer and not is_authorized:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Implicit personal advice without suitability assessment or disclaimer',
                'legal_source': self.legal_source,
                'suggestion': 'Providing personal recommendations without assessing suitability breaches COBS 9. Either: (1) Add "This is not financial advice" disclaimer and "Seek professional advice", OR (2) Conduct proper suitability assessment and document KYC.',
                'spans': spans
            }

        # Fail: Gives advice with KYC but not authorized
        if gives_advice and has_kyc and not is_authorized and not has_disclaimer:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Personal advice provided but authorization not stated',
                'legal_source': self.legal_source,
                'suggestion': 'Only FCA-authorized firms can provide financial advice. State authorization or add disclaimer that it\'s not advice.',
                'spans': spans
            }

        # Warning: Advice language with disclaimer (borderline)
        if gives_advice and has_disclaimer and not is_execution_only:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Advice-like language despite disclaimer',
                'legal_source': self.legal_source,
                'suggestion': 'Disclaimer present but language still sounds like advice. Use more neutral wording ("may consider", "options include", "information only") or move to execution-only.',
                'spans': spans
            }

        # Pass: Authorized and conducted KYC
        if gives_advice and is_authorized and has_kyc:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Personal advice with proper authorization and suitability assessment',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Pass: Execution-only clearly stated
        if is_execution_only:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Execution-only basis clearly stated',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Pass: Good disclaimer
        if has_disclaimer:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Appropriate "not advice" disclaimer present',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Default warning
        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Advice-like language - ensure appropriate disclaimers',
            'legal_source': self.legal_source,
            'suggestion': 'Add clear disclaimer or establish proper advised status with suitability.',
            'spans': spans
        }
