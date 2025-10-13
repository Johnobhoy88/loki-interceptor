import re


class ConflictsDeclarationGate:
    def __init__(self):
        self.name = "conflicts_declaration"
        self.severity = "high"
        self.legal_source = "FCA SYSC 10 (Conflicts of Interest)"

    def _is_relevant(self, text):
        """Check if document involves advice, recommendations, or arrangements"""
        text_lower = text.lower()
        keywords = [
            'advice', 'recommend', 'arrange', 'facilitate', 'introduce',
            'conflict', 'interest', 'impartial', 'independent', 'commission'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not provide advice or recommendations requiring conflict disclosure',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check if advice/recommendation is being provided
        advice_patterns = [
            r'\b(?:advice|advise|advising|advisor|adviser)\b',
            r'\b(?:recommend|recommendation|suggesting|suggest)\b',
            r'(?:arrange|arranging)\s+(?:a|the)\s+(?:product|policy|investment|mortgage)',
            r'(?:introduce|introduction)\s+(?:to|you\s+to)',
            r'(?:facilitate|facilitation)'
        ]

        provides_advice = False
        for pattern in advice_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                provides_advice = True
                for m in matches:
                    spans.append({
                        'type': 'advice_provision',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'medium'
                    })

        if not provides_advice:
            return {'status': 'N/A'}

        # Check for conflicts of interest disclosure
        # ENHANCED: Must have explicit "conflict of interest" language, not just mentioning payments
        conflict_disclosure_patterns = [
            r'conflict(?:s)?\s+of\s+interest',
            r'(?:potential|possible|may\s+have)\s+(?:a\s+)?conflict',
            r'(?:manage|managing|disclose|disclos(?:ure|ing))\s+(?:our\s+)?conflict',
            r'conflict(?:s)?\s+(?:policy|procedure|management|disclosure)'
        ]

        has_conflict_disclosure = False
        for pattern in conflict_disclosure_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_conflict_disclosure = True
                for m in matches:
                    spans.append({
                        'type': 'conflict_disclosure',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for conflicts policy reference
        policy_patterns = [
            r'conflict(?:s)?\s+(?:of\s+interest\s+)?policy',
            r'(?:manage|managing|management\s+of)\s+conflict',
            r'conflict(?:s)?\s+(?:procedure|framework|approach)',
            r'(?:identify|prevent|manage)\s+conflict'
        ]

        has_policy_reference = False
        for pattern in policy_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_policy_reference = True
                for m in matches:
                    spans.append({
                        'type': 'conflicts_policy',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for specific conflict examples
        specific_conflicts = {
            'commission': [
                r'\b(?:commission|fee|remuneration)\s+(?:from|paid\s+by)',
                r'(?:receive|earn|paid)\s+(?:a\s+)?commission',
                r'commission-based'
            ],
            'ownership': [
                r'(?:own|ownership|owned\s+by|part\s+of)\s+(?:the\s+)?(?:provider|manufacturer|company)',
                r'(?:sister|parent|group)\s+company',
                r'related\s+(?:entity|party|company)'
            ],
            'restricted_panel': [
                r'restricted\s+(?:advice|panel|range)',
                r'limited\s+(?:panel|range)\s+of',
                r'(?:only|exclusively)\s+(?:from|with)\s+(?:selected|certain|specific)'
            ]
        }

        disclosed_conflicts = {}
        for conflict_type, patterns in specific_conflicts.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    if conflict_type not in disclosed_conflicts:
                        disclosed_conflicts[conflict_type] = []
                    for m in matches:
                        disclosed_conflicts[conflict_type].append(m.group())
                        spans.append({
                            'type': f'conflict_{conflict_type}',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'medium' if not has_conflict_disclosure else 'none'
                        })

        # Check for independence claims (potential issue if conflicts exist)
        independence_patterns = [
            r'\b(?:independent|impartial|unbiased|objective)\b',
            r'no\s+(?:conflict|bias|interest)',
            r'(?:whole|entire)\s+(?:of\s+)?market'
        ]

        claims_independence = False
        for pattern in independence_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                claims_independence = True
                for m in matches:
                    spans.append({
                        'type': 'independence_claim',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'high' if disclosed_conflicts else 'none'
                    })

        # Determine status
        issues = []

        # Critical: Claims independence but has undisclosed conflicts
        if claims_independence and disclosed_conflicts and not has_conflict_disclosure:
            details = []
            details.append(f'Undisclosed conflicts: {", ".join(list(disclosed_conflicts.keys()))}')
            return {
                'status': 'FAIL',
                'severity': 'high',
                'message': 'Independence claimed but conflicts of interest not disclosed',
                'legal_source': self.legal_source,
                'suggestion': 'SYSC 10 requires disclosure of conflicts. If you receive commission, are part of provider group, or have restricted panel, you cannot claim to be independent.',
                'spans': spans,
                'details': details
            }

        # Fail: Advice provided but no conflicts policy
        if provides_advice and not has_policy_reference and not has_conflict_disclosure:
            issues.append('No conflicts of interest policy or disclosure')

        # Warning: Specific conflicts identified but not explicitly disclosed
        if disclosed_conflicts and not has_conflict_disclosure:
            issues.append(f'Potential conflicts detected ({", ".join(disclosed_conflicts.keys())}) but not explicitly disclosed')

        # Failures and warnings
        if len(issues) > 0:
            severity = 'high' if 'No conflicts' in str(issues) else 'high'
            details = []
            for issue in issues:
                details.append(issue)
            return {
                'status': 'FAIL' if severity == 'high' and len(issues) >= 1 else 'WARNING',
                'severity': 'medium' if 'WARNING' in ['WARNING'] else severity,
                'message': 'Conflicts of interest disclosure required',
                'legal_source': self.legal_source,
                'suggestion': 'Include conflicts of interest policy. Disclose any commissions, ownership relationships, or panel restrictions.',
                'spans': spans,
                'details': details
            }

        # Pass: Conflicts appropriately disclosed
        if has_conflict_disclosure or has_policy_reference:
            disclosure_quality = []
            if has_conflict_disclosure:
                disclosure_quality.append('conflicts disclosed')
            if has_policy_reference:
                disclosure_quality.append('policy referenced')
            if disclosed_conflicts:
                disclosure_quality.append(f'{len(disclosed_conflicts)} specific conflict types mentioned')

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Conflicts of interest appropriately addressed ({", ".join(disclosure_quality)})',
                'legal_source': self.legal_source,
                'spans': spans
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'No significant conflicts of interest issues detected',
            'legal_source': self.legal_source,
            'spans': spans
        }
