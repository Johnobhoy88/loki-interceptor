"""
GDPR International Transfer Validator
Validates international data transfers against UK GDPR Chapter V (Articles 44-50)

Transfer mechanisms:
1. Adequacy decisions (Article 45)
2. Standard Contractual Clauses (SCCs) (Article 46)
3. Binding Corporate Rules (BCRs) (Article 47)
4. Derogations for specific situations (Article 49)

ICO Guidance: International Transfers
Post-Brexit: UK has its own adequacy framework
"""

import re
from typing import Dict, List, Set


class InternationalTransferValidator:
    """
    Validates international data transfer compliance
    References: UK GDPR Articles 44-50; ICO International Transfers Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Articles 44-50; DPA 2018 Schedule 21; ICO International Transfers"

        # UK adequacy decisions (countries with adequate protection)
        # As of 2024 - UK recognizes these jurisdictions
        self.adequate_countries = {
            # EEA countries
            'eea', 'european economic area',
            'eu', 'european union',
            'austria', 'belgium', 'bulgaria', 'croatia', 'cyprus', 'czech republic',
            'denmark', 'estonia', 'finland', 'france', 'germany', 'greece',
            'hungary', 'ireland', 'italy', 'latvia', 'lithuania', 'luxembourg',
            'malta', 'netherlands', 'poland', 'portugal', 'romania', 'slovakia',
            'slovenia', 'spain', 'sweden',
            'iceland', 'liechtenstein', 'norway',
            # Other adequate countries
            'andorra', 'argentina', 'canada', 'faroe islands', 'guernsey',
            'israel', 'isle of man', 'jersey', 'new zealand', 'switzerland',
            'uruguay', 'japan', 'south korea'
        }

        # Countries with partial adequacy (specific sectors)
        self.partial_adequacy = {
            'canada': 'PIPEDA organizations only',
            'japan': 'Organizations under APPI',
            'south korea': 'Organizations under PIPA'
        }

        # Transfer mechanisms
        self.transfer_mechanisms = {
            'adequacy': [
                r'adequacy\s+decision',
                r'adequate\s+(?:level\s+of\s+)?protection',
                r'adequate\s+jurisdiction',
            ],
            'sccs': [
                r'standard\s+contractual\s+clauses',
                r'\bSCCs?\b',
                r'model\s+clauses',
                r'standard\s+data\s+protection\s+clauses',
            ],
            'bcr': [
                r'binding\s+corporate\s+rules',
                r'\bBCRs?\b',
            ],
            'derogations': [
                r'derogation',
                r'explicit\s+consent.*transfer',
                r'necessary\s+for.*(?:contract|legal\s+claim)',
                r'important\s+(?:public\s+)?interest',
            ]
        }

    def validate_transfers(self, text: str) -> Dict:
        """
        Validates international data transfer compliance

        Returns:
            Dict with validation results including:
            - has_transfers: bool
            - is_compliant: bool
            - transfers_found: List[Dict]
            - mechanisms_used: List[str]
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'has_transfers': False,
            'is_compliant': False,
            'transfers_found': [],
            'mechanisms_used': [],
            'adequate_countries_mentioned': [],
            'inadequate_countries_mentioned': [],
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            results['issues'].append("No text provided for transfer validation")
            return results

        text_lower = text.lower()

        # Check if international transfers are mentioned
        transfer_mentioned = self._check_transfer_mentioned(text_lower)

        if not transfer_mentioned:
            # No transfers mentioned - compliant by default
            return results

        results['has_transfers'] = True

        # 1. Identify countries mentioned
        countries = self._identify_countries(text_lower)
        results['transfers_found'] = countries

        # 2. Check which countries have adequate protection
        for country_info in countries:
            country = country_info['country']
            if country in self.adequate_countries:
                results['adequate_countries_mentioned'].append(country)
            else:
                results['inadequate_countries_mentioned'].append(country)

        # 3. Check for transfer mechanisms
        mechanisms = self._check_transfer_mechanisms(text_lower)
        results['mechanisms_used'] = mechanisms

        # 4. Validate transfers to inadequate countries
        if results['inadequate_countries_mentioned']:
            if not mechanisms:
                results['issues'].append(
                    f"Transfers to non-adequate countries ({', '.join(results['inadequate_countries_mentioned'])}) "
                    f"without appropriate safeguards (Article 46 violation)"
                )
                results['severity'] = 'critical'
                results['suggestions'].append(
                    "For non-adequate countries, implement: Standard Contractual Clauses (SCCs), "
                    "Binding Corporate Rules (BCRs), or obtain explicit consent"
                )
            elif 'adequacy' in mechanisms:
                # They claim adequacy for non-adequate country
                results['issues'].append(
                    f"Claims adequacy for non-adequate countries: {', '.join(results['inadequate_countries_mentioned'])}"
                )
                results['severity'] = 'high'

        # 5. Check for vague transfer language
        vague_issues = self._check_vague_transfers(text_lower)
        results['warnings'].extend(vague_issues)

        # 6. Check for US-specific considerations (post-Schrems II)
        us_issues = self._check_us_transfers(text, text_lower, mechanisms)
        results['warnings'].extend(us_issues)

        # 7. Check for transfer impact assessments (TIAs)
        tia_warnings = self._check_tia(text_lower)
        results['warnings'].extend(tia_warnings)

        # 8. Check if recipients are named
        recipient_warnings = self._check_recipients(text_lower)
        results['warnings'].extend(recipient_warnings)

        # 9. Check for onward transfer provisions
        onward_warnings = self._check_onward_transfers(text_lower)
        results['warnings'].extend(onward_warnings)

        # Determine compliance
        results['is_compliant'] = (
            len(results['issues']) == 0 and
            (not results['has_transfers'] or
             len(results['mechanisms_used']) > 0 or
             all(c in self.adequate_countries for c in [ci['country'] for ci in countries]))
        )

        return results

    def _check_transfer_mentioned(self, text_lower: str) -> bool:
        """Check if international transfers are mentioned"""
        transfer_keywords = [
            'international transfer', 'transfer.*outside',
            'outside.*(?:uk|united kingdom|eea|eu)',
            'third country', 'third countr',
            'global.*transfer', 'cross.?border.*transfer'
        ]
        return any(re.search(kw, text_lower) for kw in transfer_keywords)

    def _identify_countries(self, text_lower: str) -> List[Dict]:
        """Identify specific countries/regions mentioned for transfers"""
        countries_found = []

        # Common country patterns in transfer contexts
        transfer_context_pattern = r'(?:transfer|send|store|process|host).*(?:in|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'

        # Check for specific country mentions
        all_countries = list(self.adequate_countries) + [
            'usa', 'united states', 'america', 'china', 'russia', 'india',
            'brazil', 'australia', 'singapore', 'hong kong', 'dubai', 'uae'
        ]

        for country in all_countries:
            if country in text_lower:
                context = self._get_context(text_lower, country, 50)
                countries_found.append({
                    'country': country,
                    'context': context
                })

        # Also check for regional mentions
        regions = ['asia', 'americas', 'africa', 'middle east', 'asia-pacific', 'apac']
        for region in regions:
            if region in text_lower:
                countries_found.append({
                    'country': region,
                    'context': self._get_context(text_lower, region, 50),
                    'is_region': True
                })

        return countries_found

    def _get_context(self, text: str, keyword: str, chars: int = 50) -> str:
        """Get context around a keyword"""
        pos = text.find(keyword)
        if pos == -1:
            return ""
        start = max(0, pos - chars)
        end = min(len(text), pos + len(keyword) + chars)
        return text[start:end].strip()

    def _check_transfer_mechanisms(self, text_lower: str) -> List[str]:
        """Check which transfer mechanisms are mentioned"""
        mechanisms_found = []

        for mechanism, patterns in self.transfer_mechanisms.items():
            if any(re.search(p, text_lower) for p in patterns):
                mechanisms_found.append(mechanism)

        return mechanisms_found

    def _check_vague_transfers(self, text_lower: str) -> List[str]:
        """Check for vague transfer language"""
        warnings = []

        vague_patterns = [
            (r'may\s+transfer.*(?:anywhere|globally|worldwide)',
             "Vague transfer statement - should specify countries/regions"),
            (r'transfer.*(?:to\s+)?(?:our\s+)?(?:partners|affiliates|subsidiaries)',
             "Vague recipient identification - should name specific entities or countries"),
            (r'(?:various|multiple)\s+(?:countries|jurisdictions)',
             "Vague jurisdiction specification - should list specific countries"),
        ]

        for pattern, message in vague_patterns:
            if re.search(pattern, text_lower):
                warnings.append(message)

        return warnings

    def _check_us_transfers(self, text: str, text_lower: str, mechanisms: List[str]) -> List[str]:
        """Check US-specific transfer considerations (post-Schrems II)"""
        warnings = []

        us_mentioned = any(kw in text_lower for kw in ['usa', 'united states', 'us ', 'america', 'u.s.'])

        if us_mentioned:
            # Check for Data Privacy Framework (successor to Privacy Shield)
            dpf_patterns = [
                r'data\s+privacy\s+framework',
                r'\bDPF\b',
                r'EU-US\s+Data\s+Privacy\s+Framework',
                r'UK\s+Extension\s+to\s+the\s+EU-US\s+DPF'
            ]

            has_dpf = any(re.search(p, text_lower) for p in dpf_patterns)

            # Check for Privacy Shield (invalidated - should warn)
            if re.search(r'privacy\s+shield', text_lower):
                warnings.append(
                    "Privacy Shield mentioned - INVALID since Schrems II (2020). Use Data Privacy Framework or SCCs instead"
                )

            if not has_dpf and 'sccs' not in mechanisms:
                warnings.append(
                    "US transfers mentioned without Data Privacy Framework or SCCs - ensure appropriate safeguards"
                )

            # Check for supplementary measures (required post-Schrems II)
            supp_patterns = [
                r'supplementary\s+measures',
                r'additional\s+safeguards',
                r'technical\s+(?:and\s+)?organizational\s+measures',
            ]

            has_supplementary = any(re.search(p, text_lower) for p in supp_patterns)

            if not has_supplementary:
                warnings.append(
                    "US transfers should reference supplementary measures (Schrems II requirement)"
                )

        return warnings

    def _check_tia(self, text_lower: str) -> List[str]:
        """Check for Transfer Impact Assessment (TIA)"""
        warnings = []

        tia_patterns = [
            r'transfer\s+(?:risk\s+)?assessment',
            r'\bTIA\b',
            r'impact\s+assessment.*transfer',
            r'assess.*(?:risks?|impact).*transfer',
        ]

        has_tia = any(re.search(p, text_lower) for p in tia_patterns)

        if not has_tia:
            warnings.append(
                "No mention of Transfer Impact Assessment - ICO recommends TIA for transfers to non-adequate countries"
            )

        return warnings

    def _check_recipients(self, text_lower: str) -> List[str]:
        """Check if transfer recipients are properly identified"""
        warnings = []

        recipient_patterns = [
            r'recipient.*(?:name|identit)',
            r'(?:transfer|send).*to\s+[A-Z][a-z]+\s+(?:Ltd|Inc|Corp|GmbH)',
            r'processor.*(?:located|based)\s+in',
        ]

        has_recipients = any(re.search(p, text_lower) for p in recipient_patterns)

        if not has_recipients:
            if 'transfer' in text_lower and 'third countr' in text_lower:
                warnings.append(
                    "Transfer recipients not clearly identified - should name specific entities"
                )

        return warnings

    def _check_onward_transfers(self, text_lower: str) -> List[str]:
        """Check for onward transfer provisions"""
        warnings = []

        onward_patterns = [
            r'onward\s+transfer',
            r'sub.?processor',
            r'further\s+transfer',
        ]

        has_onward = any(re.search(p, text_lower) for p in onward_patterns)

        if 'transfer' in text_lower and not has_onward:
            warnings.append(
                "No mention of onward transfer restrictions - consider addressing sub-processor transfers"
            )

        return warnings


def validate_international_transfers(text: str) -> Dict:
    """
    Convenience function to validate international transfers

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = InternationalTransferValidator()
    return validator.validate_transfers(text)
