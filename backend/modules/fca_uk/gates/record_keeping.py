import re


class RecordKeepingGate:
    def __init__(self):
        self.name = "record_keeping"
        self.severity = "medium"
        self.legal_source = "FCA SYSC 9 (Record Keeping)"

    def _is_relevant(self, text):
        """Check if document mentions records, documentation, or retention"""
        text_lower = text.lower()
        keywords = [
            'record', 'document', 'retain', 'keep', 'store', 'maintain',
            'evidence', 'proof', 'log', 'register', 'file'
        ]
        return any(kw in text_lower for kw in keywords)

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document does not discuss record retention or documentation policies',
                'legal_source': self.legal_source
            }

        text_lower = text.lower()
        spans = []

        # Check for record-keeping mentions
        record_patterns = [
            r'(?:maintain|keep|retain|store)\s+(?:a\s+)?(?:record|log|register|file)',
            r'(?:record|document|evidence)\s+(?:of|shall\s+be\s+kept)',
            r'(?:recording|documentation)\s+(?:requirement|process)',
            r'audit\s+trail'
        ]

        has_record_keeping = False
        for pattern in record_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_record_keeping = True
                for m in matches:
                    spans.append({
                        'type': 'record_keeping_mention',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        if not has_record_keeping:
            return {'status': 'N/A'}

        # Check for WHAT records are kept
        what_patterns = [
            r'record(?:s)?\s+(?:of|include|including)\s+(?:all|each|any)',
            r'(?:decision|advice|transaction|complaint|communication|call|email|meeting)',
            r'(?:customer|client)\s+(?:file|record|documentation)',
            r'(?:suitability|appropriateness)\s+(?:assessment|report)',
            r'(?:compliance|risk)\s+(?:assessment|review|report)'
        ]

        has_what = False
        for pattern in what_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_what = True
                for m in matches:
                    spans.append({
                        'type': 'record_what',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for WHERE records are stored
        where_patterns = [
            r'(?:stored|kept|maintained)\s+(?:in|on|at)\s+(?:the|our)',
            r'(?:central|secure|electronic|digital)\s+(?:repository|system|database|filing)',
            r'(?:cloud|server|system|sharepoint|drive)',
            r'(?:physical|paper)\s+(?:file|storage)',
            r'client\s+(?:file|folder|record\s+system)'
        ]

        has_where = False
        for pattern in where_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_where = True
                for m in matches:
                    spans.append({
                        'type': 'record_where',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for HOW LONG records are retained
        retention_patterns = [
            r'(?:retain|keep|maintain)\s+(?:for|at\s+least)\s+(?:[0-9]+)\s+(?:year|month)',
            r'(?:retention|kept)\s+(?:period|duration)\s+(?:of|is)\s+(?:[0-9]+)',
            r'(?:[0-9]+)\s+(?:year|month)s?\s+(?:from|after|following)',
            r'(?:minimum|at\s+least)\s+(?:[0-9]+)\s+(?:year|yr)s?',
            r'(?:indefinitely|permanently)',
            r'(?:5|6|7|10)\s+year'
        ]

        has_retention = False
        for pattern in retention_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Check if in context of records/documents
                for m in matches:
                    context_start = max(0, m.start() - 150)
                    context_end = min(len(text), m.end() + 150)
                    context = text[context_start:context_end].lower()

                    if any(kw in context for kw in ['record', 'document', 'retain', 'keep', 'store', 'file']):
                        has_retention = True
                        spans.append({
                            'type': 'retention_period',
                            'start': m.start(),
                            'end': m.end(),
                            'text': m.group(),
                            'severity': 'none'
                        })

        # Check for specific FCA retention requirements
        fca_retention_patterns = [
            r'(?:5|6)\s+years?\s+(?:from|after|following)\s+(?:the\s+)?(?:transaction|service|advice|relationship)',
            r'mifid\s+(?:retention|record)',
            r'(?:data|document)\s+retention\s+(?:policy|schedule|period)'
        ]

        has_fca_compliant = False
        for pattern in fca_retention_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_fca_compliant = True
                for m in matches:
                    spans.append({
                        'type': 'fca_retention_requirement',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Check for security/access controls
        security_patterns = [
            r'(?:secure|encrypted|protected|confidential)',
            r'access\s+(?:control|restriction|limited)',
            r'(?:gdpr|data\s+protection)\s+compliant',
            r'password[\s-]protected',
            r'backup\s+(?:and\s+)?(?:recovery|restore)'
        ]

        has_security = False
        for pattern in security_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                has_security = True
                for m in matches:
                    spans.append({
                        'type': 'record_security',
                        'start': m.start(),
                        'end': m.end(),
                        'text': m.group(),
                        'severity': 'none'
                    })

        # Determine status
        record_elements = []
        missing_elements = []

        if has_what:
            record_elements.append('what is recorded')
        else:
            missing_elements.append('what records are kept')

        if has_where:
            record_elements.append('where stored')
        else:
            missing_elements.append('where records are stored')

        if has_retention:
            record_elements.append('retention period')
        else:
            missing_elements.append('how long records are retained')

        if has_security:
            record_elements.append('security measures')

        if has_fca_compliant:
            record_elements.append('FCA-compliant retention')

        # Warning: Records mentioned but insufficient detail
        if len(missing_elements) >= 2:
            details = []
            for element in missing_elements:
                details.append(f'Missing: {element}')
            for element in record_elements:
                details.append(f'Present: {element}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Record-keeping mentioned but lacks key details ({len(missing_elements)} missing)',
                'legal_source': self.legal_source,
                'suggestion': f'SYSC 9 requires firms to specify: {", ".join(missing_elements)}. Typical FCA requirement is 5-6 years from end of relationship.',
                'spans': spans,
                'details': details
            }

        # Warning: Some detail missing
        if len(missing_elements) == 1:
            details = []
            for element in missing_elements:
                details.append(f'Missing: {element}')
            for element in record_elements:
                details.append(f'Present: {element}')
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Record-keeping could be more specific',
                'legal_source': self.legal_source,
                'suggestion': f'Add: {", ".join(missing_elements)}',
                'spans': spans,
                'details': details
            }

        # Pass: Good record-keeping detail
        if len(record_elements) >= 3:
            details = []
            for element in record_elements:
                details.append(element)
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Record-keeping requirements well-defined ({len(record_elements)} elements: {", ".join(record_elements)})',
                'legal_source': self.legal_source,
                'spans': spans,
                'details': details
            }

        # Marginal pass
        details = []
        for element in record_elements:
            details.append(element)
        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Basic record-keeping requirements stated ({len(record_elements)} elements)',
            'legal_source': self.legal_source,
            'spans': spans,
            'details': details
        }
