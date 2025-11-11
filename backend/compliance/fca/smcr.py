"""
FCA Senior Managers & Certification Regime (SMCR) Compliance Checker
Implements SMCR requirements for financial services firms

Legal References:
- SYSC 4.7 (Senior Management Arrangements)
- SYSC 26 & 27 (Senior Managers Regime and Certification Regime)
- COCON (Code of Conduct)
- Effective from December 9, 2019 (all firms)
"""

import re
from typing import Dict, List


class SMCRComplianceChecker:
    """
    Validates SMCR compliance in documents
    Checks for accountability, conduct rules, and responsibilities
    """

    def __init__(self):
        self.name = "smcr_compliance"
        self.legal_source = "FCA SYSC 26 & 27 (SMCR)"

    # Senior Manager Functions (SMFs)
    SMF_FUNCTIONS = {
        'SMF1': 'Chief Executive',
        'SMF2': 'Chief Finance Officer',
        'SMF3': 'Executive Director',
        'SMF4': 'Chief Risk Officer',
        'SMF5': 'Head of Internal Audit',
        'SMF9': 'Chair',
        'SMF10': 'Chair of Risk Committee',
        'SMF11': 'Chair of Audit Committee',
        'SMF12': 'Chair of Remuneration Committee',
        'SMF13': 'Chair of Nomination Committee',
        'SMF14': 'Senior Independent Director',
        'SMF16': 'Compliance Oversight',
        'SMF17': 'Money Laundering Reporting Officer',
        'SMF18': 'Other Overall Responsibility',
        'SMF24': 'Chief Operations Officer'
    }

    def check_smcr_compliance(self, text: str, document_type: str = None) -> Dict:
        """Main SMCR compliance check"""
        text_lower = text.lower()

        # Determine if document is SMCR-relevant
        if not self._is_smcr_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not SMCR-relevant document',
                'legal_source': self.legal_source
            }

        results = {
            'accountability': self.check_accountability(text),
            'conduct_rules': self.check_conduct_rules(text),
            'responsibilities_map': self.check_responsibilities_map(text),
            'sm_function': self.check_senior_manager_functions(text),
            'certification': self.check_certification_regime(text),
            'fit_and_proper': self.check_fit_and_proper(text)
        }

        failures = [k for k, v in results.items() if v['status'] == 'FAIL']
        warnings = [k for k, v in results.items() if v['status'] == 'WARNING']

        overall_status = 'PASS'
        overall_severity = 'none'

        if failures:
            overall_status = 'FAIL'
            overall_severity = 'critical'
        elif warnings:
            overall_status = 'WARNING'
            overall_severity = 'medium'

        return {
            'status': overall_status,
            'severity': overall_severity,
            'message': f'SMCR: {len(failures)} failures, {len(warnings)} warnings',
            'legal_source': self.legal_source,
            'checks': results,
            'failures': failures,
            'warnings': warnings
        }

    def _is_smcr_relevant(self, text: str) -> bool:
        """Determine if document is SMCR-relevant"""
        smcr_terms = [
            r'\bsmcr\b',
            r'senior\s+manager(?:s)?(?:\s+regime)?',
            r'certification\s+regime',
            r'\bsmf\d+\b',
            r'conduct\s+rule',
            r'(?:statement|map)\s+of\s+responsibilit',
            r'fit\s+and\s+proper',
            r'accountability\s+regime',
            r'prescribed\s+responsibilit'
        ]

        return any(re.search(term, text, re.IGNORECASE) for term in smcr_terms)

    def check_accountability(self, text: str) -> Dict:
        """
        Check for clear accountability statements
        SMCR Principle: Clear allocation of responsibility
        """
        accountability_patterns = [
            r'(?:responsible|accountability)\s+for',
            r'(?:owned|accountable)\s+by',
            r'ultimate\s+responsibilit',
            r'clearly\s+(?:defined|allocated|assigned)',
            r'reporting\s+(?:line|to|structure)',
            r'escalation\s+(?:process|route|path)'
        ]

        accountability_count = sum(1 for p in accountability_patterns if re.search(p, text, re.IGNORECASE))

        # Red flags - lack of accountability
        red_flags = [
            r'no\s+(?:one|person)\s+responsible',
            r'shared\s+responsibilit(?:y|ies)(?!\s+clearly)',
            r'unclear.*responsibilit',
            r'(?:may|might)\s+be\s+responsible',
            r'collective(?:ly)?\s+responsible(?!\s+(?:but|and).*individual)'
        ]

        has_red_flags = any(re.search(p, text, re.IGNORECASE) for p in red_flags)

        if has_red_flags:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Lack of clear accountability',
                'legal_source': 'SYSC 26 (Senior Managers Regime)',
                'suggestion': 'SMCR requires clear individual accountability. Each responsibility must be owned by a named Senior Manager.'
            }

        if accountability_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Accountability statements could be clearer',
                'legal_source': 'SYSC 26',
                'suggestion': 'Strengthen accountability: clearly state who is responsible, reporting lines, and escalation'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Clear accountability ({accountability_count} indicators)',
            'legal_source': 'SYSC 26'
        }

    def check_conduct_rules(self, text: str) -> Dict:
        """
        Check for conduct rules references
        COCON: Individual and Senior Manager Conduct Rules
        """
        # Individual Conduct Rules
        individual_rules = {
            'Rule 1': r'(?:act\s+with\s+)?integrity',
            'Rule 2': r'due\s+(?:skill|care|diligence)',
            'Rule 3': r'(?:open|cooperative).*(?:regulator|fca)',
            'Rule 4': r'(?:pay\s+due\s+regard|customer.*best\s+interest)',
            'Rule 5': r'market\s+(?:conduct|integrity|abuse)'
        }

        # Senior Manager Conduct Rules (additional)
        sm_rules = {
            'SM Rule 1': r'take\s+reasonable\s+steps',
            'SM Rule 2': r'delegate\s+appropriately',
            'SM Rule 3': r'appropriate\s+(?:oversight|control|governance)',
            'SM Rule 4': r'(?:disclose|inform).*(?:appropriately|fca)'
        }

        found_individual_rules = []
        found_sm_rules = []

        for rule_id, pattern in individual_rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_individual_rules.append(rule_id)

        for rule_id, pattern in sm_rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_sm_rules.append(rule_id)

        # Check for explicit COCON references
        has_cocon_ref = bool(re.search(r'\bcocon\b|conduct\s+rule', text, re.IGNORECASE))

        total_rules = len(found_individual_rules) + len(found_sm_rules)

        if total_rules == 0 and not has_cocon_ref:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No conduct rules referenced',
                'legal_source': 'COCON (Code of Conduct)',
                'suggestion': 'Reference COCON conduct rules: integrity, due care, cooperation with regulator, customer interest'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Conduct rules referenced ({total_rules} rules)',
            'legal_source': 'COCON',
            'details': {
                'individual_rules': found_individual_rules,
                'sm_rules': found_sm_rules
            }
        }

    def check_responsibilities_map(self, text: str) -> Dict:
        """
        Check for Responsibilities Map
        Required for Core firms and Enhanced firms
        """
        responsibilities_map_patterns = [
            r'responsibilit(?:y|ies)\s+map',
            r'management\s+responsibilities\s+map',
            r'\bmrm\b',
            r'statement\s+of\s+responsibilit',
            r'\bsor\b'
        ]

        has_responsibilities_map = any(re.search(p, text, re.IGNORECASE) for p in responsibilities_map_patterns)

        if not has_responsibilities_map:
            # Check if document discusses senior management structure
            discusses_structure = bool(re.search(r'senior\s+(?:management|manager|leadership)|org(?:anisation|anization)al\s+structure', text, re.IGNORECASE))

            if discusses_structure:
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': 'Senior management structure discussed but no Responsibilities Map',
                    'legal_source': 'SYSC 26.7 (Responsibilities Map)',
                    'suggestion': 'Core and Enhanced firms must maintain Management Responsibilities Map (MRM) or Statement of Responsibilities (SOR)'
                }

            return {
                'status': 'N/A',
                'message': 'Responsibilities Map not applicable to this document',
                'legal_source': 'SYSC 26.7'
            }

        # Check for key elements of responsibilities map
        map_elements = [
            r'reporting\s+line',
            r'prescribed\s+responsibilit',
            r'(?:senior\s+manager|smf)\s+function',
            r'key\s+(?:function|role|responsibility)',
            r'delegation'
        ]

        element_count = sum(1 for p in map_elements if re.search(p, text, re.IGNORECASE))

        if element_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Responsibilities Map mentioned but lacks detail',
                'legal_source': 'SYSC 26.7',
                'suggestion': 'Responsibilities Map must show: reporting lines, prescribed responsibilities, delegations, key functions'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Responsibilities Map present ({element_count} elements)',
            'legal_source': 'SYSC 26.7'
        }

    def check_senior_manager_functions(self, text: str) -> Dict:
        """Check for Senior Manager Functions (SMF) references"""
        # Look for SMF designations
        smf_matches = re.findall(r'\bsmf\s*(\d+)\b', text, re.IGNORECASE)

        found_smfs = {}
        for smf_num in smf_matches:
            smf_key = f'SMF{smf_num}'
            if smf_key in self.SMF_FUNCTIONS:
                found_smfs[smf_key] = self.SMF_FUNCTIONS[smf_key]

        if not found_smfs:
            # Check for role names
            for smf_key, role_name in self.SMF_FUNCTIONS.items():
                if re.search(role_name.replace(' ', r'\s+'), text, re.IGNORECASE):
                    found_smfs[smf_key] = role_name

        if found_smfs:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Senior Manager Functions referenced ({len(found_smfs)} functions)',
                'legal_source': 'SYSC 26',
                'functions': found_smfs
            }

        return {
            'status': 'N/A',
            'message': 'No specific SMF functions mentioned',
            'legal_source': 'SYSC 26'
        }

    def check_certification_regime(self, text: str) -> Dict:
        """
        Check Certification Regime references
        Applies to staff performing significant harm functions
        """
        certification_patterns = [
            r'certification\s+(?:regime|function|staff)',
            r'certified\s+(?:person|staff|individual)',
            r'significant\s+harm\s+function',
            r'annual\s+certification',
            r'fit\s+and\s+proper.*certif'
        ]

        has_certification = any(re.search(p, text, re.IGNORECASE) for p in certification_patterns)

        if not has_certification:
            return {
                'status': 'N/A',
                'message': 'Certification regime not applicable',
                'legal_source': 'SYSC 27'
            }

        # Check for key certification elements
        certification_elements = [
            r'annual(?:ly)?\s+(?:certif|assess)',
            r'fit\s+and\s+proper',
            r'regulatory\s+reference',
            r'training\s+(?:and|&)\s+competence',
            r'conduct\s+rule'
        ]

        element_count = sum(1 for p in certification_elements if re.search(p, text, re.IGNORECASE))

        if element_count < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Certification regime mentioned but lacks key elements',
                'legal_source': 'SYSC 27',
                'suggestion': 'Certification requires: annual assessment, fit and proper assessment, regulatory references, conduct rules'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Certification regime elements present ({element_count} elements)',
            'legal_source': 'SYSC 27'
        }

    def check_fit_and_proper(self, text: str) -> Dict:
        """Check fit and proper assessments"""
        fit_and_proper_patterns = [
            r'fit\s+and\s+proper',
            r'honesty\s*,?\s+integrity\s+and\s+reputation',
            r'competence\s+and\s+capability',
            r'financial\s+soundness',
            r'criminal\s+(?:record|conviction|history)',
            r'regulatory\s+(?:reference|history)',
            r'fitness\s+assessment'
        ]

        element_count = sum(1 for p in fit_and_proper_patterns if re.search(p, text, re.IGNORECASE))

        if element_count == 0:
            return {
                'status': 'N/A',
                'message': 'Fit and proper assessment not applicable',
                'legal_source': 'FIT (Fit and Proper)'
            }

        # Check for comprehensive assessment
        assessment_components = {
            'honesty': r'honesty|integrity|reputation',
            'competence': r'competence|capability|skill|qualification',
            'financial': r'financial\s+soundness|bankruptcy|insolvency',
            'references': r'(?:regulatory|employment)\s+reference'
        }

        found_components = []
        for component, pattern in assessment_components.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_components.append(component)

        if len(found_components) < 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Fit and proper assessment incomplete',
                'legal_source': 'FIT 2.1',
                'suggestion': 'Assess: honesty/integrity, competence/capability, financial soundness, regulatory references',
                'found': found_components
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': f'Fit and proper assessment comprehensive ({len(found_components)} components)',
            'legal_source': 'FIT 2.1',
            'components': found_components
        }

    def check_prescribed_responsibilities(self, text: str) -> Dict:
        """
        Check for Prescribed Responsibilities (PRs)
        30 core prescribed responsibilities under SMCR
        """
        pr_patterns = {
            'PR1': r'compliance.*fca\s+(?:rule|requirement)',
            'PR2': r'embed.*culture',
            'PR3': r'induction.*training.*smcr',
            'PR4': r'whistle?blow(?:ing|er)',
            'PR5': r'data\s+(?:security|integrity)',
            'PR6': r'client\s+(?:asset|money)',
            'PR7': r'operational\s+resilience'
        }

        found_prs = []
        for pr_id, pattern in pr_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_prs.append(pr_id)

        if found_prs:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Prescribed Responsibilities referenced ({len(found_prs)} PRs)',
                'legal_source': 'SYSC 26.3',
                'prescribed_responsibilities': found_prs
            }

        return {
            'status': 'N/A',
            'message': 'No specific Prescribed Responsibilities mentioned',
            'legal_source': 'SYSC 26.3'
        }
