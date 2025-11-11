import re


class AuditRightsGate:
    def __init__(self):
        self.name = "audit_rights"
        self.severity = "low"
        self.legal_source = "Contract Law"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        # Mainly relevant for business NDAs, particularly with ongoing relationships
        return any(kw in text_lower for kw in ['nda', 'non-disclosure', 'confidential', 'agreement'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for audit/inspection rights
        audit_patterns = [
            r'audit(?:s)?|inspect(?:ion)?',
            r'examine.*(?:record|book|document)',
            r'access\s+to.*(?:record|book|premise)',
            r'right\s+to\s+(?:audit|inspect|verify)'
        ]

        has_audit_rights = any(re.search(p, text, re.IGNORECASE) for p in audit_patterns)

        if not has_audit_rights:
            return {
                'status': 'N/A',
                'message': 'No audit rights provisions',
                'legal_source': self.legal_source,
                'note': 'Audit rights useful for verifying confidentiality compliance in business NDAs'
            }

        # Check for notice requirement
        notice_patterns = [
            r'(?:upon|with)\s+(?:\d+\s+(?:days?|business\s+days?))?\s*notice',
            r'reasonable\s+(?:advance\s+)?notice',
            r'prior\s+notice'
        ]

        has_notice = any(re.search(p, text, re.IGNORECASE) for p in notice_patterns)

        # Check for frequency limitation
        frequency_patterns = [
            r'(?:not\s+more\s+than|no\s+more\s+than|maximum\s+of)\s+(\d+)\s+(?:time|audit).*(?:year|12\s+month)',
            r'once\s+(?:per|a)\s+year',
            r'annual(?:ly)?.*audit'
        ]

        has_frequency_limit = any(re.search(p, text, re.IGNORECASE) for p in frequency_patterns)

        # Check for scope definition
        scope_patterns = [
            r'(?:record|document|book|system).*relating\s+to',
            r'relevant\s+(?:to|for).*(?:agreement|confidential)',
            r'reasonably\s+(?:required|necessary)'
        ]

        has_scope = any(re.search(p, text, re.IGNORECASE) for p in scope_patterns)

        # Check for costs allocation
        cost_patterns = [
            r'cost.*(?:audit|inspection).*(?:borne|paid)',
            r'(?:at|expense\s+of)',
            r'bear.*(?:own|their)\s+cost'
        ]

        addresses_costs = any(re.search(p, text, re.IGNORECASE) for p in cost_patterns)

        # Check for confidentiality of audit findings
        confidential_findings_patterns = [
            r'(?:finding|result).*audit.*confidential',
            r'not\s+disclose.*(?:audit|inspection)'
        ]

        protects_findings = any(re.search(p, text, re.IGNORECASE) for p in confidential_findings_patterns)

        # Check for business hours/reasonable times
        timing_patterns = [
            r'(?:business|normal\s+working)\s+hours?',
            r'reasonable\s+times?',
            r'during.*hours?\s+of\s+(?:business|operation)'
        ]

        has_timing = any(re.search(p, text, re.IGNORECASE) for p in timing_patterns)

        elements_present = sum([
            has_notice,
            has_frequency_limit,
            has_scope,
            addresses_costs,
            protects_findings,
            has_timing
        ])

        if elements_present >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive audit rights ({elements_present}/6 elements)',
                'legal_source': self.legal_source,
                'elements': {
                    'notice': has_notice,
                    'frequency_limit': has_frequency_limit,
                    'scope': has_scope,
                    'costs': addresses_costs,
                    'confidentiality': protects_findings,
                    'timing': has_timing
                }
            }

        if elements_present >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic audit rights provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: frequency limits, cost allocation, timing restrictions'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Audit rights mentioned but lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Specify: notice period, frequency limits, scope, costs, timing'
        }
