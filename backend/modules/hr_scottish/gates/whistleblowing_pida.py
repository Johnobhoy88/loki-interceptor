import re


class WhistleblowingPIDAGate:
    def __init__(self):
        self.name = "whistleblowing_pida"
        self.severity = "critical"
        self.legal_source = "Employment Rights Act 1996 Part IVA (ss.43A-43L), Public Interest Disclosure Act 1998"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['whistleblow', 'disclosure', 'raising concerns', 'speak up', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        whistleblowing_patterns = [
            r'whistleblow',
            r'protected\s+disclosure',
            r'public\s+interest\s+disclosure',
            r'raising\s+concerns?',
            r'speak\s+up'
        ]

        has_policy = any(re.search(p, text, re.IGNORECASE) for p in whistleblowing_patterns)

        if not has_policy:
            return {'status': 'N/A', 'message': 'No whistleblowing policy', 'legal_source': self.legal_source}

        # Check for qualifying disclosures (6 categories)
        qualifying_disclosures = {
            'crime': r'(?:criminal\s+offence|crime)',
            'legal_obligation': r'breach.*legal\s+obligation|fail.*comply.*law',
            'miscarriage_justice': r'miscarriage\s+of\s+justice',
            'health_safety': r'health\s+and\s+safety|danger',
            'environmental': r'environment(?:al)?.*damage',
            'cover_up': r'cover[- ]?up|conceal(?:ment)?'
        }

        found_disclosures = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in qualifying_disclosures.items()}
        disclosure_coverage = sum(found_disclosures.values())

        elements = {
            'public_interest': r'public\s+interest',
            'reasonable_belief': r'reasonable\s+belief|reasonably\s+believ',
            'internal_procedure': r'(?:report|raise).*(?:manager|designated|compliance)',
            'external_bodies': r'(?:regulator|prescribed\s+person|FCA|HSE|ICO)',
            'confidentiality': r'confidential|anonymous',
            'no_detriment': r'(?:no|not).*detriment|protection.*victimi[sz]',
            'no_dismissal': r'(?:not|unfair).*dismiss.*(?:whistleblow|disclosure)',
            'timescales': r'(?:promptly|timely|within).*(?:investigat|respond)',
            'feedback': r'feedback|outcome.*(?:disclosure|concern)',
            'training': r'training.*(?:awareness|whistleblow)'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in elements.items()}
        element_score = sum(found_elements.values())

        total_score = disclosure_coverage + element_score

        if disclosure_coverage >= 4 and element_score >= 6:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': f'Comprehensive PIDA whistleblowing policy ({disclosure_coverage}/6 disclosures, {element_score}/10 elements)',
                'legal_source': self.legal_source,
                'qualifying_disclosures': [k for k, v in found_disclosures.items() if v],
                'elements_found': [k for k, v in found_elements.items() if v]
            }

        if disclosure_coverage >= 3 and element_score >= 4:
            return {
                'status': 'WARNING',
                'severity': 'high',
                'message': f'Whistleblowing policy incomplete ({disclosure_coverage}/6 disclosures, {element_score}/10 elements)',
                'legal_source': self.legal_source,
                'missing_disclosures': [k for k, v in found_disclosures.items() if not v],
                'missing_elements': [k for k, v in found_elements.items() if not v][:5],
                'suggestion': 'Add qualifying disclosures: crime, legal breach, health/safety, environmental, miscarriage of justice, cover-up'
            }

        return {
            'status': 'FAIL',
            'severity': 'critical',
            'message': 'Inadequate whistleblowing protection',
            'legal_source': self.legal_source,
            'penalty': 'Unlimited compensation for detriment/dismissal; regulatory sanctions',
            'suggestion': 'Must include: 6 qualifying disclosures, public interest test, reasonable belief, internal procedure, external bodies, protection from detriment/dismissal per PIDA 1998'
        }
