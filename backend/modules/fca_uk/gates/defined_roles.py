import re


class DefinedRolesGate:
    def __init__(self):
        self.name = "defined_roles"
        self.severity = "medium"
        self.legal_source = "FCA SYSC 4 & 5 (Senior Management Arrangements)"

    def _is_relevant(self, text):
        """Check if document describes processes or procedures"""
        text_lower = text.lower()
        keywords = [
            'process', 'procedure', 'responsible', 'accountability',
            'role', 'oversight', 'approve', 'review', 'decision'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not describe processes, procedures, or accountability structures',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for Senior Management Function (SMF) references
        smf_patterns = [
            r'smf\s*[0-9]{1,2}',
            r'senior\s+management\s+function',
            r'(?:chief\s+)?(?:executive|operating|financial|risk|compliance)\s+officer',
            r'\b(?:ceo|coo|cfo|cro|cco)\b',
            r'(?:head\s+of|director\s+of)\s+(?:compliance|risk|operations|finance)',
            r'responsible\s+(?:senior\s+)?(?:manager|person)'
        ]

        has_smf = False
        for pattern in smf_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_smf = True
                for m in matches:
                    spans.append({
                        'type': 'smf_reference',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for role/responsibility assignment
        responsibility_patterns = [
            r'(?:responsible|accountability|accountable)\s+(?:for|to)',
            r'(?:role|duty|function)\s+(?:of|is\s+to)',
            r'(?:assigned|designated|appointed)\s+to',
            r'(?:ownership|owner)\s+(?:of|for|is)',
            r'(?:shall|will|must)\s+(?:be\s+)?(?:approved|reviewed|overseen)\s+by'
        ]

        has_responsibility = False
        for pattern in responsibility_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_responsibility = True
                for m in matches:
                    spans.append({
                        'type': 'responsibility_assignment',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for specific role titles
        role_patterns = [
            r'(?:compliance|risk|operations|product|distribution)\s+(?:manager|officer|director|lead)',
            r'(?:money\s+laundering\s+reporting|data\s+protection|financial\s+crime)\s+officer',
            r'\b(?:mlro|dpo)\b',
            r'(?:board|committee)\s+(?:member|director)',
            r'(?:senior|executive)\s+(?:manager|leadership|team)'
        ]

        has_role_titles = False
        for pattern in role_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_role_titles = True
                for m in matches:
                    spans.append({
                        'type': 'role_title',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for approval/oversight language
        approval_patterns = [
            r'(?:approved|authorised|signed\s+off)\s+by',
            r'(?:subject\s+to|require|requires)\s+(?:approval|authorisation|sign-off)',
            r'(?:overseen|supervised|monitored)\s+by',
            r'(?:board|committee|senior\s+management)\s+(?:approval|oversight|review)'
        ]

        has_approval = False
        for pattern in approval_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_approval = True
                for m in matches:
                    spans.append({
                        'type': 'approval_requirement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for governance structure
        governance_patterns = [
            r'governance\s+(?:structure|framework|arrangement)',
            r'(?:reporting|escalation)\s+(?:line|structure|path)',
            r'three\s+lines\s+of\s+(?:defence|defense)',
            r'(?:first|second|third)\s+line',
            r'organisational\s+structure'
        ]

        has_governance = False
        for pattern in governance_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_governance = True
                for m in matches:
                    spans.append({
                        'type': 'governance_structure',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for vague/unclear responsibility
        # ENHANCED: Added more vague language patterns
        vague_patterns = [
            r'(?:relevant|appropriate|designated)\s+(?:person|team|department)',
            r'(?:someone|anyone|staff)\s+(?:will|shall|should)',
            r'(?:to\s+be\s+)?(?:determined|decided|confirmed)',
            r'(?:as\s+)?(?:appropriate|necessary|required)',
            # Additional vague patterns:
            r'(?:various|different|several)\s+(?:people|staff|individuals)',
            r'(?:the\s+)?(?:management\s+)?team\s+(?:oversees?|looks?\s+after|handles?)',
            r'managers?\s+(?:looking\s+after|responsible\s+for)\s+(?:different|various)\s+things?',
            r'(?:people|staff)\s+(?:are\s+)?responsible'
        ]

        has_vague_responsibility = False
        for pattern in vague_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if it's about responsibility/approval
                for m in matches:
                    context_start = max(0, m.start() - 100)
                    context_end = min(len(text), m.end() + 100)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['responsible', 'approve', 'review', 'oversight', 'decision', 'function', 'duty']):
                        has_vague_responsibility = True
                        spans.append({
                            'type': 'vague_responsibility',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'medium'
                        })

        # Determine status
        clarity_elements = []
        issues = []

        if has_smf:
            clarity_elements.append('SMF referenced')
        if has_role_titles:
            clarity_elements.append('specific role titles')
        if has_responsibility:
            clarity_elements.append('responsibilities assigned')
        if has_approval:
            clarity_elements.append('approval process defined')
        if has_governance:
            clarity_elements.append('governance structure')

        # Warning: Vague responsibility
        if has_vague_responsibility:
            issues.append('Vague or unspecified responsibility assignments detected')

        # Warning: No clear roles
        if len(clarity_elements) == 0:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No clearly defined roles or responsibilities',
                'legal_source': self.legal_source,
                'suggestion': 'SYSC requires clear accountability. Specify who is responsible (role/SMF), who approves, and who oversees processes.',
                'spans': spans
            }

        # ENHANCED: Prioritize vague language warnings even with some clarity elements
        if has_vague_responsibility:
            details = []
            for issue in issues:
                details.append(issue)
            for element in clarity_elements:
                details.append(f'Some clarity: {element}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Responsibility assignments may be too vague despite some clarity',
                'legal_source': self.legal_source,
                'suggestion': 'Replace vague terms ("appropriate person", "management team", "various people") with specific roles or SMF references.',
                'spans': spans,
                'details': details
            }

        # Pass with good clarity
        if len(clarity_elements) >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Roles and responsibilities clearly defined ({len(clarity_elements)} elements: {", ".join(clarity_elements)})',
                'legal_source': self.legal_source,
                'spans': spans
            }

        # Marginal pass
        details = []
        for element in clarity_elements:
            details.append(element)
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Some role clarity present',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
