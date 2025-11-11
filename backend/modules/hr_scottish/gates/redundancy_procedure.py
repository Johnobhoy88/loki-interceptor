import re


class RedundancyProcedureGate:
    def __init__(self):
        self.name = "redundancy_procedure"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 ss.135-181, Trade Union and Labour Relations (Consolidation) Act 1992 s.188"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['redundan', 'restructur', 'reorgnis', 'reorganiz', 'consultation'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        redundancy_patterns = [
            r'redundan(?:cy|t)',
            r'restructur',
            r're[- ]?organi[sz]',
            r'reduction.*workforce'
        ]

        has_redundancy = any(re.search(p, text, re.IGNORECASE) for p in redundancy_patterns)

        if not has_redundancy:
            return {'status': 'N/A', 'message': 'No redundancy provisions', 'legal_source': self.legal_source}

        elements = {
            'genuine_redundancy': r'genuine.*redundan|business\s+need',
            'selection_criteria': r'selection\s+(?:criteria|method|matrix)',
            'objective_fair': r'(?:objective|fair|non[- ]discriminatory)',
            'consultation_individual': r'consult(?:ation)?.*(?:individual|employee)',
            'consultation_collective': r'collective\s+consultation|(?:45|30)\s+days?',
            'alternative_employment': r'alternative\s+(?:employment|role|position|vacancy)',
            'trial_period': r'trial\s+period|four\s+weeks?',
            'redundancy_pay': r'redundancy\s+pay(?:ment)?|statutory\s+redundancy',
            'notice_period': r'notice\s+period',
            'appeal_right': r'appeal|right\s+to\s+appeal',
            'time_off_job_search': r'time\s+off.*(?:job|interview|search)',
            'volunteers': r'volunteer(?:s)?|(?:call|ask)\s+for'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        # Check for discriminatory selection criteria
        discriminatory_patterns = [
            r'(?:last\s+in|LIFO).*first\s+out',
            r'part[- ]time.*(?:first|before\s+full)',
            r'(?:pregnant|maternity).*(?:first|select)'
        ]

        has_discriminatory = any(re.search(p, text, re.IGNORECASE) for p in discriminatory_patterns)

        if has_discriminatory:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Potentially discriminatory redundancy selection criteria detected',
                'legal_source': 'Equality Act 2010, Williams v Compair Maxam',
                'penalty': 'Unfair dismissal; indirect discrimination (unlimited compensation)',
                'suggestion': 'Remove: LIFO (age discrimination), part-time first (sex discrimination), pregnancy/maternity considerations'
            }

        if score >= 8:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive redundancy procedure ({score}/12 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 5:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Redundancy procedure incomplete ({score}/12)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:5],
                'suggestion': 'Add: objective selection criteria, consultation, alternative employment, redundancy pay, appeal rights'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate redundancy procedure',
            'legal_source': self.legal_source,
            'penalty': 'Unfair dismissal claims; protective awards (up to 90 days pay) for collective consultation failures',
            'suggestion': 'Must include: genuine redundancy, objective selection, consultation (individual + collective if 20+), alternative employment, statutory redundancy pay, appeal'
        }
