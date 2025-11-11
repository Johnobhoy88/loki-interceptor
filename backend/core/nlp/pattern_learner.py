"""
Pattern Learner - Adaptive learning from user feedback
Improves pattern detection over time based on user corrections and feedback
"""

import json
import pickle
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternFeedback:
    """User feedback on a pattern match"""
    pattern_id: str
    pattern_text: str
    matched_text: str
    context: str
    feedback_type: str  # 'accept', 'reject', 'modify'
    user_correction: Optional[str] = None
    timestamp: str = None
    gate_type: str = None
    confidence_before: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class PatternEffectiveness:
    """Effectiveness metrics for a pattern"""
    pattern_id: str
    pattern_text: str
    total_matches: int = 0
    accepted: int = 0
    rejected: int = 0
    modified: int = 0
    effectiveness_score: float = 0.0
    precision: float = 0.0
    false_positive_rate: float = 0.0
    avg_confidence: float = 0.0
    last_updated: str = None

    def calculate_metrics(self):
        """Calculate effectiveness metrics"""
        if self.total_matches == 0:
            self.effectiveness_score = 0.0
            self.precision = 0.0
            self.false_positive_rate = 0.0
            return

        # Precision: accepted / (accepted + rejected)
        total_decisions = self.accepted + self.rejected + self.modified
        if total_decisions > 0:
            self.precision = self.accepted / total_decisions
            self.false_positive_rate = self.rejected / total_decisions

        # Effectiveness score: weighted combination
        # Accept = 1.0, Modify = 0.5, Reject = 0.0
        weighted_score = (self.accepted * 1.0 + self.modified * 0.5) / total_decisions
        self.effectiveness_score = weighted_score

        self.last_updated = datetime.utcnow().isoformat()


class PatternLearner:
    """
    Learn from user feedback to improve pattern detection
    Tracks pattern effectiveness and suggests improvements
    """

    def __init__(self, storage_path: str = '/tmp/loki_pattern_learning.json'):
        self.storage_path = storage_path
        self.feedback_history: List[PatternFeedback] = []
        self.pattern_effectiveness: Dict[str, PatternEffectiveness] = {}
        self.learned_patterns: Dict[str, List[str]] = defaultdict(list)
        self.pattern_variants: Dict[str, Set[str]] = defaultdict(set)

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load saved learning data"""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

                # Load feedback history
                self.feedback_history = [
                    PatternFeedback(**fb) for fb in data.get('feedback_history', [])
                ]

                # Load effectiveness metrics
                for pattern_id, metrics in data.get('pattern_effectiveness', {}).items():
                    self.pattern_effectiveness[pattern_id] = PatternEffectiveness(**metrics)

                # Load learned patterns
                self.learned_patterns = defaultdict(list, data.get('learned_patterns', {}))

                # Load pattern variants
                variants = data.get('pattern_variants', {})
                self.pattern_variants = {
                    k: set(v) for k, v in variants.items()
                }

                logger.info(f"Loaded {len(self.feedback_history)} feedback entries")
                logger.info(f"Tracking {len(self.pattern_effectiveness)} patterns")

        except FileNotFoundError:
            logger.info("No existing learning data found. Starting fresh.")
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")

    def _save_data(self):
        """Save learning data"""
        try:
            data = {
                'feedback_history': [asdict(fb) for fb in self.feedback_history],
                'pattern_effectiveness': {
                    k: asdict(v) for k, v in self.pattern_effectiveness.items()
                },
                'learned_patterns': dict(self.learned_patterns),
                'pattern_variants': {
                    k: list(v) for k, v in self.pattern_variants.items()
                }
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info("Saved learning data")

        except Exception as e:
            logger.error(f"Error saving learning data: {e}")

    def record_feedback(
        self,
        pattern_id: str,
        pattern_text: str,
        matched_text: str,
        context: str,
        feedback_type: str,
        user_correction: Optional[str] = None,
        gate_type: Optional[str] = None,
        confidence: float = 0.0
    ):
        """
        Record user feedback on a pattern match

        Args:
            pattern_id: Unique pattern identifier
            pattern_text: The pattern that matched
            matched_text: The text that was matched
            context: Surrounding context
            feedback_type: 'accept', 'reject', or 'modify'
            user_correction: User's correction (if modified)
            gate_type: Gate type (fca, gdpr, etc.)
            confidence: Initial confidence score
        """
        feedback = PatternFeedback(
            pattern_id=pattern_id,
            pattern_text=pattern_text,
            matched_text=matched_text,
            context=context,
            feedback_type=feedback_type,
            user_correction=user_correction,
            gate_type=gate_type,
            confidence_before=confidence
        )

        self.feedback_history.append(feedback)

        # Update pattern effectiveness
        self._update_effectiveness(feedback)

        # Learn pattern variants
        if feedback_type == 'accept':
            self._learn_pattern_variant(pattern_id, matched_text)
        elif feedback_type == 'modify' and user_correction:
            self._learn_correction_pattern(pattern_id, matched_text, user_correction)

        # Save data
        self._save_data()

        logger.info(f"Recorded {feedback_type} feedback for pattern {pattern_id}")

    def _update_effectiveness(self, feedback: PatternFeedback):
        """Update pattern effectiveness metrics"""
        pattern_id = feedback.pattern_id

        if pattern_id not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_id] = PatternEffectiveness(
                pattern_id=pattern_id,
                pattern_text=feedback.pattern_text
            )

        metrics = self.pattern_effectiveness[pattern_id]
        metrics.total_matches += 1

        if feedback.feedback_type == 'accept':
            metrics.accepted += 1
        elif feedback.feedback_type == 'reject':
            metrics.rejected += 1
        elif feedback.feedback_type == 'modify':
            metrics.modified += 1

        # Update average confidence
        total_feedback = metrics.accepted + metrics.rejected + metrics.modified
        if total_feedback > 0:
            metrics.avg_confidence = (
                (metrics.avg_confidence * (total_feedback - 1) + feedback.confidence_before)
                / total_feedback
            )

        # Recalculate metrics
        metrics.calculate_metrics()

    def _learn_pattern_variant(self, pattern_id: str, matched_text: str):
        """Learn a new variant of a pattern that was accepted"""
        self.pattern_variants[pattern_id].add(matched_text)

        # If we have enough variants, suggest a generalized pattern
        if len(self.pattern_variants[pattern_id]) >= 5:
            self._suggest_generalized_pattern(pattern_id)

    def _learn_correction_pattern(
        self,
        pattern_id: str,
        original_text: str,
        corrected_text: str
    ):
        """Learn from user corrections to suggest new patterns"""
        correction_key = f"{pattern_id}_corrections"

        if correction_key not in self.learned_patterns:
            self.learned_patterns[correction_key] = []

        self.learned_patterns[correction_key].append({
            'original': original_text,
            'corrected': corrected_text,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Analyze correction patterns
        if len(self.learned_patterns[correction_key]) >= 3:
            self._analyze_correction_patterns(pattern_id)

    def _suggest_generalized_pattern(self, pattern_id: str):
        """Suggest a generalized pattern based on variants"""
        variants = list(self.pattern_variants[pattern_id])

        if len(variants) < 5:
            return

        # Simple generalization: find common words
        common_words = self._find_common_words(variants)

        if len(common_words) >= 2:
            suggested_pattern = '(?:' + '|'.join(common_words) + ')'
            logger.info(f"Suggested generalized pattern for {pattern_id}: {suggested_pattern}")

            # Store suggestion
            self.learned_patterns[f"{pattern_id}_suggestions"].append({
                'type': 'generalized',
                'pattern': suggested_pattern,
                'based_on': len(variants),
                'timestamp': datetime.utcnow().isoformat()
            })

    def _analyze_correction_patterns(self, pattern_id: str):
        """Analyze correction patterns to find systematic changes"""
        correction_key = f"{pattern_id}_corrections"
        corrections = self.learned_patterns[correction_key]

        if len(corrections) < 3:
            return

        # Find common replacements
        replacements = Counter()
        for correction in corrections:
            if isinstance(correction, dict):
                orig = correction['original'].lower()
                corr = correction['corrected'].lower()
                replacements[(orig, corr)] += 1

        # Suggest patterns for frequent corrections
        for (original, corrected), count in replacements.most_common(3):
            if count >= 2:
                logger.info(f"Frequent correction: '{original}' -> '{corrected}' ({count} times)")

                self.learned_patterns[f"{pattern_id}_suggestions"].append({
                    'type': 'replacement',
                    'original': original,
                    'corrected': corrected,
                    'frequency': count,
                    'timestamp': datetime.utcnow().isoformat()
                })

    def _find_common_words(self, texts: List[str]) -> List[str]:
        """Find words common to multiple texts"""
        if not texts:
            return []

        # Tokenize all texts
        word_sets = [set(text.lower().split()) for text in texts]

        # Find intersection
        common = set.intersection(*word_sets) if word_sets else set()

        # Filter out very common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        common = common - stopwords

        return list(common)

    def get_pattern_effectiveness(self, pattern_id: str) -> Optional[PatternEffectiveness]:
        """Get effectiveness metrics for a pattern"""
        return self.pattern_effectiveness.get(pattern_id)

    def get_top_patterns(self, n: int = 10) -> List[PatternEffectiveness]:
        """
        Get top N most effective patterns

        Args:
            n: Number of patterns to return

        Returns:
            List of PatternEffectiveness sorted by effectiveness score
        """
        patterns = list(self.pattern_effectiveness.values())
        patterns.sort(key=lambda p: p.effectiveness_score, reverse=True)
        return patterns[:n]

    def get_problematic_patterns(self, threshold: float = 0.3) -> List[PatternEffectiveness]:
        """
        Get patterns with low effectiveness (high false positive rate)

        Args:
            threshold: Maximum effectiveness score to include

        Returns:
            List of problematic patterns
        """
        problematic = [
            p for p in self.pattern_effectiveness.values()
            if p.effectiveness_score < threshold and p.total_matches >= 5
        ]

        problematic.sort(key=lambda p: p.effectiveness_score)
        return problematic

    def get_suggested_patterns(self, pattern_id: str = None) -> List[Dict]:
        """
        Get suggested patterns learned from feedback

        Args:
            pattern_id: Specific pattern ID, or None for all

        Returns:
            List of suggested patterns
        """
        if pattern_id:
            key = f"{pattern_id}_suggestions"
            return self.learned_patterns.get(key, [])

        # Return all suggestions
        suggestions = []
        for key, values in self.learned_patterns.items():
            if key.endswith('_suggestions'):
                suggestions.extend(values)

        return suggestions

    def get_effectiveness_report(self) -> Dict:
        """
        Generate comprehensive effectiveness report

        Returns:
            Dict with effectiveness statistics
        """
        if not self.pattern_effectiveness:
            return {
                'total_patterns': 0,
                'total_feedback': 0,
                'avg_effectiveness': 0.0
            }

        patterns = list(self.pattern_effectiveness.values())

        total_feedback = len(self.feedback_history)
        total_patterns = len(patterns)

        # Calculate averages
        avg_effectiveness = sum(p.effectiveness_score for p in patterns) / total_patterns
        avg_precision = sum(p.precision for p in patterns) / total_patterns
        avg_false_positive = sum(p.false_positive_rate for p in patterns) / total_patterns

        # Top and bottom patterns
        top_5 = self.get_top_patterns(5)
        bottom_5 = self.get_problematic_patterns(0.5)[:5]

        return {
            'total_patterns': total_patterns,
            'total_feedback': total_feedback,
            'avg_effectiveness': round(avg_effectiveness, 3),
            'avg_precision': round(avg_precision, 3),
            'avg_false_positive_rate': round(avg_false_positive, 3),
            'top_patterns': [
                {'id': p.pattern_id, 'score': p.effectiveness_score}
                for p in top_5
            ],
            'problematic_patterns': [
                {'id': p.pattern_id, 'score': p.effectiveness_score}
                for p in bottom_5
            ],
            'suggested_patterns': len(self.get_suggested_patterns())
        }

    def should_apply_pattern(
        self,
        pattern_id: str,
        confidence_threshold: float = 0.6
    ) -> Tuple[bool, float]:
        """
        Determine if a pattern should be applied based on learned effectiveness

        Args:
            pattern_id: Pattern identifier
            confidence_threshold: Minimum effectiveness score to apply

        Returns:
            (should_apply, adjusted_confidence)
        """
        effectiveness = self.pattern_effectiveness.get(pattern_id)

        if effectiveness is None:
            # No data yet, apply with default confidence
            return True, 0.7

        # Don't apply if effectiveness is too low
        if effectiveness.effectiveness_score < confidence_threshold:
            return False, effectiveness.effectiveness_score

        # Apply with adjusted confidence
        return True, effectiveness.effectiveness_score

    def get_feedback_stats_by_gate(self) -> Dict[str, Dict]:
        """Get feedback statistics broken down by gate type"""
        stats = defaultdict(lambda: {'accept': 0, 'reject': 0, 'modify': 0, 'total': 0})

        for feedback in self.feedback_history:
            gate = feedback.gate_type or 'unknown'
            stats[gate][feedback.feedback_type] += 1
            stats[gate]['total'] += 1

        return dict(stats)

    def export_learned_patterns(self) -> Dict:
        """Export learned patterns for integration into pattern registry"""
        export = {
            'suggested_patterns': self.get_suggested_patterns(),
            'effective_patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'pattern_text': p.pattern_text,
                    'effectiveness': p.effectiveness_score,
                    'precision': p.precision
                }
                for p in self.get_top_patterns(20)
            ],
            'pattern_variants': {
                k: list(v) for k, v in self.pattern_variants.items()
            }
        }

        return export


# Singleton instance
_pattern_learner_instance = None

def get_pattern_learner(storage_path: str = '/tmp/loki_pattern_learning.json') -> PatternLearner:
    """Get singleton pattern learner instance"""
    global _pattern_learner_instance
    if _pattern_learner_instance is None:
        _pattern_learner_instance = PatternLearner(storage_path)
    return _pattern_learner_instance
