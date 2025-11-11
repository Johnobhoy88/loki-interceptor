import re


class BereavementLeaveGate:
    def __init__(self):
        self.name = "bereavement_leave"
        self.severity = "medium"
        self.legal_source = "Parental Bereavement Leave Regulations 2020, Employment Rights Act 1996"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['bereavement', 'bereave', 'death', 'funeral', 'compassionate'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        bereavement_patterns = [
            r'bereavement\s+leave',
            r'compassionate\s+leave',
            r'(?:leave|time\s+off).*(?:death|funeral|bereave)'
        ]

        has_bereavement = any(re.search(p, text, re.IGNORECASE) for p in bereavement_patterns)

        if not has_bereavement:
            return {'status': 'N/A', 'message': 'No bereavement leave provisions', 'legal_source': self.legal_source}

        # Check for statutory parental bereavement leave
        parental_bereavement_elements = {
            'two_weeks_child': r'(?:two|2)\s+weeks?.*(?:child|under\s+18)',
            'under_18': r'(?:child|under)\s+(?:18|eighteen)',
            'notification': r'(?:notice|notify).*(?:bereave|death)',
            'day_one_right': r'(?:day\s+one|from\s+(?:start|commencement))|(?:all\s+employees)',
            'paid_or_unpaid': r'(?:paid|unpaid|statutory.*pay)',
            '56_weeks': r'56\s+weeks?.*(?:from|after|following).*(?:death|stillbirth)'
        }

        found_parental = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in parental_bereavement_elements.items()}
        parental_score = sum(found_parental.values())

        # General bereavement provisions
        general_elements = {
            'family_members_covered': r'(?:parent|sibling|grandparent|spouse|partner|child)',
            'flexible_timing': r'(?:flexible|arrange|timing).*(?:leave|time\s+off)',
            'funeral_attendance': r'funeral|memorial\s+service',
            'compassionate': r'compassionate',
            'reasonable_time': r'reasonable\s+(?:time|period|amount)',
            'support_offered': r'(?:support|counselling|EAP|employee\s+assistance)',
            'protection_from_detriment': r'(?:not|no).*detriment.*bereave'
        }

        found_general = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in general_elements.items()}
        general_score = sum(found_general.values())

        total_score = parental_score + general_score

        if parental_score >= 3:
            if total_score >= 8:
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': f'Comprehensive bereavement leave policy ({parental_score}/6 parental, {general_score}/7 general)',
                    'legal_source': self.legal_source,
                    'elements_found': list(found_parental.keys()) + [k for k, v in found_general.items() if v]
                }

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Parental bereavement leave covered ({parental_score}/6)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider expanding to cover: other family members, funeral attendance, support services'
            }

        if general_score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'General bereavement provisions but missing statutory parental bereavement ({general_score}/7 general)',
                'legal_source': self.legal_source,
                'suggestion': 'Add statutory parental bereavement leave per 2020 Regulations: 2 weeks for death of child under 18, day one right, within 56 weeks of death, notification requirements'
            }

        if general_score >= 2:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Basic bereavement provisions ({general_score}/7)',
                'legal_source': self.legal_source,
                'suggestion': 'Strengthen policy: add parental bereavement leave (2 weeks), family members covered, reasonable time, funeral attendance, support services, protection from detriment'
            }

        return {
            'status': 'WARNING',
            'severity': 'medium',
            'message': 'Bereavement leave lacks detail',
            'legal_source': self.legal_source,
            'suggestion': 'Implement comprehensive policy including: (1) Statutory parental bereavement leave (2 weeks for child under 18, day one right), (2) compassionate leave for other family deaths, (3) funeral attendance, (4) support services'
        }
