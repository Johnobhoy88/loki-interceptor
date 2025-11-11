import re


class EqualityImpactAssessmentGate:
    def __init__(self):
        self.name = "equality_impact_assessment"
        self.severity = "high"
        self.legal_source = "Equality Act 2010 s.149 (Public Sector Equality Duty), Equality Act 2010 (Specific Duties) (Scotland) Regulations 2012"

    def _is_relevant(self, text):
        text_lower = (text or '').lower()
        return any(kw in text_lower for kw in ['equality', 'impact', 'assessment', 'discrimin', 'diversity', 'policy'])

    def check(self, text, document_type):
        if not self._is_relevant(text):
            return {'status': 'N/A', 'message': 'Not applicable', 'legal_source': self.legal_source}

        eia_patterns = [
            r'equality\s+impact\s+assessment|EIA|EQIA',
            r'(?:assess|consider).*(?:equality|discriminat).*impact',
            r'due\s+regard.*equality'
        ]

        has_eia = any(re.search(p, text, re.IGNORECASE) for p in eia_patterns)

        # Check for public sector equality duty elements
        psed_elements = {
            'eliminate_discrimination': r'eliminat.*discriminat',
            'advance_equality': r'advance.*equality\s+of\s+opportunity',
            'foster_good_relations': r'foster.*good\s+relations',
            'protected_characteristics': r'protected\s+characteristic',
            'monitoring': r'monitor(?:ing)?.*(?:equality|diversity|protected)',
            'publish_data': r'publish.*(?:data|information|report).*(?:equality|diversity)',
            'outcomes': r'(?:equality\s+)?outcome(?:s)?',
            'consultation': r'consult.*(?:affected|representative)'
        }

        found_elements = {k: bool(re.search(p, text, re.IGNORECASE)) for k, p in psed_elements.items()}
        score = sum(found_elements.values())

        # Check if this is a public sector organization
        public_sector_patterns = [
            r'public\s+(?:sector|body|authority)',
            r'(?:council|NHS|government|local\s+authority)',
            r'Scottish\s+(?:government|parliament|ministers)'
        ]

        is_public_sector = any(re.search(p, text, re.IGNORECASE) for p in public_sector_patterns)

        if is_public_sector and not has_eia:
            return {
                'status': 'FAIL',
                'severity': 'critical',
                'message': 'Public sector body without equality impact assessment provisions',
                'legal_source': 'Equality Act 2010 s.149, Specific Duties (Scotland) Regulations 2012',
                'penalty': 'Judicial review; failure to comply with public sector equality duty',
                'suggestion': 'Must have equality impact assessment process per s.149 PSED: eliminate discrimination, advance equality, foster good relations'
            }

        if has_eia:
            if score >= 5:
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': f'Comprehensive equality impact assessment framework ({score}/8 elements)',
                    'legal_source': self.legal_source,
                    'elements_found': [k for k, v in found_elements.items() if v]
                }

            if score >= 3:
                return {
                    'status': 'WARNING',
                    'severity': 'medium',
                    'message': f'Equality impact assessment incomplete ({score}/8 elements)',
                    'legal_source': self.legal_source,
                    'missing': [k for k, v in found_elements.items() if not v],
                    'suggestion': 'Ensure EIA covers: eliminate discrimination, advance equality, foster good relations, protected characteristics'
                }

            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Equality impact assessment mentioned',
                'legal_source': self.legal_source,
                'suggestion': 'Expand to cover PSED duties: eliminate discrimination, advance equality of opportunity, foster good relations'
            }

        # Not public sector and no EIA
        return {
            'status': 'N/A',
            'message': 'No equality impact assessment provisions',
            'legal_source': self.legal_source,
            'note': 'While PSED only applies to public sector, private employers should consider equality impact of policies'
        }
