"""
Confidence Scorer - Calculates confidence scores for corrections

Provides multi-factor confidence scoring for snippet applications and corrections:
- Pattern matching strength
- Gate severity alignment
- Historical success rate
- Context relevance
- Domain expertise level
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ConfidenceFactors:
    """Individual confidence factors that contribute to overall score"""
    pattern_match_strength: float = 0.0  # 0.0-1.0
    severity_alignment: float = 0.0  # 0.0-1.0
    historical_success: float = 0.0  # 0.0-1.0
    context_relevance: float = 0.0  # 0.0-1.0
    domain_expertise: float = 0.0  # 0.0-1.0
    snippet_specificity: float = 0.0  # 0.0-1.0

    def calculate_weighted_score(
        self,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate weighted confidence score

        Args:
            weights: Optional custom weights for each factor

        Returns:
            Overall confidence score 0.0-1.0
        """
        if weights is None:
            weights = {
                'pattern_match_strength': 0.25,
                'severity_alignment': 0.20,
                'historical_success': 0.20,
                'context_relevance': 0.15,
                'domain_expertise': 0.10,
                'snippet_specificity': 0.10
            }

        score = (
            self.pattern_match_strength * weights.get('pattern_match_strength', 0.25) +
            self.severity_alignment * weights.get('severity_alignment', 0.20) +
            self.historical_success * weights.get('historical_success', 0.20) +
            self.context_relevance * weights.get('context_relevance', 0.15) +
            self.domain_expertise * weights.get('domain_expertise', 0.10) +
            self.snippet_specificity * weights.get('snippet_specificity', 0.10)
        )

        return min(1.0, max(0.0, score))


class ConfidenceScorer:
    """
    Calculates confidence scores for corrections using multiple factors
    """

    def __init__(self):
        # Historical success tracking
        self.success_history: Dict[str, List[bool]] = defaultdict(list)
        self.snippet_applications: Dict[str, int] = defaultdict(int)
        self.snippet_successes: Dict[str, int] = defaultdict(int)

        # Domain expertise mappings
        self.domain_expertise_levels = {
            'fca_uk': 0.9,  # High confidence in FCA UK rules
            'gdpr_uk': 0.9,  # High confidence in GDPR UK rules
            'tax_uk': 0.85,  # Good confidence in Tax UK rules
            'nda_uk': 0.8,  # Good confidence in NDA rules
            'hr_scottish': 0.8,  # Good confidence in HR Scottish rules
            'generic': 0.6  # Medium confidence for generic corrections
        }

    def score_correction(
        self,
        gate_id: str,
        snippet_key: str,
        gate_severity: str,
        snippet_severity: str,
        context: Dict[str, Any],
        snippet_text: str = "",
        gate_message: str = ""
    ) -> ConfidenceFactors:
        """
        Calculate comprehensive confidence score for a correction

        Args:
            gate_id: ID of the failing gate
            snippet_key: Key of the snippet to apply
            gate_severity: Severity of the gate failure
            snippet_severity: Severity of the snippet
            context: Additional context (document type, module, etc.)
            snippet_text: The actual snippet text
            gate_message: Gate failure message

        Returns:
            ConfidenceFactors object with all scoring components
        """
        factors = ConfidenceFactors()

        # 1. Pattern Match Strength
        factors.pattern_match_strength = self._calculate_pattern_match(
            gate_id, snippet_key, gate_message, snippet_text
        )

        # 2. Severity Alignment
        factors.severity_alignment = self._calculate_severity_alignment(
            gate_severity, snippet_severity
        )

        # 3. Historical Success Rate
        factors.historical_success = self._calculate_historical_success(snippet_key)

        # 4. Context Relevance
        factors.context_relevance = self._calculate_context_relevance(
            gate_id, snippet_key, context
        )

        # 5. Domain Expertise Level
        factors.domain_expertise = self._calculate_domain_expertise(gate_id, context)

        # 6. Snippet Specificity
        factors.snippet_specificity = self._calculate_snippet_specificity(
            snippet_text, gate_id
        )

        return factors

    def _calculate_pattern_match(
        self,
        gate_id: str,
        snippet_key: str,
        gate_message: str,
        snippet_text: str
    ) -> float:
        """
        Calculate how well the snippet pattern matches the gate

        Returns: 0.0-1.0 confidence score
        """
        gate_id_lower = gate_id.lower()
        snippet_key_lower = snippet_key.lower()
        gate_message_lower = gate_message.lower()

        # Extract key terms from gate and snippet
        gate_terms = set(re.findall(r'\w+', gate_id_lower))
        snippet_terms = set(re.findall(r'\w+', snippet_key_lower))

        if not gate_terms:
            return 0.5  # Neutral score if no terms

        # Calculate term overlap
        overlap = gate_terms.intersection(snippet_terms)
        overlap_ratio = len(overlap) / len(gate_terms)

        # Check for direct substring match (higher confidence)
        direct_match = False
        for term in gate_terms:
            if len(term) > 3 and term in snippet_key_lower:
                direct_match = True
                break

        # Check message alignment
        message_match = False
        if gate_message_lower and snippet_text:
            message_terms = set(re.findall(r'\w{4,}', gate_message_lower))
            snippet_content_terms = set(re.findall(r'\w{4,}', snippet_text.lower()))
            if message_terms.intersection(snippet_content_terms):
                message_match = True

        # Calculate final score
        score = overlap_ratio * 0.6

        if direct_match:
            score += 0.3
        if message_match:
            score += 0.1

        return min(1.0, score)

    def _calculate_severity_alignment(
        self,
        gate_severity: str,
        snippet_severity: str
    ) -> float:
        """
        Calculate how well snippet severity aligns with gate severity

        Returns: 0.0-1.0 confidence score
        """
        severity_levels = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1,
            'info': 0
        }

        gate_level = severity_levels.get(gate_severity.lower(), 2)
        snippet_level = severity_levels.get(snippet_severity.lower(), 2)

        # Perfect match = 1.0
        if gate_level == snippet_level:
            return 1.0

        # Close match (within 1 level) = 0.8
        if abs(gate_level - snippet_level) == 1:
            return 0.8

        # Distant match (within 2 levels) = 0.5
        if abs(gate_level - snippet_level) == 2:
            return 0.5

        # Poor match = 0.3
        return 0.3

    def _calculate_historical_success(self, snippet_key: str) -> float:
        """
        Calculate success rate based on historical applications

        Returns: 0.0-1.0 confidence score
        """
        applications = self.snippet_applications.get(snippet_key, 0)
        successes = self.snippet_successes.get(snippet_key, 0)

        if applications == 0:
            return 0.7  # Default confidence for untested snippets

        success_rate = successes / applications

        # Apply smoothing for small sample sizes
        if applications < 5:
            # Weight towards default confidence for small samples
            weight = applications / 5.0
            return (success_rate * weight) + (0.7 * (1 - weight))

        return success_rate

    def _calculate_context_relevance(
        self,
        gate_id: str,
        snippet_key: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate relevance of snippet to document context

        Returns: 0.0-1.0 confidence score
        """
        document_type = context.get('document_type', '').lower()
        module_id = context.get('module_id', '').lower()

        if not document_type and not module_id:
            return 0.7  # Neutral score if no context

        gate_id_lower = gate_id.lower()
        snippet_key_lower = snippet_key.lower()

        # Check module alignment
        module_match = False
        if module_id:
            if module_id in gate_id_lower or module_id in snippet_key_lower:
                module_match = True

        # Check document type relevance
        doc_type_match = False
        if document_type:
            # Map document types to expected terms
            type_terms = {
                'financial': ['fca', 'investment', 'risk', 'client', 'money'],
                'privacy': ['gdpr', 'data', 'consent', 'privacy', 'processing'],
                'tax': ['tax', 'vat', 'hmrc', 'duty', 'corporation'],
                'nda': ['confidential', 'disclosure', 'nda', 'whistleblowing'],
                'employment': ['employment', 'hr', 'disciplinary', 'grievance']
            }

            expected_terms = type_terms.get(document_type, [])
            for term in expected_terms:
                if term in gate_id_lower or term in snippet_key_lower:
                    doc_type_match = True
                    break

        # Calculate score
        score = 0.5  # Base score

        if module_match:
            score += 0.3
        if doc_type_match:
            score += 0.2

        return min(1.0, score)

    def _calculate_domain_expertise(
        self,
        gate_id: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate domain expertise level for this correction area

        Returns: 0.0-1.0 confidence score
        """
        gate_id_lower = gate_id.lower()

        # Determine domain from gate ID
        domain = 'generic'

        if 'fca' in gate_id_lower or 'financial' in gate_id_lower:
            domain = 'fca_uk'
        elif 'gdpr' in gate_id_lower or 'data_protection' in gate_id_lower:
            domain = 'gdpr_uk'
        elif 'tax' in gate_id_lower or 'vat' in gate_id_lower or 'hmrc' in gate_id_lower:
            domain = 'tax_uk'
        elif 'nda' in gate_id_lower or 'confidential' in gate_id_lower:
            domain = 'nda_uk'
        elif 'hr' in gate_id_lower or 'employment' in gate_id_lower:
            domain = 'hr_scottish'

        return self.domain_expertise_levels.get(domain, 0.6)

    def _calculate_snippet_specificity(
        self,
        snippet_text: str,
        gate_id: str
    ) -> float:
        """
        Calculate how specific/targeted the snippet is

        More specific snippets generally have higher confidence

        Returns: 0.0-1.0 confidence score
        """
        if not snippet_text:
            return 0.5  # Neutral if no text

        # Longer, more detailed snippets are generally more specific
        length_score = min(len(snippet_text) / 500, 0.3)  # Up to 0.3 for length

        # Presence of specific markers increases confidence
        specificity_markers = [
            r'\[specify[:\]]',  # Contains placeholders
            r'must include',  # Strong requirements
            r'as required by',  # Legal citations
            r'article \d+',  # Article references
            r'section \d+',  # Section references
            r'regulation \d+',  # Regulation references
            r'FRN:',  # FCA reference number
            r'www\.',  # External references
            r'\d{4}/\d+',  # Legal citation format
        ]

        marker_count = 0
        for marker in specificity_markers:
            if re.search(marker, snippet_text, re.IGNORECASE):
                marker_count += 1

        marker_score = min(marker_count * 0.1, 0.4)  # Up to 0.4 for markers

        # Contains detailed structure (bullets, sections)
        structure_score = 0.0
        if '•' in snippet_text or '\n-' in snippet_text or '\n*' in snippet_text:
            structure_score = 0.2

        # Gate-specific terminology
        gate_specific_score = 0.0
        gate_terms = re.findall(r'\w{5,}', gate_id.lower())
        for term in gate_terms:
            if term in snippet_text.lower():
                gate_specific_score = 0.1
                break

        total_score = length_score + marker_score + structure_score + gate_specific_score
        return min(1.0, total_score)

    def record_application(
        self,
        snippet_key: str,
        success: bool
    ):
        """
        Record the outcome of a snippet application for historical tracking

        Args:
            snippet_key: The snippet that was applied
            success: Whether the application was successful
        """
        self.snippet_applications[snippet_key] += 1
        if success:
            self.snippet_successes[snippet_key] += 1
        self.success_history[snippet_key].append(success)

    def get_snippet_statistics(self, snippet_key: str) -> Dict[str, Any]:
        """
        Get historical statistics for a specific snippet

        Args:
            snippet_key: The snippet to query

        Returns:
            Dictionary with usage statistics
        """
        applications = self.snippet_applications.get(snippet_key, 0)
        successes = self.snippet_successes.get(snippet_key, 0)
        history = self.success_history.get(snippet_key, [])

        success_rate = successes / applications if applications > 0 else 0.0

        # Calculate recent success rate (last 10 applications)
        recent_history = history[-10:] if len(history) > 10 else history
        recent_success_rate = sum(recent_history) / len(recent_history) if recent_history else 0.0

        return {
            'snippet_key': snippet_key,
            'applications': applications,
            'successes': successes,
            'success_rate': success_rate,
            'recent_success_rate': recent_success_rate,
            'trending': 'up' if recent_success_rate > success_rate else 'down' if recent_success_rate < success_rate else 'stable'
        }

    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics across all snippets

        Returns:
            Dictionary with aggregate statistics
        """
        total_applications = sum(self.snippet_applications.values())
        total_successes = sum(self.snippet_successes.values())

        overall_success_rate = total_successes / total_applications if total_applications > 0 else 0.0

        # Top performing snippets
        top_snippets = sorted(
            [
                {
                    'snippet_key': key,
                    'success_rate': self.snippet_successes[key] / self.snippet_applications[key]
                    if self.snippet_applications[key] > 0 else 0.0,
                    'applications': self.snippet_applications[key]
                }
                for key in self.snippet_applications.keys()
            ],
            key=lambda x: (x['success_rate'], x['applications']),
            reverse=True
        )[:10]

        return {
            'total_applications': total_applications,
            'total_successes': total_successes,
            'overall_success_rate': overall_success_rate,
            'unique_snippets_used': len(self.snippet_applications),
            'top_performers': top_snippets
        }
