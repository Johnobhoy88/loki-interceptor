"""
Prompt Optimization and Caching Module

Provides utilities for optimizing prompts through:
- Prompt compression
- Structural optimization
- Token reduction
- Clarity enhancement
- Reusable prompt patterns
"""

import hashlib
import json
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime


class OptimizationStrategy(str, Enum):
    """Strategy for prompt optimization"""
    COMPRESS = "compress"  # Reduce tokens while maintaining meaning
    ENHANCE_CLARITY = "enhance_clarity"  # Improve prompt clarity
    STRUCTURE = "structure"  # Add structure for better parsing
    HYBRID = "hybrid"  # Combine multiple strategies


@dataclass
class OptimizedPrompt:
    """Result of prompt optimization"""
    original: str
    optimized: str
    strategy: OptimizationStrategy
    token_reduction: float  # Percentage reduction
    compression_ratio: float  # Original tokens / optimized tokens
    quality_score: float  # 0-1, how well meaning is preserved
    timestamp: str
    metadata: Dict


class PromptOptimizer:
    """
    Optimizes prompts for better efficiency and quality

    Features:
    - Multiple optimization strategies
    - Token usage estimation
    - Quality preservation scoring
    - Prompt caching at optimizer level
    """

    def __init__(self):
        self.optimization_history: List[OptimizedPrompt] = []
        self.cache: Dict[str, OptimizedPrompt] = {}
        self.token_estimator = TokenEstimator()

    def optimize(
        self,
        prompt: str,
        strategy: OptimizationStrategy = OptimizationStrategy.HYBRID,
        preserve_meaning: bool = True
    ) -> OptimizedPrompt:
        """
        Optimize a prompt using specified strategy

        Args:
            prompt: Original prompt text
            strategy: Optimization strategy to use
            preserve_meaning: Whether to preserve exact meaning

        Returns:
            OptimizedPrompt with optimization details
        """
        # Check cache
        cache_key = self._get_cache_key(prompt, strategy)
        if cache_key in self.cache:
            return self.cache[cache_key]

        original_tokens = self.token_estimator.estimate(prompt)

        if strategy == OptimizationStrategy.COMPRESS:
            optimized = self._compress(prompt)
        elif strategy == OptimizationStrategy.ENHANCE_CLARITY:
            optimized = self._enhance_clarity(prompt)
        elif strategy == OptimizationStrategy.STRUCTURE:
            optimized = self._add_structure(prompt)
        else:  # HYBRID
            optimized = self._hybrid_optimize(prompt)

        optimized_tokens = self.token_estimator.estimate(optimized)

        result = OptimizedPrompt(
            original=prompt,
            optimized=optimized,
            strategy=strategy,
            token_reduction=(original_tokens - optimized_tokens) / original_tokens * 100 if original_tokens > 0 else 0,
            compression_ratio=original_tokens / optimized_tokens if optimized_tokens > 0 else 1.0,
            quality_score=self._estimate_quality(prompt, optimized),
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "original_tokens": original_tokens,
                "optimized_tokens": optimized_tokens,
                "strategy": strategy.value
            }
        )

        self.cache[cache_key] = result
        self.optimization_history.append(result)

        return result

    def _compress(self, prompt: str) -> str:
        """Compress prompt while maintaining meaning"""
        # Remove redundant words and phrases
        prompt = re.sub(r'\b(the|a|an)\b', '', prompt, flags=re.IGNORECASE)
        prompt = re.sub(r'\s+', ' ', prompt)
        prompt = prompt.strip()

        # Remove obvious filler words
        filler_words = [
            'please', 'kindly', 'would you', 'could you', 'thank you',
            'basically', 'essentially', 'in other words'
        ]

        for word in filler_words:
            prompt = re.sub(rf'\b{word}\b', '', prompt, flags=re.IGNORECASE)

        prompt = re.sub(r'\s+', ' ', prompt).strip()
        return prompt

    def _enhance_clarity(self, prompt: str) -> str:
        """Enhance prompt clarity with structure markers"""
        lines = prompt.split('\n')
        enhanced_lines = []

        for line in lines:
            line = line.strip()
            if line:
                # Add emphasis markers for key instructions
                if any(kw in line.lower() for kw in ['must', 'should', 'important', 'critical']):
                    enhanced_lines.append(f"[INSTRUCTION] {line}")
                elif any(kw in line.lower() for kw in ['example', 'e.g', 'such as']):
                    enhanced_lines.append(f"[EXAMPLE] {line}")
                elif line.endswith('?'):
                    enhanced_lines.append(f"[QUESTION] {line}")
                else:
                    enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    def _add_structure(self, prompt: str) -> str:
        """Add structural markers for parsing"""
        return f"""[PROMPT]
Input: {prompt}
[/PROMPT]

[EXPECTED_OUTPUT]
- Structured response
- Clear reasoning
- Actionable insights
[/EXPECTED_OUTPUT]"""

    def _hybrid_optimize(self, prompt: str) -> str:
        """Apply hybrid optimization combining multiple strategies"""
        # First compress
        optimized = self._compress(prompt)

        # Then enhance clarity
        optimized = self._enhance_clarity(optimized)

        return optimized

    def _estimate_quality(self, original: str, optimized: str) -> float:
        """
        Estimate how well optimization preserves meaning

        Returns value between 0-1 where 1 is perfect preservation
        """
        # Simple heuristic: measure keyword preservation
        original_words = set(original.lower().split())
        optimized_words = set(optimized.lower().split())

        # Key words that should be preserved
        key_indicators = ['must', 'should', 'important', 'critical', 'error', 'fail']

        original_keys = {w for w in original_words if any(k in w for k in key_indicators)}
        optimized_keys = {w for w in optimized_words if any(k in w for k in key_indicators)}

        if not original_keys:
            return 0.95  # If no key words, assume high quality

        preserved = len(original_keys & optimized_keys) / len(original_keys)
        return max(0.5, min(1.0, preserved * 0.95 + 0.05))

    def _get_cache_key(self, prompt: str, strategy: OptimizationStrategy) -> str:
        """Generate cache key for prompt and strategy"""
        combined = f"{prompt}:{strategy.value}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get_statistics(self) -> Dict:
        """Get optimization statistics"""
        if not self.optimization_history:
            return {}

        total_original = sum(h.metadata['original_tokens'] for h in self.optimization_history)
        total_optimized = sum(h.metadata['optimized_tokens'] for h in self.optimization_history)
        avg_quality = sum(h.quality_score for h in self.optimization_history) / len(self.optimization_history)

        return {
            "total_optimizations": len(self.optimization_history),
            "total_original_tokens": total_original,
            "total_optimized_tokens": total_optimized,
            "overall_reduction": (total_original - total_optimized) / total_original * 100 if total_original > 0 else 0,
            "average_quality_score": avg_quality,
            "cache_size": len(self.cache),
            "cache_hit_potential": len(self.cache) / (len(self.optimization_history) or 1)
        }


class TokenEstimator:
    """Estimates token count for prompts"""

    def estimate(self, text: str) -> int:
        """
        Simple token estimation (averages ~4 chars per token)
        For production, use official tokenizer from provider
        """
        # More accurate estimation: split by words and apply ratio
        words = len(text.split())
        # Average tokens per word varies, ~1.3 for English
        return max(1, int(words * 1.3))

    def estimate_by_provider(self, text: str, provider: str = "anthropic") -> int:
        """
        Provider-specific token estimation
        """
        if provider == "anthropic":
            # Anthropic uses more granular tokenization
            return self.estimate(text)
        elif provider == "openai":
            # OpenAI tokens are slightly different
            return int(self.estimate(text) * 1.1)
        else:
            return self.estimate(text)
