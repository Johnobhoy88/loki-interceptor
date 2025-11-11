import re


class RestrictiveCovenantsGate:
    def __init__(self):
        self.name = "restrictive_covenants"
        self.severity = "high"
        self.legal_source = "Restraint of Trade doctrine, Nordenfelt v Maxim [1894], TFS Derivatives v Morgan [2004]"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['employment', 'contract', 'agreement', 'nda'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for restrictive covenants
        covenant_types = {
            'non_compete': [
                r'not\s+(?:engage|work|be\s+employed).*compet(?:ing|itor)',
                r'shall\s+not.*(?:compete|competition)',
                r'restrict(?:ed|ion).*(?:similar\s+business|competing)'
            ],
            'non_solicitation_clients': [
                r'not.*solicit.*(?:client|customer)',
                r'shall\s+not.*(?:approach|contact).*customer'
            ],
            'non_solicitation_employees': [
                r'not.*(?:solicit|entice|induce).*employee',
                r'shall\s+not.*employ.*(?:former|current).*employee'
            ],
            'non_dealing': [
                r'not.*deal.*with.*customer',
                r'cease.*business.*with.*client'
            ]
        }

        found_covenants = {}
        issues = []

        for covenant_type, patterns in covenant_types.items():
            found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
            found_covenants[covenant_type] = found

        if not any(found_covenants.values()):
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'No restrictive covenants detected',
                'legal_source': self.legal_source
            }

        # If restrictive covenants present, check reasonableness factors

        # 1. Geographic scope
        geographic_patterns = [
            r'within\s+(?:the\s+)?(?:united\s+kingdom|UK|England|Scotland|Wales)',
            r'within\s+\d+\s+(?:mile|kilometre|km)',
            r'in\s+the\s+(?:territory|area|region)',
            r'worldwide|global(?:ly)?'
        ]
        has_geographic = any(re.search(p, text, re.IGNORECASE) for p in geographic_patterns)

        # Check for worldwide restriction (usually unreasonable)
        has_worldwide = re.search(r'worldwide|global(?:ly)?', text, re.IGNORECASE)
        if has_worldwide:
            issues.append('worldwide_scope')

        # 2. Time limitation
        time_patterns = [
            r'(?:for|period\s+of)\s+(\d+)\s+(?:month|year)',
            r'(\d+)\s+(?:month|year).*(?:after|following)',
            r'duration.*(\d+)'
        ]
        time_matches = [re.search(p, text, re.IGNORECASE) for p in time_patterns]
        time_durations = [int(m.group(1)) for m in time_matches if m]

        if time_durations:
            max_duration = max(time_durations)
            # Check if duration mentions months or years
            if re.search(r'\b' + str(max_duration) + r'\s+year', text, re.IGNORECASE):
                if max_duration > 2:
                    issues.append('excessive_duration_years')
            elif re.search(r'\b' + str(max_duration) + r'\s+month', text, re.IGNORECASE):
                if max_duration > 12:
                    issues.append('excessive_duration_months')
        else:
            issues.append('no_time_limit')

        # 3. Check for legitimate business interest justification
        legitimate_interest_patterns = [
            r'protect.*(?:legitimate|proprietary)\s+(?:business\s+)?interest',
            r'confidential\s+information',
            r'trade\s+secret',
            r'customer\s+(?:relationship|connection)',
            r'goodwill'
        ]
        has_legitimate_interest = any(re.search(p, text, re.IGNORECASE) for p in legitimate_interest_patterns)

        if not has_legitimate_interest:
            issues.append('no_legitimate_interest')

        # 4. Check for consideration
        consideration_patterns = [
            r'in\s+consideration\s+of',
            r'payment\s+of',
            r'salary',
            r'compensation'
        ]
        has_consideration = any(re.search(p, text, re.IGNORECASE) for p in consideration_patterns)

        if not has_consideration:
            issues.append('no_consideration')

        # Determine severity based on issues
        if len(issues) >= 3:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': f'Restrictive covenants likely unenforceable ({len(issues)} reasonableness issues)',
                'legal_source': self.legal_source,
                'covenants_found': [k for k, v in found_covenants.items() if v],
                'issues': issues,
                'suggestion': 'Restrictive covenants must be: (1) no wider than necessary, (2) protect legitimate business interest, (3) reasonable in scope and duration, (4) supported by consideration',
                'penalty': 'Void and unenforceable; potential restraint of trade'
            }

        if len(issues) >= 1:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Restrictive covenants may have enforceability issues',
                'legal_source': self.legal_source,
                'covenants_found': [k for k, v in found_covenants.items() if v],
                'issues': issues,
                'suggestion': 'Review restrictions for reasonableness: geographic scope, duration, legitimate business interest'
            }

        return {
            'status': 'PASS',
            'severity': 'none',
            'message': 'Restrictive covenants appear reasonable',
            'legal_source': self.legal_source,
            'covenants_found': [k for k, v in found_covenants.items() if v]
        }
