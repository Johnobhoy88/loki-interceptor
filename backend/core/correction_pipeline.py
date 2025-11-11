"""
Correction Pipeline - Orchestrates multi-stage correction process

Stages:
1. VALIDATE - Validate inputs and document structure
2. ANALYZE - Analyze issues and plan corrections
3. CORRECT - Apply corrections
4. VERIFY - Verify correction quality and consistency
5. EXPORT - Prepare for export

Features:
- Stage-by-stage execution with progress tracking
- Rollback support
- Validation at each stage
- Performance metrics
- Caching support
"""

import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

try:
    from .corrector import DocumentCorrector
    from .cache import Cache
except ImportError:
    from corrector import DocumentCorrector
    from cache import Cache


class PipelineStage(str, Enum):
    """Pipeline execution stages"""
    VALIDATE = "validate"
    ANALYZE = "analyze"
    CORRECT = "correct"
    VERIFY = "verify"
    EXPORT = "export"


class PipelineError(Exception):
    """Pipeline execution error"""
    pass


class CorrectionPipeline:
    """
    Multi-stage correction pipeline with orchestration

    Features:
    - Stage-by-stage execution
    - Progress tracking
    - Error handling and rollback
    - Result caching
    - Performance monitoring
    """

    def __init__(
        self,
        algorithm_version: str = "2.0.0",
        enable_caching: bool = True,
        enable_rollback: bool = True
    ):
        """
        Initialize correction pipeline

        Args:
            algorithm_version: Correction algorithm version to use
            enable_caching: Enable result caching
            enable_rollback: Enable rollback on errors
        """
        self.algorithm_version = algorithm_version
        self.enable_caching = enable_caching
        self.enable_rollback = enable_rollback

        # Initialize components
        self.corrector = DocumentCorrector(advanced_mode=True)
        self.cache = Cache() if enable_caching else None

        # Pipeline state
        self.current_stage = None
        self.execution_log = []
        self.stage_results = {}

    async def execute(
        self,
        text: str,
        validation_results: Optional[Dict] = None,
        document_type: Optional[str] = None,
        stages: Optional[List[PipelineStage]] = None,
        auto_apply: bool = True,
        confidence_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Execute correction pipeline

        Args:
            text: Document text to correct
            validation_results: Validation results (if available)
            document_type: Document type for context-aware corrections
            stages: Stages to execute (default: all)
            auto_apply: Auto-apply high-confidence corrections
            confidence_threshold: Confidence threshold for auto-apply

        Returns:
            Complete correction result with pipeline execution details
        """
        start_time = time.time()

        # Default to all stages
        if stages is None:
            stages = [
                PipelineStage.VALIDATE,
                PipelineStage.ANALYZE,
                PipelineStage.CORRECT,
                PipelineStage.VERIFY
            ]

        # Check cache
        cache_key = None
        if self.enable_caching and self.cache:
            cache_key = self._generate_cache_key(text, validation_results, stages)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                cached_result['metadata']['from_cache'] = True
                return cached_result

        # Initialize result
        result = {
            'original_text': text,
            'corrected_text': text,
            'issues_found': 0,
            'issues_corrected': 0,
            'corrections': [],
            'suggestions': [],
            'improvement_score': 0.0,
            'algorithm_version': self.algorithm_version,
            'pipeline_execution': {
                'stages': [],
                'total_time_ms': 0,
                'errors': []
            }
        }

        try:
            # Execute stages in order
            for stage in stages:
                stage_result = await self._execute_stage(
                    stage,
                    result,
                    validation_results,
                    document_type,
                    auto_apply,
                    confidence_threshold
                )

                # Update result with stage output
                result = self._merge_stage_result(result, stage_result)

                # Log stage execution
                self.execution_log.append({
                    'stage': stage.value,
                    'status': 'completed',
                    'timestamp': datetime.utcnow().isoformat(),
                    'duration_ms': stage_result['metadata']['duration_ms']
                })

            # Calculate total execution time
            total_time = (time.time() - start_time) * 1000
            result['pipeline_execution']['total_time_ms'] = total_time
            result['pipeline_execution']['stages'] = self.execution_log

            # Cache result
            if self.enable_caching and self.cache and cache_key:
                self.cache.set(cache_key, result, expire=3600)

            return result

        except Exception as e:
            # Handle pipeline error
            if self.enable_rollback:
                # Rollback to last successful state
                result = self._rollback()

            # Add error to execution log
            result['pipeline_execution']['errors'].append({
                'stage': self.current_stage.value if self.current_stage else 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })

            # Return partial result
            return result

    async def _execute_stage(
        self,
        stage: PipelineStage,
        current_result: Dict,
        validation_results: Optional[Dict],
        document_type: Optional[str],
        auto_apply: bool,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """Execute a single pipeline stage"""
        self.current_stage = stage
        stage_start = time.time()

        if stage == PipelineStage.VALIDATE:
            result = await self._stage_validate(
                current_result['original_text'],
                validation_results
            )

        elif stage == PipelineStage.ANALYZE:
            result = await self._stage_analyze(
                current_result,
                validation_results,
                document_type
            )

        elif stage == PipelineStage.CORRECT:
            result = await self._stage_correct(
                current_result,
                validation_results,
                document_type,
                auto_apply,
                confidence_threshold
            )

        elif stage == PipelineStage.VERIFY:
            result = await self._stage_verify(current_result)

        elif stage == PipelineStage.EXPORT:
            result = await self._stage_export(current_result)

        else:
            raise PipelineError(f"Unknown stage: {stage}")

        # Add stage metadata
        result['metadata'] = {
            'stage': stage.value,
            'duration_ms': (time.time() - stage_start) * 1000,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Save stage result for potential rollback
        self.stage_results[stage.value] = result

        return result

    async def _stage_validate(self, text: str, validation_results: Optional[Dict]) -> Dict:
        """
        VALIDATE stage - Validate inputs and document structure

        Checks:
        - Text is not empty
        - Text size within limits
        - Validation results are valid (if provided)
        - Document structure is parseable
        """
        issues = []

        # Check text
        if not text or not text.strip():
            issues.append("Empty document text")

        if len(text.encode('utf-8')) > 10485760:  # 10MB
            issues.append("Document exceeds 10MB size limit")

        # Check validation results
        if validation_results:
            if not isinstance(validation_results, dict):
                issues.append("Invalid validation results format")
            elif 'validation' not in validation_results:
                issues.append("Missing validation data in results")

        # Document structure checks
        if text:
            # Check for common document issues
            if text.count('\n') < 2:
                issues.append("Document appears to be single line (possible formatting issue)")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'checks_performed': 4,
            'text_size_bytes': len(text.encode('utf-8')) if text else 0
        }

    async def _stage_analyze(
        self,
        current_result: Dict,
        validation_results: Optional[Dict],
        document_type: Optional[str]
    ) -> Dict:
        """
        ANALYZE stage - Analyze issues and plan corrections

        Analyzes:
        - Number and types of issues
        - Correctable vs. non-correctable issues
        - Correction strategies to apply
        - Estimated impact
        """
        text = current_result['original_text']

        # Get available corrections
        if validation_results:
            available_corrections = self.corrector.get_available_corrections(
                text,
                validation_results
            )
        else:
            available_corrections = {
                'total_gates': 0,
                'failing_gates': 0,
                'available_corrections': [],
                'estimated_changes': 0
            }

        # Analyze correction strategies
        strategy_breakdown = {}
        for correction in available_corrections.get('available_corrections', []):
            strategy = correction.get('strategy', 'unknown')
            if strategy not in strategy_breakdown:
                strategy_breakdown[strategy] = 0
            strategy_breakdown[strategy] += 1

        # Estimate impact
        estimated_changes = available_corrections.get('estimated_changes', 0)
        text_length = len(text)
        impact_percentage = min(100.0, (estimated_changes / max(text_length, 1)) * 100)

        return {
            'issues_detected': available_corrections.get('failing_gates', 0),
            'correctable_issues': len(available_corrections.get('available_corrections', [])),
            'strategy_breakdown': strategy_breakdown,
            'estimated_changes': estimated_changes,
            'estimated_impact_percentage': impact_percentage,
            'document_type': document_type or 'unknown'
        }

    async def _stage_correct(
        self,
        current_result: Dict,
        validation_results: Optional[Dict],
        document_type: Optional[str],
        auto_apply: bool,
        confidence_threshold: float
    ) -> Dict:
        """
        CORRECT stage - Apply corrections to document

        Applies:
        - Rule-based corrections
        - Template insertions
        - Structural reorganizations
        - Suggestion-based corrections
        """
        text = current_result['original_text']

        if not validation_results:
            # No validation results, cannot correct
            return {
                'corrected_text': text,
                'corrections': [],
                'suggestions': [],
                'issues_corrected': 0,
                'auto_applied': False
            }

        # Apply corrections using corrector
        correction_result = self.corrector.correct_document(
            text,
            validation_results,
            document_type=document_type,
            advanced_options={
                'multi_level': True,
                'context_aware': True,
                'document_metadata': {
                    'type': document_type,
                    'auto_apply': auto_apply,
                    'confidence_threshold': confidence_threshold
                }
            }
        )

        return {
            'corrected_text': correction_result.get('corrected', text),
            'corrections': correction_result.get('corrections_applied', []),
            'suggestions': correction_result.get('suggestions', []),
            'issues_corrected': correction_result.get('correction_count', 0),
            'strategies_applied': correction_result.get('strategies_applied', []),
            'determinism': correction_result.get('determinism', {}),
            'validation': correction_result.get('validation', {})
        }

    async def _stage_verify(self, current_result: Dict) -> Dict:
        """
        VERIFY stage - Verify correction quality and consistency

        Verifies:
        - Corrections were applied successfully
        - Document structure is maintained
        - No new errors introduced
        - Improvement metrics
        """
        original_text = current_result['original_text']
        corrected_text = current_result.get('corrected_text', original_text)
        corrections = current_result.get('corrections', [])

        # Calculate metrics
        text_changed = original_text != corrected_text
        changes_count = len(corrections)

        # Verify structure maintained
        original_lines = original_text.count('\n')
        corrected_lines = corrected_text.count('\n')
        structure_maintained = abs(original_lines - corrected_lines) < original_lines * 0.5  # Within 50%

        # Calculate improvement score
        issues_found = current_result.get('issues_found', 0)
        issues_corrected = current_result.get('issues_corrected', 0)
        improvement_score = 0.0
        if issues_found > 0:
            improvement_score = min(1.0, issues_corrected / issues_found)

        # Quality checks
        quality_checks = {
            'text_changed': text_changed,
            'corrections_applied': changes_count > 0,
            'structure_maintained': structure_maintained,
            'no_empty_result': bool(corrected_text.strip()),
            'improvement_achieved': improvement_score > 0.0
        }

        passed_checks = sum(1 for v in quality_checks.values() if v)
        total_checks = len(quality_checks)

        return {
            'quality_score': passed_checks / total_checks,
            'quality_checks': quality_checks,
            'improvement_score': improvement_score,
            'structure_maintained': structure_maintained,
            'verification_passed': passed_checks >= total_checks * 0.8  # 80% threshold
        }

    async def _stage_export(self, current_result: Dict) -> Dict:
        """
        EXPORT stage - Prepare result for export

        Prepares:
        - Format result for export
        - Generate metadata
        - Create export-ready package
        """
        return {
            'export_ready': True,
            'formats_available': ['json', 'xml', 'docx', 'html', 'markdown'],
            'export_metadata': {
                'algorithm_version': self.algorithm_version,
                'pipeline_version': '2.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'total_corrections': len(current_result.get('corrections', [])),
                'improvement_score': current_result.get('improvement_score', 0.0)
            }
        }

    def _merge_stage_result(self, current_result: Dict, stage_result: Dict) -> Dict:
        """Merge stage result into overall result"""
        # Remove metadata before merging
        metadata = stage_result.pop('metadata', {})

        # Merge stage result
        for key, value in stage_result.items():
            if key in current_result:
                # Update existing key
                if isinstance(value, dict) and isinstance(current_result[key], dict):
                    current_result[key].update(value)
                else:
                    current_result[key] = value
            else:
                current_result[key] = value

        return current_result

    def _generate_cache_key(
        self,
        text: str,
        validation_results: Optional[Dict],
        stages: List[PipelineStage]
    ) -> str:
        """Generate cache key for result"""
        # Create hash of inputs
        hash_input = f"{text}:{str(validation_results)}:{str([s.value for s in stages])}:{self.algorithm_version}"
        return f"pipeline:{hashlib.md5(hash_input.encode()).hexdigest()}"

    def _rollback(self) -> Dict:
        """Rollback to last successful stage"""
        # Find last successful stage
        if not self.stage_results:
            return {
                'original_text': '',
                'corrected_text': '',
                'corrections': [],
                'error': 'Pipeline failed with no successful stages'
            }

        # Return last successful stage result
        last_stage = list(self.stage_results.values())[-1]
        return last_stage

    def get_statistics(self) -> Dict:
        """Get pipeline statistics"""
        stats = self.corrector.get_correction_statistics()

        return {
            'algorithm_version': self.algorithm_version,
            'caching_enabled': self.enable_caching,
            'rollback_enabled': self.enable_rollback,
            'corrector_stats': stats,
            'execution_log_size': len(self.execution_log),
            'stages_cached': len(self.stage_results)
        }
