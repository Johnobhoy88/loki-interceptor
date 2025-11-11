import re


class ContractVariationsGate:
    def __init__(self):
        self.name = "contract_variations"
        self.severity = "high"
        self.legal_source = "Contract Law, Rigby v Ferodo [1988]"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['vary', 'change', 'amend', 'modify', 'alter', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        variation_patterns = [
            r'var(?:y|iation)',
            r'(?:change|amend|modify|alter).*(?:term|condition|contract)',
            r'(?:revise|update).*(?:term|contract)'
        ]

        has_variation = any(re.search(p, text, re.IGNORECASE) for p in variation_patterns)

        if not has_variation:
            return {'status': 'N/A', 'message': 'No variation provisions', 'legal_source': self.legal_source}

        # Check for unilateral variation clause
        unilateral_patterns = [
            r'(?:employer|company|we).*(?:may|reserve.*right).*(?:vary|change|amend).*(?:term|condition)',
            r'(?:at\s+(?:our\s+)?discretion|right\s+to).*(?:vary|change|amend)',
            r'(?:may|can).*(?:vary|change).*without.*(?:consent|agreement)'
        ]

        has_unilateral = any(re.search(p, text, re.IGNORECASE) for p in unilateral_patterns)

        if has_unilateral:
            # Check if it's limited to minor/administrative changes
            limited_patterns = [
                r'(?:minor|administrative|non-material)',
                r'(?:policy|procedure).*(?:not|without).*(?:term|condition)',
                r'does\s+not\s+affect.*(?:remuneration|core\s+term)'
            ]

            is_limited = any(re.search(p, text, re.IGNORECASE) for p in limited_patterns)

            if not is_limited:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Broad unilateral variation clause detected',
                    'legal_source': 'Rigby v Ferodo [1988] ICR 29',
                    'penalty': 'Clause may be void; unilateral changes can be breach of contract/constructive dismissal',
                    'suggestion': 'Remove unilateral variation clause or limit to: (1) minor/administrative changes, (2) policies/procedures (not contractual terms), (3) changes required by law'
                }

        # Check for mutual consent requirement
        consent_patterns = [
            r'(?:mutual|both\s+parties).*(?:agree|consent)',
            r'(?:with|subject\s+to).*(?:employee.*agreement|written\s+consent)',
            r'only.*(?:with|by).*(?:agreement|consent)'
        ]

        requires_consent = any(re.search(p, text, re.IGNORECASE) for p in consent_patterns)

        # Check for consultation requirement
        consultation_patterns = [
            r'consult.*(?:before|prior\s+to)',
            r'discuss.*(?:propose|intend)',
            r'(?:reasonable\s+)?notice.*(?:variation|change)'
        ]

        requires_consultation = any(re.search(p, text, re.IGNORECASE) for p in consultation_patterns)

        # Check for specific variation scenarios
        scenarios = {
            'job_duties': r'(?:duties|responsibilities).*(?:may\s+vary|change)',
            'location': r'(?:place|location).*work.*(?:may\s+change|vary|transfer)',
            'hours': r'(?:working\s+)?hours?.*(?:may\s+(?:be\s+)?vary|change)',
            'policies': r'(?:policy|policies|procedure).*(?:may\s+(?:be\s+)?(?:change|amend|update))',
            'benefits': r'benefit(?:s)?.*(?:may\s+(?:be\s+)?(?:vary|change|withdraw))'
        }

        found_scenarios = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in scenarios.items()}

        if requires_consent or (requires_consultation and not has_unilateral):
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Variation requires consent/consultation',
                'legal_source': self.legal_source,
                'requires_consent': requires_consent,
                'requires_consultation': requires_consultation
            }

        if has_unilateral and is_limited:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Limited unilateral variation (minor/administrative only)',
                'legal_source': self.legal_source,
                'note': 'Ensure variations are genuinely minor and do not affect core terms'
            }

        scenario_count = sum(found_scenarios.values())
        if scenario_count >= 3 and not requires_consent:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Multiple variation scenarios ({scenario_count}) without consent requirement',
                'legal_source': self.legal_source,
                'scenarios': [k for k, v in found_scenarios.items() if v],
                'suggestion': 'Add: "Any variation to terms of employment requires mutual written agreement" or "Employer will consult before material changes"'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Variation provisions unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify: variations require mutual consent, or employer will consult, or unilateral right limited to minor/administrative changes only'
        }
