import re


class ReasonableAdjustmentsGate:
    def __init__(self):
        self.name = "reasonable_adjustments"
        self.severity = "medium"
        self.legal_source = "FCA FG21/1 & Equality Act 2010 (Reasonable Adjustments)"

    def _is_relevant(self, text):
        """Check if document mentions disability, vulnerability, or accessibility"""
        text_lower = text.lower()
        keywords = [
            'disability', 'disabled', 'vulnerable', 'accessibility',
            'impairment', 'adjustment', 'support', 'accommodate',
            'alternative', 'format', 'accessible'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not address disability, accessibility, or customer support accommodations',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for reasonable adjustments offered
        adjustment_types = {
            'communication': [
                r'alternative\s+format',
                r'(?:large\s+print|braille|audio)',
                r'(?:email|phone|video)\s+call',
                r'(?:british\s+)?sign\s+language',
                r'(?:translator|interpretation)\s+service',
                r'plain\s+(?:english|language)'
            ],
            'time': [
                r'(?:extra|additional|more)\s+time',
                r'(?:extended|longer)\s+(?:deadline|timeframe|period)',
                r'(?:flexible|adjusted)\s+(?:deadline|timeline)',
                r'take\s+your\s+time',
                r'no\s+(?:rush|pressure)'
            ],
            'process': [
                r'(?:simplified|simpler)\s+(?:process|procedure|form)',
                r'(?:help|assistance|support)\s+(?:completing|with)',
                r'(?:face-to-face|in-person)\s+(?:meeting|appointment)',
                r'home\s+visit',
                r'step-by-step\s+(?:guide|help)'
            ],
            'channel': [
                r'(?:alternative|different)\s+(?:method|way|channel)',
                r'(?:phone|online|post|email|branch)\s+(?:available|option)',
                r'(?:speak|talk)\s+to\s+(?:someone|person|advisor)',
                r'(?:contact\s+)?(?:us\s+)?(?:via|by|through)',
                r'(?:multiple|various)\s+(?:way|method|channel)'
            ]
        }

        offered_adjustments = {}
        for adjustment_type, patterns in adjustment_types.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if adjustment_type not in offered_adjustments:
                        offered_adjustments[adjustment_type] = []
                    for m in matches:
                        offered_adjustments[adjustment_type].append(m.group())
                        spans.append({
                            'type': f'adjustment_{adjustment_type}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for explicit "reasonable adjustments" language
        reasonable_adjustment_patterns = [
            r'reasonable\s+adjustment',
            r'accommodate\s+(?:your\s+)?(?:need|circumstance|situation)',
            r'(?:adapted|tailored)\s+(?:service|support|approach)',
            r'(?:we\s+)?can\s+(?:adjust|adapt|modify|change)',
            r'let\s+us\s+know.*(?:need|require|help)'
        ]

        has_explicit_ra = False
        for pattern in reasonable_adjustment_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_explicit_ra = True
                for m in matches:
                    spans.append({
                        'type': 'explicit_reasonable_adjustment',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for proactive invitation to request adjustments
        invitation_patterns = [
            r'(?:please\s+)?(?:let\s+us\s+know|tell\s+us|inform\s+us).*(?:need|require|support)',
            r'if\s+you\s+(?:need|require|would\s+like).*(?:support|help|adjustment)',
            r'(?:ask|speak\s+to\s+us)\s+about.*(?:need|support|help)',
            r'(?:we\'re|we\s+are)\s+here\s+to\s+help'
        ]

        has_invitation = False
        for pattern in invitation_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_invitation = True
                for m in matches:
                    spans.append({
                        'type': 'adjustment_invitation',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for barriers (negative indicators)
        barrier_patterns = [
            r'(?:must|only|required\s+to)\s+(?:complete|submit|attend).*(?:online|in\s+person)',
            r'no\s+(?:alternative|other\s+option)',
            r'(?:unable|not\s+able|cannot)\s+to\s+(?:provide|offer|accommodate)',
            r'(?:standard|normal)\s+process\s+(?:only|applies)'
        ]

        barriers_found = []
        for pattern in barrier_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                for m in matches:
                    barriers_found.append(m.group())
                    spans.append({
                        'type': 'adjustment_barrier',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        # Determine status
        adjustment_count = len(offered_adjustments)

        # Fail if barriers detected
        if barriers_found:
            details = []
            for barrier in barriers_found[:3]:
                details.append(f'Barrier: {barrier}')
            return {
                'status': 'FAIL',
                'severity': 'medium',
                'message': 'Process barriers detected - may prevent reasonable adjustments',
                'legal_source': self.legal_source,
                'suggestion': 'Remove mandatory single-channel requirements. Offer alternatives (e.g., if online form required, offer phone/paper option for those who need it).',
                'spans': spans,
                'details': details
            }

        # Warning if no adjustments mentioned but document discusses disability/vulnerability
        if adjustment_count == 0 and not has_explicit_ra and not has_invitation:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Disability/vulnerability mentioned but no reasonable adjustments offered',
                'legal_source': self.legal_source,
                'suggestion': 'Offer reasonable adjustments such as: alternative formats, extra time, different communication channels, or simplified processes.',
                'spans': spans
            }

        # Pass with good coverage
        if adjustment_count >= 2 or has_explicit_ra:
            details = []
            details.append(f'Adjustment types: {", ".join(offered_adjustments.keys())}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Reasonable adjustments offered ({adjustment_count} types: {", ".join(offered_adjustments.keys())})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Pass with invitation
        if has_invitation:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Customers invited to request adjustments',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Marginal pass
        if adjustment_count == 1:
            details = []
            details.append(f'Adjustment types: {", ".join(offered_adjustments.keys())}')
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Some adjustments offered ({list(offered_adjustments.keys())[0]})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        return {'status': 'N/A'}
