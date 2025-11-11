import re


class ConstructiveDismissalGate:
    def __init__(self):
        self.name = "constructive_dismissal"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 s.95(1)(c), Western Excavating v Sharp [1978]"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['resign', 'breach', 'trust', 'confidence', 'grievance'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        # Check for mutual trust and confidence
        trust_confidence_patterns = [
            r'(?:mutual\s+)?trust\s+and\s+confidence',
            r'implied\s+term',
            r'good\s+faith'
        ]

        mentions_trust = any(re.search(p, text, re.IGNORECASE) for p in trust_confidence_patterns)

        # Check for fundamental breach
        fundamental_breach_patterns = [
            r'fundamental\s+breach',
            r'material\s+breach',
            r'serious\s+breach',
            r'repudiatory'
        ]

        mentions_fundamental_breach = any(re.search(p, text, re.IGNORECASE) for p in fundamental_breach_patterns)

        # Check for common constructive dismissal triggers
        triggers = {
            'unilateral_variation': r'(?:change|vary|alter).*(?:term|condition|contract).*without.*(?:consent|agreement)',
            'demotion': r'demot(?:e|ion)',
            'pay_cut': r'(?:reduc|cut).*(?:pay|salary|wage)',
            'bullying_harassment': r'(?:bully|harassment)',
            'unsafe_work': r'(?:unsafe|dangerous).*(?:work|condition)',
            'undermining': r'undermin',
            'unreasonable_behaviour': r'unreasonable.*(?:behaviour|conduct|demand)'
        }

        found_triggers = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in triggers.items()}

        # Check for grievance procedure (allows employee to raise issues)
        grievance_patterns = [
            r'grievance',
            r'raise.*concern',
            r'complaint\s+procedure'
        ]

        has_grievance_procedure = any(re.search(p, text, re.IGNORECASE) for p in grievance_patterns)

        # Check for variation consultation
        consultation_patterns = [
            r'consult.*(?:before|prior\s+to).*chang',
            r'discuss.*(?:variation|change)',
            r'(?:mutual\s+)?(?:agreement|consent).*(?:variation|change)'
        ]

        requires_consultation = any(re.search(p, text, re.IGNORECASE) for p in consultation_patterns)

        elements_present = sum([
            mentions_trust,
            has_grievance_procedure,
            requires_consultation
        ])

        trigger_count = sum(found_triggers.values())

        # If triggers mentioned without protections, flag as risk
        if trigger_count >= 2 and not has_grievance_procedure:
            return {
                'status': 'WARNING',
                'severity': 'critical',
                'message': 'Constructive dismissal risk factors without grievance procedure',
                'legal_source': self.legal_source,
                'risk_factors': [k for k, v in found_triggers.items() if v],
                'suggestion': 'Add grievance procedure; ensure consultation before variations; avoid unilateral changes to terms'
            }

        if elements_present >= 2:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Good protections against constructive dismissal',
                'legal_source': self.legal_source,
                'protections': {
                    'trust_confidence': mentions_trust,
                    'grievance': has_grievance_procedure,
                    'consultation': requires_consultation
                }
            }

        if has_grievance_procedure:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Grievance procedure provides outlet for employee concerns',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding: mutual trust and confidence term, consultation requirement for variations'
            }

        return {
            'status': 'WARNING',
            'severity': 'high',
            'message': 'Limited protection against constructive dismissal claims',
            'legal_source': self.legal_source,
            'suggestion': 'Add: grievance procedure (ACAS Code), mutual trust and confidence term, consultation before variations, avoid unilateral changes'
        }
