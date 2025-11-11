import re


class GrievanceProcedureACASGate:
    def __init__(self):
        self.name = "grievance_procedure_acas"
        self.severity = "critical"
        self.legal_source = "Employment Act 2002, ACAS Code of Practice on Disciplinary and Grievance Procedures"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['grievance', 'complaint', 'concern', 'procedure', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        grievance_patterns = [
            r'grievance',
            r'raise.*concern',
            r'complaint\s+(?:procedure|process)'
        ]

        has_grievance = any(re.search(p, text, re.IGNORECASE) for p in grievance_patterns)

        if not has_grievance:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No grievance procedure',
                'legal_source': self.legal_source,
                'penalty': 'Up to 25% uplift on tribunal awards for failure to follow ACAS Code',
                'suggestion': 'Must provide grievance procedure per ACAS Code'
            }

        # ACAS Code elements
        acas_elements = {
            'written_statement': r'(?:in\s+)?writing|written\s+(?:statement|grievance)',
            'without_delay': r'(?:without\s+(?:unreasonable\s+)?delay|promptly|timely)',
            'meeting': r'(?:grievance\s+)?meeting|(?:discuss|hear).*grievance',
            'right_to_be_accompanied': r'(?:accompan|bring.*(?:colleague|representative))|right.*(?:accompan|representation)',
            'investigation': r'investigat',
            'decision_communicated': r'(?:decision|outcome).*(?:writing|written|communicated)',
            'reasons_given': r'reason(?:s)?.*(?:decision|outcome)',
            'appeal_right': r'appeal|right.*appeal',
            'timescales': r'(?:within|timescale).*(?:\d+|reasonable).*(?:day|working\s+day)',
            'confidentiality': r'confidential'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in acas_elements.items()}
        score = sum(found_elements.values())

        # Check for informal resolution
        informal_patterns = [
            r'informal(?:ly)?.*(?:resolve|discuss|raise)',
            r'(?:first|initially).*(?:speak|discuss).*(?:manager|supervisor)',
            r'attempt.*(?:informal|resolve).*(?:before|first)'
        ]

        has_informal = any(re.search(p, text, re.IGNORECASE) for p in informal_patterns)

        # Check for multiple stages
        multiple_stages_patterns = [
            r'(?:stage|step)\s+(?:1|one|2|two|3|three)',
            r'(?:first|second|final)\s+(?:stage|step)',
            r'escalat.*(?:senior|higher)'
        ]

        has_multiple_stages = any(re.search(p, text, re.IGNORECASE) for p in multiple_stages_patterns)

        # Check for mediation reference
        mediation_patterns = [
            r'mediat(?:e|ion)',
            r'ACAS.*(?:conciliation|early\s+conciliation)'
        ]

        mentions_mediation = any(re.search(p, text, re.IGNORECASE) for p in mediation_patterns)

        if score >= 7 and has_informal:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive ACAS-compliant grievance procedure ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found_elements.items() if v],
                'has_informal_stage': has_informal
            }

        if score >= 5:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Grievance procedure incomplete ({score}/10 ACAS elements)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found_elements.items() if not v][:5],
                'suggestion': 'ACAS Code requires: written statement, timely meeting, representation right, investigation, written decision with reasons, appeal'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Grievance procedure fails to meet ACAS Code',
            'legal_source': self.legal_source,
            'penalty': 'Up to 25% uplift on tribunal awards',
            'suggestion': 'Implement ACAS-compliant procedure: (1) encourage informal resolution, (2) written grievance, (3) timely meeting, (4) right to be accompanied, (5) investigation, (6) written decision with reasons, (7) appeal right'
        }
