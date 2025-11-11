import re


class BullyingHarassmentPolicyGate:
    def __init__(self):
        self.name = "bullying_harassment_policy"
        self.severity = "critical"
        self.legal_source = "Equality Act 2010 s.26, Protection from Harassment Act 1997, Health and Safety at Work Act 1974"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['bully', 'harassment', 'dignity', 'respect', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        harassment_patterns = [
            r'harassment',
            r'bullying',
            r'dignity\s+at\s+work',
            r'hostile\s+(?:environment|workplace)'
        ]

        has_policy = any(re.search(p, text, re.IGNORECASE) for p in harassment_patterns)

        if not has_policy:
            return {'status': 'N/A', 'message': 'No bullying/harassment policy', 'legal_source': self.legal_source}

        elements = {
            'definition_bullying': r'bullying.*(?:is|means|includes)',
            'definition_harassment': r'harassment.*(?:is|means|includes)',
            'unwanted_conduct': r'unwanted\s+conduct',
            'protected_characteristics': r'protected\s+characteristic',
            'examples': r'(?:example|include|such\s+as).*(?:intimidat|humiliat|offens)',
            'zero_tolerance': r'zero\s+tolerance|not\s+tolerat',
            'reporting_procedure': r'(?:report|raise|complaint).*(?:how|procedure|process)',
            'confidentiality': r'confidential',
            'investigation': r'investigat',
            'sanctions': r'disciplinary|sanction|consequence',
            'protection_complainant': r'(?:no|not).*(?:detriment|victimi[sz]|retaliat)',
            'third_party_harassment': r'third\s+party|(?:client|customer|visitor)',
            'prevention_measures': r'(?:prevent|training|aware)',
            'timescales': r'within\s+\d+\s+(?:day|working\s+day)'
        }

        found = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        score = sum(found.values())

        if score >= 10:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive bullying/harassment policy ({score}/14 elements)',
                'legal_source': self.legal_source,
                'elements_found': [k for k, v in found.items() if v]
            }

        if score >= 6:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Bullying/harassment policy incomplete ({score}/14)',
                'legal_source': self.legal_source,
                'missing': [k for k, v in found.items() if not v][:5],
                'suggestion': 'Strengthen policy: definitions, reporting procedure, investigation, protection from victimisation'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate bullying/harassment policy',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited compensation for harassment; potential criminal liability',
            'suggestion': 'Add: clear definitions, examples, reporting procedure, investigation process, confidentiality, sanctions, protection from victimisation'
        }
