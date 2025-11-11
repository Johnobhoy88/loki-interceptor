import re


class TradeUnionRightsGate:
    def __init__(self):
        self.name = "trade_union_rights"
        self.severity = "critical"
        self.legal_source = "Trade Union and Labour Relations (Consolidation) Act 1992 ss.137-177"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['union', 'trade union', 'representative', 'collective', 'recognition'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        union_patterns = [
            r'trade\s+union',
            r'\bunion\b',
            r'collective\s+(?:bargaining|agreement)',
            r'(?:union\s+)?representative'
        ]

        mentions_union = any(re.search(p, text, re.IGNORECASE) for p in union_patterns)

        if not mentions_union:
            return {'status': 'N/A', 'message': 'No trade union provisions', 'legal_source': self.legal_source}

        # Check for prohibited actions
        prohibited_actions = [
            r'(?:not|cannot|must\s+not).*(?:join|member\s+of).*union',
            r'(?:dismiss|detriment).*(?:union\s+(?:member|activity))',
            r'(?:require|insist).*(?:not\s+join|leave).*union',
            r'blacklist'
        ]

        has_prohibited = any(re.search(p, text, re.IGNORECASE) for p in prohibited_actions)

        if has_prohibited:
            # Check if it's prohibiting the employer from taking action
            protection_patterns = [
                r'(?:employer|company|we).*(?:not|never|shall\s+not).*(?:dismiss|detriment).*union',
                r'(?:protected|right).*(?:join|member).*union'
            ]
            is_protection = any(re.search(p, text, re.IGNORECASE) for p in protection_patterns)

            if not is_protection:
                return {
                    'status': 'FAIL',
                    'severity': 'critical',
                    'message': 'Prohibited restriction on trade union membership/activity',
                    'legal_source': 'TULRCA 1992 s.137, s.146, s.152',
                    'penalty': 'Automatic unfair dismissal; unlimited compensation; injunction',
                    'suggestion': 'Cannot: prevent union membership, dismiss for union activity, subject to detriment for union membership. These are fundamental rights.'
                }

        # Positive union rights
        union_rights = {
            'right_to_join': r'(?:right\s+to\s+join|free\s+to\s+join|entitled\s+to\s+join).*union',
            'no_detriment': r'(?:not|no).*(?:detriment|disadvantage).*(?:union|membership|activity)',
            'time_off_for_duties': r'time\s+off.*(?:union\s+)?(?:duties|activities|representative)',
            'facility_time': r'facility\s+time',
            'recognition': r'recogni[sz]e.*union|collective\s+bargaining',
            'consultation': r'consult.*(?:union|representative).*(?:redundancy|TUPE|change)',
            'check_off': r'check[- ]off|deduct.*union.*(?:subscription|dues)',
            'protection_from_dismissal': r'(?:unfair|automatic).*dismiss.*union',
            'disclosure_of_information': r'disclose.*information.*(?:collective\s+bargaining|union)',
            'industrial_action': r'(?:strike|industrial)\s+action|ballot'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in union_rights.items()}
        score = sum(found.values())

        if score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive trade union provisions ({score}/10 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 3:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Basic trade union provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: time off for union duties, facility time, consultation requirements, protection from detriment'
            }

        if score >= 1:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Limited trade union provisions ({score}/10)',
                'legal_source': self.legal_source,
                'suggestion': 'Add fundamental rights: join union, no detriment, time off for duties, protection from dismissal per TULRCA 1992'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Trade union mentioned without rights specified',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify trade union rights: right to join, time off for duties, no detriment, protection from dismissal, consultation'
        }
