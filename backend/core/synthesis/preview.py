"""
Preview Mode - Dry-run correction preview without applying changes

Allows users to see what corrections would be applied without modifying the document.
Useful for review, approval workflows, and understanding correction impacts.
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import difflib


@dataclass
class CorrectionPreview:
    """Preview of a single correction"""
    snippet_key: str
    gate_id: str
    module_id: str
    severity: str
    confidence: float
    iteration: int
    order: int
    text_to_add: str
    insertion_point: str
    estimated_impact: str  # 'low', 'medium', 'high'
    gates_likely_fixed: List[str]
    potential_side_effects: List[str]


@dataclass
class PreviewResult:
    """Complete preview result for a document"""
    original_text: str
    proposed_corrections: List[CorrectionPreview]
    total_corrections: int
    estimated_success_rate: float
    high_confidence_corrections: int
    medium_confidence_corrections: int
    low_confidence_corrections: int
    estimated_gates_fixed: int
    estimated_gates_remaining: int
    warnings: List[str]
    recommendations: List[str]


class PreviewEngine:
    """
    Engine for generating correction previews without applying changes
    """

    def __init__(self):
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.0
        }

    def generate_preview(
        self,
        synthesis_result: Dict[str, Any],
        include_diff: bool = False
    ) -> PreviewResult:
        """
        Generate a detailed preview from synthesis results

        Args:
            synthesis_result: Results from synthesis engine in preview mode
            include_diff: Whether to include text diffs in preview

        Returns:
            PreviewResult with detailed correction information
        """
        original_text = synthesis_result.get('original_text', '')
        snippets_applied = synthesis_result.get('snippets_applied', [])

        # Convert snippets to preview objects
        previews = []
        for snippet in snippets_applied:
            preview = self._create_correction_preview(snippet, synthesis_result)
            previews.append(preview)

        # Categorize by confidence
        high_conf = sum(1 for p in previews if p.confidence >= self.confidence_thresholds['high'])
        medium_conf = sum(
            1 for p in previews
            if self.confidence_thresholds['medium'] <= p.confidence < self.confidence_thresholds['high']
        )
        low_conf = sum(1 for p in previews if p.confidence < self.confidence_thresholds['medium'])

        # Estimate success rate
        avg_confidence = sum(p.confidence for p in previews) / len(previews) if previews else 0.0

        # Generate warnings and recommendations
        warnings = self._generate_warnings(previews, synthesis_result)
        recommendations = self._generate_recommendations(previews, synthesis_result)

        # Estimate gates fixed
        initial_failures = synthesis_result.get('metrics', {}).get('gates_remaining', 0) + \
                          synthesis_result.get('metrics', {}).get('gates_fixed', 0)
        estimated_fixed = synthesis_result.get('metrics', {}).get('gates_fixed', len(previews))
        estimated_remaining = initial_failures - estimated_fixed

        return PreviewResult(
            original_text=original_text,
            proposed_corrections=previews,
            total_corrections=len(previews),
            estimated_success_rate=avg_confidence,
            high_confidence_corrections=high_conf,
            medium_confidence_corrections=medium_conf,
            low_confidence_corrections=low_conf,
            estimated_gates_fixed=estimated_fixed,
            estimated_gates_remaining=estimated_remaining,
            warnings=warnings,
            recommendations=recommendations
        )

    def _create_correction_preview(
        self,
        snippet: Dict[str, Any],
        synthesis_result: Dict[str, Any]
    ) -> CorrectionPreview:
        """Create a preview object for a single correction"""
        confidence = snippet.get('confidence', 0.0)

        # Estimate impact based on text length and severity
        text_added = snippet.get('text_added', '')
        severity = snippet.get('severity', 'medium').lower()

        if len(text_added) > 500 or severity in ['critical', 'high']:
            estimated_impact = 'high'
        elif len(text_added) > 200 or severity == 'medium':
            estimated_impact = 'medium'
        else:
            estimated_impact = 'low'

        # Determine insertion point
        insertion_point = self._determine_insertion_point(snippet)

        # Estimate which gates will be fixed
        gates_likely_fixed = [snippet.get('gate_id', 'unknown')]

        # Identify potential side effects
        side_effects = self._identify_side_effects(snippet, synthesis_result)

        return CorrectionPreview(
            snippet_key=snippet.get('snippet_key', ''),
            gate_id=snippet.get('gate_id', ''),
            module_id=snippet.get('module_id', ''),
            severity=snippet.get('severity', 'medium'),
            confidence=confidence,
            iteration=snippet.get('iteration', 1),
            order=snippet.get('order', 1),
            text_to_add=text_added,
            insertion_point=insertion_point,
            estimated_impact=estimated_impact,
            gates_likely_fixed=gates_likely_fixed,
            potential_side_effects=side_effects
        )

    def _determine_insertion_point(self, snippet: Dict[str, Any]) -> str:
        """Determine where the correction will be inserted"""
        # This would be extracted from snippet metadata if available
        return 'end'  # Default

    def _identify_side_effects(
        self,
        snippet: Dict[str, Any],
        synthesis_result: Dict[str, Any]
    ) -> List[str]:
        """Identify potential side effects of applying this correction"""
        side_effects = []

        text_added = snippet.get('text_added', '')
        confidence = snippet.get('confidence', 0.0)

        # Low confidence warning
        if confidence < 0.6:
            side_effects.append('Low confidence - may require manual review')

        # Large text addition warning
        if len(text_added) > 1000:
            side_effects.append('Large text addition - may significantly change document structure')

        # Check for conflicts
        conflicts = synthesis_result.get('conflicts', [])
        if conflicts:
            side_effects.append(f'May introduce {len(conflicts)} new validation issue(s)')

        return side_effects

    def _generate_warnings(
        self,
        previews: List[CorrectionPreview],
        synthesis_result: Dict[str, Any]
    ) -> List[str]:
        """Generate warnings based on preview analysis"""
        warnings = []

        # Low confidence corrections
        low_conf_count = sum(1 for p in previews if p.confidence < 0.6)
        if low_conf_count > 0:
            warnings.append(
                f'{low_conf_count} correction(s) have low confidence (<0.6) and may require review'
            )

        # High impact corrections
        high_impact_count = sum(1 for p in previews if p.estimated_impact == 'high')
        if high_impact_count > 0:
            warnings.append(
                f'{high_impact_count} correction(s) have high impact and may significantly alter the document'
            )

        # Conflicts detected
        conflicts = synthesis_result.get('conflicts', [])
        if conflicts:
            warnings.append(
                f'{len(conflicts)} potential conflict(s) detected - some corrections may introduce new issues'
            )

        # Non-convergence warning
        if not synthesis_result.get('converged', True):
            warnings.append('Corrections did not fully converge - some issues may remain')

        # Many iterations required
        iterations = synthesis_result.get('iterations', 0)
        if iterations >= 4:
            warnings.append(
                f'Required {iterations} iterations - document may be complex or have interdependent issues'
            )

        return warnings

    def _generate_recommendations(
        self,
        previews: List[CorrectionPreview],
        synthesis_result: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on preview analysis"""
        recommendations = []

        # High confidence corrections
        high_conf_count = sum(1 for p in previews if p.confidence >= 0.8)
        if high_conf_count > 0:
            recommendations.append(
                f'{high_conf_count} correction(s) have high confidence (≥0.8) and can be safely applied'
            )

        # Suggest manual review for low confidence
        low_conf = [p for p in previews if p.confidence < 0.6]
        if low_conf:
            recommendations.append(
                f'Manually review {len(low_conf)} low-confidence correction(s) before applying'
            )

        # Suggest iterative application
        if len(previews) > 10:
            recommendations.append(
                'Consider applying corrections in batches to validate incrementally'
            )

        # Suggest specific corrections first
        critical_corrections = [p for p in previews if p.severity.lower() == 'critical']
        if critical_corrections:
            recommendations.append(
                f'Apply {len(critical_corrections)} critical correction(s) first, then re-validate'
            )

        # Success rate estimation
        estimated_success = synthesis_result.get('metrics', {}).get('f1_score', 0.0)
        if estimated_success >= 0.9:
            recommendations.append(
                f'High estimated success rate ({estimated_success:.1%}) - safe to apply all corrections'
            )
        elif estimated_success >= 0.7:
            recommendations.append(
                f'Good estimated success rate ({estimated_success:.1%}) - review and apply'
            )
        else:
            recommendations.append(
                f'Moderate estimated success rate ({estimated_success:.1%}) - careful review recommended'
            )

        return recommendations

    def generate_diff_preview(
        self,
        original_text: str,
        corrected_text: str,
        context_lines: int = 3
    ) -> str:
        """
        Generate a unified diff showing proposed changes

        Args:
            original_text: Original document text
            corrected_text: Text with proposed corrections
            context_lines: Number of context lines to show

        Returns:
            Unified diff string
        """
        original_lines = original_text.splitlines(keepends=True)
        corrected_lines = corrected_text.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            corrected_lines,
            fromfile='original',
            tofile='corrected',
            n=context_lines
        )

        return ''.join(diff)

    def generate_html_preview(
        self,
        preview_result: PreviewResult,
        include_full_text: bool = False
    ) -> str:
        """
        Generate an HTML preview of corrections

        Args:
            preview_result: Preview result to render
            include_full_text: Whether to include full correction text

        Returns:
            HTML string
        """
        html = ['<div class="correction-preview">']

        # Summary section
        html.append('<div class="preview-summary">')
        html.append(f'<h2>Correction Preview - {preview_result.total_corrections} Proposed Corrections</h2>')
        html.append(f'<p>Estimated Success Rate: <strong>{preview_result.estimated_success_rate:.1%}</strong></p>')
        html.append(f'<p>High Confidence: {preview_result.high_confidence_corrections} | '
                   f'Medium: {preview_result.medium_confidence_corrections} | '
                   f'Low: {preview_result.low_confidence_corrections}</p>')
        html.append('</div>')

        # Warnings section
        if preview_result.warnings:
            html.append('<div class="preview-warnings">')
            html.append('<h3>⚠️ Warnings</h3>')
            html.append('<ul>')
            for warning in preview_result.warnings:
                html.append(f'<li>{warning}</li>')
            html.append('</ul>')
            html.append('</div>')

        # Recommendations section
        if preview_result.recommendations:
            html.append('<div class="preview-recommendations">')
            html.append('<h3>💡 Recommendations</h3>')
            html.append('<ul>')
            for rec in preview_result.recommendations:
                html.append(f'<li>{rec}</li>')
            html.append('</ul>')
            html.append('</div>')

        # Corrections list
        html.append('<div class="preview-corrections">')
        html.append('<h3>Proposed Corrections</h3>')

        for idx, correction in enumerate(preview_result.proposed_corrections, 1):
            confidence_class = 'high' if correction.confidence >= 0.8 else 'medium' if correction.confidence >= 0.6 else 'low'

            html.append(f'<div class="correction-item confidence-{confidence_class}">')
            html.append(f'<h4>#{idx}: {correction.gate_id}</h4>')
            html.append(f'<p><strong>Module:</strong> {correction.module_id} | '
                       f'<strong>Severity:</strong> {correction.severity} | '
                       f'<strong>Confidence:</strong> {correction.confidence:.2f}</p>')
            html.append(f'<p><strong>Impact:</strong> {correction.estimated_impact}</p>')

            if correction.potential_side_effects:
                html.append('<p><strong>Side Effects:</strong></p>')
                html.append('<ul>')
                for effect in correction.potential_side_effects:
                    html.append(f'<li>{effect}</li>')
                html.append('</ul>')

            if include_full_text:
                preview_text = correction.text_to_add[:200] + '...' if len(correction.text_to_add) > 200 else correction.text_to_add
                html.append(f'<pre class="correction-text">{preview_text}</pre>')

            html.append('</div>')

        html.append('</div>')
        html.append('</div>')

        return '\n'.join(html)

    def export_preview_json(self, preview_result: PreviewResult) -> Dict[str, Any]:
        """
        Export preview result as JSON-serializable dictionary

        Args:
            preview_result: Preview result to export

        Returns:
            Dictionary with all preview data
        """
        return {
            'original_text_length': len(preview_result.original_text),
            'proposed_corrections': [asdict(c) for c in preview_result.proposed_corrections],
            'total_corrections': preview_result.total_corrections,
            'estimated_success_rate': preview_result.estimated_success_rate,
            'high_confidence_corrections': preview_result.high_confidence_corrections,
            'medium_confidence_corrections': preview_result.medium_confidence_corrections,
            'low_confidence_corrections': preview_result.low_confidence_corrections,
            'estimated_gates_fixed': preview_result.estimated_gates_fixed,
            'estimated_gates_remaining': preview_result.estimated_gates_remaining,
            'warnings': preview_result.warnings,
            'recommendations': preview_result.recommendations
        }
