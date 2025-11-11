"""
GDPR Data Minimization Principle Validator
Validates compliance with UK GDPR Article 5(1)(c) - Data Minimisation

Data Minimisation Principle:
"Personal data shall be adequate, relevant and limited to what is
necessary in relation to the purposes for which they are processed"

ICO Guidance: Data Minimisation
"""

import re
from typing import Dict, List, Set


class DataMinimizationValidator:
    """
    Validates data minimization principle compliance
    References: UK GDPR Article 5(1)(c); ICO Data Minimisation Guidance
    """

    def __init__(self):
        self.legal_source = "UK GDPR Article 5(1)(c); ICO Data Minimisation Guidance"

        # Excessive data indicators (red flags)
        self.excessive_data_categories = {
            'financial_excessive': [
                r'bank\s+(?:statement|balance)',
                r'credit\s+(?:score|history|report)',
                r'financial\s+(?:history|records)',
            ],
            'identity_excessive': [
                r'passport\s+(?:number|copy)',
                r'national\s+insurance\s+number',
                r'driving\s+licen[cs]e\s+(?:number|copy)',
                r'full\s+date\s+of\s+birth',
            ],
            'location_excessive': [
                r'precise\s+location',
                r'real.?time\s+location',
                r'continuous\s+(?:tracking|location)',
            ],
            'contacts_excessive': [
                r'contact\s+list',
                r'address\s+book',
                r'phone\s+contacts',
            ],
            'biometric_excessive': [
                r'fingerprint',
                r'facial\s+recognition',
                r'iris\s+scan',
                r'biometric',
            ],
        }

    def validate_minimization(self, text: str) -> Dict:
        """
        Validates data minimization compliance

        Returns:
            Dict with validation results including:
            - mentions_minimization: bool
            - is_compliant: bool
            - excessive_data_found: List[str]
            - justification_present: bool
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
        """
        results = {
            'mentions_minimization': False,
            'is_compliant': False,
            'excessive_data_found': [],
            'justification_present': False,
            'purpose_alignment': False,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'severity': 'none'
        }

        if not text:
            return results

        text_lower = text.lower()

        # Check if this is relevant (data collection/processing document)
        is_relevant = self._is_relevant(text_lower)

        if not is_relevant:
            return results

        # 1. Check if minimization principle is mentioned
        minimization_mentioned = self._check_minimization_mentioned(text_lower)
        results['mentions_minimization'] = minimization_mentioned

        if not minimization_mentioned:
            results['warnings'].append(
                "Data minimization principle not explicitly mentioned (Article 5(1)(c) requirement)"
            )
            results['suggestions'].append(
                "Add: 'We collect only the minimum personal data necessary for our stated purposes.'"
            )

        # 2. Check for excessive data collection
        excessive_data = self._check_excessive_data(text, text_lower)
        results['excessive_data_found'] = excessive_data

        if excessive_data:
            results['warnings'].append(
                f"Potentially excessive data categories: {', '.join(excessive_data)}"
            )
            results['suggestions'].append(
                "Ensure each data category is necessary and justified for the stated purpose"
            )

        # 3. Check for purpose-data alignment
        alignment = self._check_purpose_alignment(text_lower)
        results['purpose_alignment'] = alignment

        if not alignment:
            results['warnings'].append(
                "Data collection not clearly linked to stated purposes"
            )
            results['suggestions'].append(
                "Clearly explain why each data category is necessary: "
                "'We collect [data] to [specific purpose].'"
            )

        # 4. Check for justification of data collection
        justification = self._check_justification(text_lower)
        results['justification_present'] = justification

        if not justification and excessive_data:
            results['issues'].append(
                "Extensive data collection without clear justification violates minimization principle"
            )
            results['severity'] = 'medium'

        # 5. Check for blanket/catch-all clauses (red flag)
        blanket_issues = self._check_blanket_clauses(text_lower)
        results['issues'].extend(blanket_issues)

        # 6. Check for optional vs required data distinction
        if not self._check_optional_required_distinction(text_lower):
            results['warnings'].append(
                "No distinction between required and optional data (best practice for minimization)"
            )
            results['suggestions'].append(
                "Indicate: 'Required fields: [list]. Optional fields: [list].'"
            )

        # 7. Check for data collection limitation statements
        limitation_checks = self._check_limitation_statements(text_lower)
        results['warnings'].extend(limitation_checks)

        # 8. Check for function creep prevention
        function_creep = self._check_function_creep(text_lower)
        if function_creep:
            results['warnings'].append(function_creep)

        # 9. Check for periodic review
        if not self._check_periodic_review(text_lower):
            results['warnings'].append(
                "No mention of periodic review of data processing (best practice for minimization)"
            )
            results['suggestions'].append(
                "Add: 'We regularly review our data processing to ensure we collect only necessary data.'"
            )

        # Determine compliance
        results['is_compliant'] = (
            len(results['issues']) == 0 and
            (results['mentions_minimization'] or len(results['warnings']) <= 2)
        )

        return results

    def _is_relevant(self, text_lower: str) -> bool:
        """Check if document involves data collection/processing"""
        relevance_keywords = [
            'collect', 'collection', 'process', 'processing',
            'personal data', 'personal information',
            'privacy policy', 'privacy notice', 'data protection'
        ]
        return any(kw in text_lower for kw in relevance_keywords)

    def _check_minimization_mentioned(self, text_lower: str) -> bool:
        """Check if data minimization principle is mentioned"""
        minimization_patterns = [
            r'data\s+minimi[sz]ation',
            r'minimi[sz]e.*data',
            r'only.*(?:necessary|essential|required).*data',
            r'limit.*data.*(?:to|what\s+is)\s+necessary',
            r'(?:adequate|relevant).*limited.*necessary',
        ]

        return any(re.search(p, text_lower) for p in minimization_patterns)

    def _check_excessive_data(self, text: str, text_lower: str) -> List[str]:
        """Check for potentially excessive data collection"""
        excessive_found = []

        for category, patterns in self.excessive_data_categories.items():
            if any(re.search(p, text_lower) for p in patterns):
                # Check if there's justification nearby
                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        # Get context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(text_lower), match.end() + 100)
                        context = text_lower[start:end]

                        # Check if justified
                        justification_keywords = [
                            'necessary', 'required', 'essential',
                            'because', 'to verify', 'to prevent', 'for security'
                        ]

                        if not any(kw in context for kw in justification_keywords):
                            excessive_found.append(category)
                            break

        return list(set(excessive_found))

    def _check_purpose_alignment(self, text_lower: str) -> bool:
        """Check if data collection is aligned with stated purposes"""
        # Check for purpose statements
        has_purposes = bool(re.search(r'purpose[s]?.*(?:of|for)', text_lower))

        if not has_purposes:
            return False

        # Check for explicit linking of data to purposes
        alignment_patterns = [
            r'(?:collect|use).*\[data\].*(?:for|to)\s+\[purpose\]',
            r'necessary.*(?:for|to).*(?:purpose|service)',
            r'(?:in\s+order\s+to|to\s+enable|to\s+provide)',
        ]

        return any(re.search(p, text_lower) for p in alignment_patterns)

    def _check_justification(self, text_lower: str) -> bool:
        """Check if data collection is justified"""
        justification_patterns = [
            r'necessary\s+(?:for|to|because)',
            r'required\s+(?:for|to|because)',
            r'essential\s+(?:for|to)',
            r'(?:in\s+order\s+to|to\s+enable|to\s+provide)',
            r'(?:because|reason).*(?:collect|process)',
        ]

        return any(re.search(p, text_lower) for p in justification_patterns)

    def _check_blanket_clauses(self, text_lower: str) -> List[str]:
        """Check for blanket/catch-all data collection clauses"""
        issues = []

        blanket_patterns = [
            (r'(?:any|all).*(?:information|data).*(?:you\s+provide|from\s+you)',
             "Blanket clause: 'any/all information' - should specify data categories"),
            (r'collect.*(?:various|different|multiple).*(?:types?|kinds?).*(?:information|data)',
             "Vague data collection: should list specific categories"),
            (r'(?:information|data).*(?:including\s+but\s+not\s+limited\s+to)',
             "Open-ended list: 'including but not limited to' suggests unlimited collection"),
            (r'(?:other|additional).*(?:information|data).*as.*(?:necessary|needed|required)',
             "Catch-all clause: 'other data as necessary' - should be specific"),
        ]

        for pattern, message in blanket_patterns:
            if re.search(pattern, text_lower):
                issues.append(message)

        return issues

    def _check_optional_required_distinction(self, text_lower: str) -> bool:
        """Check if optional vs required data is distinguished"""
        distinction_patterns = [
            r'(?:required|mandatory).*(?:field|information|data)',
            r'(?:optional|voluntary).*(?:field|information|data)',
            r'marked\s+with.*\*.*(?:required|mandatory)',
            r'(?:must|need\s+to).*provide',
        ]

        return any(re.search(p, text_lower) for p in distinction_patterns)

    def _check_limitation_statements(self, text_lower: str) -> List[str]:
        """Check for data collection limitation statements"""
        warnings = []

        # Positive: explicit limitation
        limitation_patterns = [
            r'(?:only|just|solely).*(?:collect|process).*(?:necessary|required)',
            r'(?:do\s+not|will\s+not).*collect.*(?:unnecessary|excessive)',
        ]

        has_limitation = any(re.search(p, text_lower) for p in limitation_patterns)

        # Negative: unlimited collection
        unlimited_patterns = [
            r'(?:may|might).*collect.*(?:any|additional|other)',
            r'collect.*(?:as\s+much|all\s+available)',
        ]

        has_unlimited = any(re.search(p, text_lower) for p in unlimited_patterns)

        if has_unlimited and not has_limitation:
            warnings.append(
                "Language suggests unlimited data collection - violates minimization principle"
            )

        return warnings

    def _check_function_creep(self, text_lower: str) -> str:
        """Check for function creep (using data for new purposes)"""
        function_creep_patterns = [
            r'(?:may|might).*use.*(?:for\s+)?(?:other|additional|new).*purpose',
            r'(?:reserve|retain).*right.*use.*(?:for|in).*(?:any|other)',
            r'use.*data.*(?:as\s+we\s+see\s+fit|at\s+our\s+discretion)',
        ]

        if any(re.search(p, text_lower) for p in function_creep_patterns):
            return (
                "Function creep detected: using data for purposes beyond original collection "
                "violates minimization and purpose limitation principles"
            )

        return ""

    def _check_periodic_review(self, text_lower: str) -> bool:
        """Check for periodic review of data processing"""
        review_patterns = [
            r'(?:regularly|periodically).*(?:review|assess)',
            r'review.*data.*(?:processing|collection)',
            r'ongoing.*(?:review|assessment)',
        ]

        return any(re.search(p, text_lower) for p in review_patterns)


def validate_data_minimization(text: str) -> Dict:
    """
    Convenience function to validate data minimization

    Args:
        text: The text to validate

    Returns:
        Dictionary with validation results
    """
    validator = DataMinimizationValidator()
    return validator.validate_minimization(text)
