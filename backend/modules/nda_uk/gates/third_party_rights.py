import re


class ThirdPartyRightsGate:
    def __init__(self):
        self.name = "third_party_rights"
        self.severity = "medium"
        self.legal_source = "Contracts (Rights of Third Parties) Act 1999"

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

        # Check for third party rights exclusion/inclusion
        third_party_patterns = [
            r'contracts?\s+\(rights\s+of\s+third\s+parties\)\s+act\s+1999',
            r'third\s+part(?:y|ies).*(?:right|enforce)',
            r'no\s+(?:third\s+party|person).*(?:enforce|right)',
            r'(?:exclude|disclaim).*third\s+part(?:y|ies)',
            r'section\s+1.*1999\s+act'
        ]

        has_third_party_clause = any(re.search(p, text, re.IGNORECASE) for p in third_party_patterns)

        if not has_third_party_clause:
            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'No provision regarding third party rights (Contracts Act 1999)',
                'legal_source': self.legal_source,
                'suggestion': 'Consider adding clause to exclude third party rights unless intentionally granted',
                'risk': 'Third parties may have unintended rights to enforce agreement terms'
            }

        # Check if excluding or including third party rights
        exclusion_patterns = [
            r'(?:no|not).*third\s+part(?:y|ies).*(?:right|enforce)',
            r'exclude.*third\s+part(?:y|ies)',
            r'nothing.*confer.*third\s+part(?:y|ies)',
            r'only.*parties.*enforce'
        ]

        is_excluding = any(re.search(p, text, re.IGNORECASE) for p in exclusion_patterns)

        inclusion_patterns = [
            r'third\s+part(?:y|ies).*may\s+enforce',
            r'benefit\s+of.*third\s+part(?:y|ies)',
            r'entitled\s+to\s+enforce'
        ]

        is_including = any(re.search(p, text, re.IGNORECASE) for p in inclusion_patterns)

        if is_excluding:
            return {
                'status': 'PASS',
                'severity': 'none',
                'message': 'Third party rights explicitly excluded',
                'legal_source': self.legal_source
            }

        if is_including:
            # Check if third parties are identified
            identified_patterns = [
                r'identified.*third\s+part(?:y|ies)',
                r'named.*(?:beneficiary|beneficiaries)',
                r'following\s+(?:persons|parties)'
            ]
            has_identified = any(re.search(p, text, re.IGNORECASE) for p in identified_patterns)

            if has_identified:
                return {
                    'status': 'PASS',
                    'severity': 'none',
                    'message': 'Third party rights granted with identified parties',
                    'legal_source': self.legal_source
                }

            return {
                'status': 'WARNING',
                'severity': 'medium',
                'message': 'Third party rights granted but parties not clearly identified',
                'legal_source': self.legal_source,
                'suggestion': 'Clearly identify third parties entitled to enforce agreement'
            }

        return {
            'status': 'WARNING',
            'severity': 'low',
            'message': 'Third party rights mentioned but intent unclear',
            'legal_source': self.legal_source,
            'suggestion': 'Clarify whether third party rights are excluded or granted'
        }
