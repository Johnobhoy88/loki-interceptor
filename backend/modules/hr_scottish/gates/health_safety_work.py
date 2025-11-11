import re


class HealthSafetyWorkGate:
    def __init__(self):
        self.name = "health_safety_work"
        self.severity = "critical"
        self.legal_source = "Health and Safety at Work Act 1974, Management of Health and Safety at Work Regulations 1999"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['health', 'safety', 'accident', 'injury', 'risk', 'hazard'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        health_safety_patterns = [
            r'health\s+and\s+safety',
            r'safe.*(?:working|workplace)',
            r'H&S|HSE'
        ]

        has_hs_policy = any(re.search(p, text, re.IGNORECASE) for p in health_safety_patterns)

        if not has_hs_policy:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'No health and safety provisions',
                'legal_source': self.legal_source,
                'penalty': 'Unlimited fine; imprisonment for serious breaches; HSE enforcement',
                'suggestion': 'Must have health and safety policy per HSWA 1974 s.2'
            }

        elements = {
            'duty_of_care': r'(?:duty|obligation).*(?:health|safety|welfare)',
            'risk_assessment': r'risk\s+assessment',
            'safe_systems': r'safe\s+(?:system|working|practice|procedure)',
            'training': r'training.*(?:health|safety)',
            'ppe': r'(?:PPE|personal\s+protective\s+equipment)',
            'accident_reporting': r'(?:accident|incident).*(?:report|record)',
            'first_aid': r'first\s+aid',
            'fire_safety': r'fire.*(?:safety|evacuation|drill)',
            'consultation': r'consult.*(?:employee|representative).*(?:safety|health)',
            'right_to_refuse': r'(?:right|may).*(?:refuse|stop).*(?:unsafe|dangerous)',
            'no_detriment': r'(?:not|no).*detriment.*(?:raise|report).*(?:safety|hazard)',
            'display_screen': r'(?:DSE|display\s+screen|VDU|workstation\s+assessment)',
            'manual_handling': r'manual\s+handling',
            'stress': r'(?:stress|mental\s+health|wellbeing)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 10:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive health and safety policy ({score}/14 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 6:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': f'Health and safety policy incomplete ({score}/14)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:6],
                'suggestion': 'Add: risk assessments, safe systems, training, PPE, accident reporting, right to refuse unsafe work'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate health and safety policy',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited fine; criminal prosecution; HSE prohibition/improvement notices',
            'suggestion': 'Must include per HSWA 1974 & Management Regs 1999: risk assessments, safe systems, training, PPE, accident reporting, consultation, protection from detriment'
        }
