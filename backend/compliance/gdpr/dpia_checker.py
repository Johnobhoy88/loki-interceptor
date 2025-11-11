"""
GDPR Data Protection Impact Assessment (DPIA) Checker
Validates DPIA requirements under UK GDPR Article 35

DPIA required when processing is "likely to result in high risk"
Mandatory for:
1. Systematic and extensive automated processing with legal/significant effects
2. Large scale processing of special category data
3. Systematic monitoring of public areas at large scale

ICO Guidance: DPIAs
"""

import re
from typing import Dict, List


class DPIAChecker:
    """
    Checks if DPIA is required and properly conducted
    References: UK GDPR Article 35; ICO DPIA Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Article 35; DPA 2018; ICO DPIA Guidance"

        # High-risk indicators that trigger DPIA requirement
        self.high_risk_indicators = {
            'automated_decisions': [
                r'automat(?:ed|ic).*decision',
                r'algorithmic.*decision',
                r'(?:AI|artificial\s+intelligence).*decision',
                r'machine\s+learning.*decision',
                r'profiling.*(?:legal|significant).*effect',
            ],
            'special_category_large_scale': [
                r'large.?scale.*(?:health|medical|biometric|genetic)',
                r'(?:process|collect).*(?:thousands|millions).*(?:health|medical)',
                r'systematic.*(?:health|medical|biometric).*data',
            ],
            'systematic_monitoring': [
                r'systematic(?:ally)?\s+monitor',
                r'(?:CCTV|surveillance|tracking).*public',
                r'continuous.*monitoring',
                r'real.?time.*monitoring',
            ],
            'vulnerable_subjects': [
                r'children.*data.*(?:large.?scale|systematic)',
                r'vulnerable.*(?:individuals|subjects)',
                r'employee.*monitoring',
            ],
            'new_technology': [
                r'new\s+technolog(?:y|ies)',
                r'innovative.*processing',
                r'novel.*(?:use|application).*(?:data|technology)',
            ],
            'biometric_identification': [
                r'biometric.*(?:identification|authentication)',
                r'facial\s+recognition',
                r'fingerprint.*(?:scanning|recognition)',
                r'iris\s+scan',
            ],
            'genetic_data': [
                r'genetic.*(?:data|testing|screening)',
                r'DNA.*(?:data|testing|analysis)',
            ],
            'data_matching': [
                r'data\s+matching',
                r'combin(?:e|ing).*(?:datasets|data\s+sources)',
                r'(?:cross.?reference|link).*(?:data|databases)',
            ],
            'denial_of_service': [
                r'processing.*(?:may\s+)?(?:prevent|deny).*(?:service|access)',
                r'credit\s+(?:scoring|checking|decision)',
                r'eligibility.*assessment',
            ]
        }

    def check_dpia_requirement(self, text: str) -> Dict:
        """
        Checks if DPIA is required and if conducted properly

        Returns:
            Dict with validation results including:
            - dpia_required: bool
            - dpia_conducted: bool
            - risk_indicators: List[str]
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'dpia_required': False,
            'dpia_conducted': False,
            'dpia_mentioned': False,
            'risk_indicators': [],
            'risk_count': 0,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # 1. Check for high-risk indicators
        risk_indicators = self._check_risk_indicators(text_lower)
        results['risk_indicators'] = risk_indicators
        results['risk_count'] = len(risk_indicators)

        # DPIA required if multiple risk factors or specific high-risk activities
        results['dpia_required'] = results['risk_count'] >= 2 or self._check_mandatory_dpia(text_lower)

        # 2. Check if DPIA is mentioned/conducted
        dpia_info = self._check_dpia_conducted(text_lower)
        results['dpia_mentioned'] = dpia_info['mentioned']
        results['dpia_conducted'] = dpia_info['properly_conducted']

        # 3. Generate issues and warnings
        if results['dpia_required']:
            if not results['dpia_mentioned']:
                results['issues'].append(
                    f"DPIA required (high-risk processing detected: {', '.join(results['risk_indicators'][:3])}) "
                    f"but not mentioned (Article 35 violation)"
                )
                results['severity'] = 'high'
                results['suggestions'].append(
                    "Conduct and document a Data Protection Impact Assessment including: "
                    "(1) Description of processing, (2) Necessity and proportionality, "
                    "(3) Risk assessment, (4) Mitigation measures"
                )
            elif not results['dpia_conducted']:
                results['warnings'].append(
                    "DPIA mentioned but insufficient detail - should include risk assessment and mitigation"
                )
                results['suggestions'].append(
                    "DPIA should assess: likelihood and severity of risks, measures to address risks, "
                    "and consultation with DPO if appointed"
                )

        # 4. Check for ICO consultation requirement (very high risk)
        if results['dpia_required']:
            ico_consult_required = self._check_ico_consultation_needed(text_lower, risk_indicators)
            if ico_consult_required:
                if not self._check_ico_consultation_mentioned(text_lower):
                    results['warnings'].append(
                        "Residual high risk detected - may require ICO consultation before processing (Article 36)"
                    )

        # 5. Check for DPIA elements if mentioned
        if results['dpia_mentioned']:
            element_warnings = self._check_dpia_elements(text_lower)
            results['warnings'].extend(element_warnings)

        return results

    def _check_risk_indicators(self, text_lower: str) -> List[str]:
        """Check for high-risk processing indicators"""
        indicators_found = []

        for category, patterns in self.high_risk_indicators.items():
            if any(re.search(p, text_lower) for p in patterns):
                indicators_found.append(category)

        return indicators_found

    def _check_mandatory_dpia(self, text_lower: str) -> bool:
        """Check for activities that always require DPIA"""
        mandatory_patterns = [
            r'systematic.*extensive.*(?:evaluation|assessment|profiling)',
            r'large.?scale.*special\s+category',
            r'systematic.*monitoring.*public.*(?:area|space)',
        ]

        return any(re.search(p, text_lower) for p in mandatory_patterns)

    def _check_dpia_conducted(self, text_lower: str) -> Dict:
        """Check if DPIA is mentioned and properly conducted"""
        result = {
            'mentioned': False,
            'properly_conducted': False
        }

        # Check if DPIA is mentioned
        dpia_patterns = [
            r'data\s+protection\s+impact\s+assessment',
            r'\bDPIA\b',
            r'privacy\s+impact\s+assessment',
            r'\bPIA\b',
            r'impact\s+assessment.*(?:processing|data\s+protection)',
        ]

        result['mentioned'] = any(re.search(p, text_lower) for p in dpia_patterns)

        if result['mentioned']:
            # Check for key DPIA elements
            elements = [
                r'(?:description|nature|scope).*processing',
                r'(?:purpose|necessity).*processing',
                r'risk.*(?:to|assessment)',
                r'(?:mitigat(?:ion|e)|safeguards|measures).*risk',
            ]

            elements_present = sum(1 for p in elements if re.search(p, text_lower))
            result['properly_conducted'] = elements_present >= 3

        return result

    def _check_ico_consultation_needed(self, text_lower: str, risk_indicators: List[str]) -> bool:
        """Check if ICO consultation is needed (Article 36)"""
        # Very high risk scenarios
        very_high_risk = [
            'systematic_monitoring',
            'biometric_identification',
            'vulnerable_subjects',
        ]

        # If multiple very high risk factors, consultation may be needed
        vhr_count = sum(1 for vhr in very_high_risk if vhr in risk_indicators)

        return vhr_count >= 2 or (
            'special_category_large_scale' in risk_indicators and
            'automated_decisions' in risk_indicators
        )

    def _check_ico_consultation_mentioned(self, text_lower: str) -> bool:
        """Check if ICO consultation is mentioned"""
        consultation_patterns = [
            r'consult.*(?:ICO|information\s+commissioner)',
            r'prior\s+consultation',
            r'supervisory\s+authority.*consult',
        ]

        return any(re.search(p, text_lower) for p in consultation_patterns)

    def _check_dpia_elements(self, text_lower: str) -> List[str]:
        """Check for required DPIA elements"""
        warnings = []

        required_elements = {
            'description': (
                r'(?:description|details).*(?:processing|data)',
                "DPIA should describe the processing operations"
            ),
            'necessity': (
                r'(?:necessity|justification|legitimate\s+interest)',
                "DPIA should assess necessity and proportionality"
            ),
            'risk_identification': (
                r'(?:identify|identif(?:y|ied)).*risk',
                "DPIA should identify risks to individuals"
            ),
            'risk_assessment': (
                r'(?:likelihood|probability|severity).*risk',
                "DPIA should assess likelihood and severity of risks"
            ),
            'mitigation': (
                r'(?:mitigat(?:e|ion)|safeguards|controls|measures).*risk',
                "DPIA should describe measures to mitigate risks"
            ),
            'dpo_consultation': (
                r'(?:DPO|data\s+protection\s+officer).*(?:consult|advice)',
                "DPIA should involve consultation with DPO (if appointed)"
            ),
        }

        for element, (pattern, message) in required_elements.items():
            if not re.search(pattern, text_lower):
                warnings.append(f"DPIA element missing: {message}")

        return warnings


def check_dpia_requirements(text: str) -> Dict:
    """
    Convenience function to check DPIA requirements

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    checker = DPIAChecker()
    return checker.check_dpia_requirement(text)
