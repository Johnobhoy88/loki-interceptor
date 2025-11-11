import re


class DisputeResolutionGate:
    def __init__(self):
        self.name = "dispute_resolution"
        self.severity = "low"
        self.legal_source = "Civil Procedure Rules, ADR principles"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['agreement', 'contract'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {
                'status': 'N/A',
                'message': 'Not applicable',
                'legal_source': self.legal_source
            }

        # Check for dispute resolution mechanisms
        dr_mechanisms = {
            'negotiation': r'negotiat(?:e|ion)',
            'mediation': r'mediat(?:e|ion)',
            'arbitration': r'arbitrat(?:e|ion)',
            'expert_determination': r'expert\s+determination',
            'adjudication': r'adjudicat(?:ion|or)',
            'litigation': r'court(?:s)?|litigat(?:ion|e)'
        }

        found_mechanisms = []
        for mechanism, pattern in dr_mechanisms.items():
            if re.search(pattern, text, re.IGNORECASE):
                found_mechanisms.append(mechanism)

        if not found_mechanisms:
            return {
                'status': 'WARNING',
                'severity': 'low',
                'message': 'No dispute resolution provisions',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding dispute resolution mechanism (mediation, arbitration, or litigation)',
                'note': 'Courts encourage ADR per Halsey v Milton Keynes [2004]'
            }

        # Check for escalation procedure
        escalation_patterns = [
            r'first.*(?:attempt|seek).*(?:negotiate|resolve)',
            r'good\s+faith.*(?:negotiate|resolve)',
            r'(?:before|prior\s+to).*(?:mediation|arbitration|court)',
            r'escalat(?:e|ion).*dispute'
        ]

        has_escalation = any(re.search(p, text, re.IGNORECASE) for p in escalation_patterns)

        # Check for timeframes
        timeframe_patterns = [
            r'within\s+\d+\s+(?:day|business\s+day|working\s+day)',
            r'\d+\s+days?.*(?:notice|attempt|dispute)',
            r'period\s+of\s+\d+'
        ]

        has_timeframes = any(re.search(p, text, re.IGNORECASE) for p in timeframe_patterns)

        # Check for costs provisions
        costs_patterns = [
            r'cost(?:s)?.*(?:dispute|mediation|arbitration)',
            r'(?:bear|pay).*(?:own|their)\s+costs',
            r'(?:split|share).*costs',
            r'loser\s+pays'
        ]

        has_costs = any(re.search(p, text, re.IGNORECASE) for p in costs_patterns)

        # Evaluate comprehensiveness
        score = len(found_mechanisms)
        if has_escalation:
            score += 1
        if has_timeframes:
            score += 1
        if has_costs:
            score += 1

        details = {
            'mechanisms': found_mechanisms,
            'has_escalation': has_escalation,
            'has_timeframes': has_timeframes,
            'has_costs': has_costs
        }

        if 'mediation' in found_mechanisms:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Mediation included (court-encouraged ADR method)',
                'legal_source': 'Halsey v Milton Keynes [2004] EWCA Civ 576',
                'details': details
            }

        if score >= 4:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Comprehensive dispute resolution provisions',
                'legal_source': self.legal_source,
                'details': details
            }

        if score >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Basic dispute resolution provisions',
                'legal_source': self.legal_source,
                'details': details,
                'suggestion': 'Consider adding mediation clause (encouraged by courts)'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Limited dispute resolution provisions',
            'legal_source': self.legal_source,
            'details': details,
            'suggestion': 'Add escalation procedure and consider ADR (mediation)'
        }
