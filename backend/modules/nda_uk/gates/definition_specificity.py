import re


class DefinitionSpecificityGate:
    def __init__(self):
        self.name = "definition_specificity"
        self.severity = "critical"
        self.legal_source = "Common Law - Restraint of Trade doctrine"
    
    def _is_relevant(self, text):
        return 'confidential' in (text or '').lower()
    
    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable - document is not a non-disclosure agreement',
                'legal_source': self.legal_source
            }
        
        # Check for definition
        has_definition = bool(re.search(r'"?confidential information"?.*(?:means|shall mean|includes)', text, re.IGNORECASE))
        
        if not has_definition:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No clear definition of Confidential Information',
                'legal_source': self.legal_source,
                'suggestion': 'Define: "Confidential Information means [specific categories] but excludes [standard exclusions]"'
            }
        
        # Check for overbroad definition - extended patterns
        overbroad_patterns = [
            r'all information.*of any kind',
            r'any and all.*information',
            r'information.*in whatever form.*concerning.*business',
            r'any.*information.*(?:relating to|about|concerning).*business',
            r'all\s+(?:matters|things|data).*(?:relating|connected)',
            r'everything.*(?:related|connected).*to',
            r'information.*of\s+(?:any|whatever)\s+(?:nature|kind|type)',
            r'all.*(?:knowledge|data).*in.*possession'
        ]

        issues = []
        spans = []
        for pattern in overbroad_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                spans.append({
                    'type': 'overbroad_definition',
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(),
                    'severity': 'critical'
                })
                issues.append(f"Overbroad term: '{match.group()}'")

        # Check for missing exclusions (things that shouldn't be confidential)
        has_exclusions = bool(re.search(r'(?:does not|shall not|excludes?).*(?:include|apply to|cover)', text, re.IGNORECASE))
        public_domain_exclusion = bool(re.search(r'(?:public|publicly available|in the public domain)', text, re.IGNORECASE))

        if not has_exclusions:
            issues.append("No exclusions defined (should exclude public domain, prior knowledge, etc.)")
        if not public_domain_exclusion:
            issues.append("No public domain exclusion")

        # Check for specific categories
        has_categories = bool(re.search(r'(?:including|such as|but not limited to|specifically).*(?:,|;|:)', text, re.IGNORECASE))
        category_examples = ['trade secret', 'financial', 'technical', 'customer', 'business plan', 'strategy', 'pricing']
        categories_found = sum(1 for cat in category_examples if cat in text.lower())

        if not has_categories and categories_found < 2:
            issues.append("No specific categories or examples provided")

        if spans:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Definition is dangerously overbroad ({len(spans)} issues)',
                'spans': spans,
                'details': issues,
                'legal_source': self.legal_source,
                'suggestion': 'Define specific categories (e.g., "trade secrets, financial data, customer lists, technical specifications") AND exclude information that is: (1) Public domain, (2) Already known, (3) Independently developed, (4) Required by law to disclose'
            }

        if len(issues) >= 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Definition could be more specific ({len(issues)} issues)',
                'details': issues,
                'suggestion': 'Add: (1) Specific categories of confidential information, (2) Clear exclusions for public/known information'
            }

        if has_categories and has_exclusions:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Confidential Information specifically defined with appropriate exclusions',
                'legal_source': self.legal_source
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Definition lacks specific categories or exclusions',
            'suggestion': 'List specific types of information AND standard exclusions'
        }
