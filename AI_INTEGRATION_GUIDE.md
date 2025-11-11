# AI/ML Quality Enhancement Integration Guide

## Overview

The LOKI Interceptor AI Quality Enhancement Suite provides comprehensive utilities for improving AI integration quality, including prompt optimization, response validation, caching, cost tracking, and explainability features.

## Module Structure

### 1. Prompt Optimizer (`backend/ai/prompt_optimizer.py`)

Optimizes prompts to reduce token usage while maintaining quality.

**Key Classes:**
- `PromptOptimizer`: Main optimization engine
- `OptimizationStrategy`: Enum for optimization approaches
- `OptimizedPrompt`: Result object with metrics

**Usage Example:**

```python
from backend.ai import PromptOptimizer, OptimizationStrategy

optimizer = PromptOptimizer()

# Original prompt
prompt = "Please analyze the following document and provide comprehensive insights..."

# Optimize with hybrid strategy
result = optimizer.optimize(
    prompt=prompt,
    strategy=OptimizationStrategy.HYBRID,
    preserve_meaning=True
)

print(f"Token reduction: {result.token_reduction:.1f}%")
print(f"Quality score: {result.quality_score:.2f}")
print(f"Optimized: {result.optimized}")

# Get statistics
stats = optimizer.get_statistics()
print(f"Total optimizations: {stats['total_optimizations']}")
print(f"Cache hits: {stats['cache_hit_potential']:.1%}")
```

**Optimization Strategies:**
- `COMPRESS`: Reduce tokens while maintaining meaning
- `ENHANCE_CLARITY`: Add structural markers
- `STRUCTURE`: Add format indicators
- `HYBRID`: Combine multiple strategies

### 2. Response Validator (`backend/ai/response_validator.py`)

Validates and scores AI responses for quality across multiple dimensions.

**Key Classes:**
- `ResponseValidator`: Validation engine
- `ValidationRule`: Custom validation rules
- `ValidationResult`: Detailed validation results

**Usage Example:**

```python
from backend.ai import ResponseValidator, ValidationLevel, ValidationRule, RuleType

validator = ResponseValidator(level=ValidationLevel.MODERATE)

# Validate response
response = "Based on the analysis, we recommend implementing..."
prompt = "Analyze the following document..."

result = validator.validate(response)

print(f"Valid: {result.is_valid}")
print(f"Score: {result.score:.2f}")
print(f"Errors: {result.errors}")
print(f"Warnings: {result.warnings}")
print(f"Suggestions: {result.suggestions}")

# Get statistics
stats = validator.get_statistics()
print(f"Validity rate: {stats['validity_rate']:.1%}")
print(f"Average score: {stats['average_score']:.2f}")
```

**Validation Levels:**
- `STRICT`: All checks must pass
- `MODERATE`: Most checks must pass (recommended)
- `LENIENT`: Core checks must pass

### 3. Semantic Cache (`backend/ai/semantic_cache.py`)

Intelligent caching based on semantic similarity for similar queries.

**Key Classes:**
- `SemanticCache`: Main cache engine
- `CacheEntry`: Cache entry object
- `CacheStrategy`: Matching strategies

**Usage Example:**

```python
from backend.ai import SemanticCache, CacheStrategy

cache = SemanticCache(strategy=CacheStrategy.HYBRID, max_size=5000)

# Store response
prompt = "Explain quantum entanglement"
response = "Quantum entanglement is a phenomenon where..."
cache.set(prompt, response, ttl_minutes=60, metadata={"domain": "physics"})

# Retrieve with semantic matching
result = cache.get(
    "What is quantum entanglement?",
    similarity_threshold=0.85,
    use_semantic=True
)

if result:
    response, entry = result
    print(f"Hit! Similarity: {entry.similarity_score:.2f}")
    print(f"Response: {response}")

# Cache statistics
stats = cache.get_statistics()
print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Cache size: {stats['cache_size']}")
```

**Caching Strategies:**
- `EXACT`: Exact match only (fast, low recall)
- `FUZZY`: Fuzzy string matching (balanced)
- `SEMANTIC`: Full semantic similarity (accurate, slower)
- `HYBRID`: Combine multiple strategies (recommended)

### 4. Context Window Manager (`backend/ai/context_manager.py`)

Manages AI model context windows for optimal token usage.

**Key Classes:**
- `ContextWindowManager`: Context management engine
- `ContextItem`: Individual context item
- `ContextStrategy`: Context eviction strategies

**Usage Example:**

```python
from backend.ai import ContextWindowManager, ContextStrategy

context = ContextWindowManager(max_tokens=8192, strategy=ContextStrategy.HYBRID)

# Add system context (higher priority)
context.add_context(
    "You are a compliance expert specializing in financial regulations",
    priority=0.95,
    is_system=True
)

# Add relevant user context
context.add_context(
    "The user is asking about GDPR compliance for a European company",
    priority=0.8,
    relevance_score=0.9
)

# Check current context
summary = context.get_context_summary()
print(f"Items: {summary['items']}")
print(f"Token usage: {summary['total_tokens']}/{summary['token_capacity']}")
print(f"Utilization: {summary['utilization']:.1%}")

# Format context for API
formatted = context.get_current_context()

# Cleanup expired context
expired = context.cleanup_expired()
```

**Context Strategies:**
- `SLIDING_WINDOW`: Keep most recent items
- `PRIORITY_BASED`: Keep high-priority items
- `RELEVANCE_BASED`: Keep relevant items
- `HYBRID`: Combine strategies (recommended)

### 5. A/B Testing Framework (`backend/ai/ab_testing.py`)

Structured testing of different prompt variations.

**Key Classes:**
- `ABTestingFramework`: Testing engine
- `TestVariant`: Prompt variant definition
- `TestResult`: Individual test result

**Usage Example:**

```python
from backend.ai import ABTestingFramework, TestVariant, MetricType

# Create A/B test
test = ABTestingFramework("prompt_v1_test")

# Define variants
variant_a = TestVariant(
    id="v1_concise",
    name="Concise Prompt",
    prompt_template="Analyze this: {content}",
    weight=0.5
)

variant_b = TestVariant(
    id="v1_detailed",
    name="Detailed Prompt",
    prompt_template="Thoroughly analyze the following content...: {content}",
    weight=0.5
)

test.add_variant(variant_a)
test.add_variant(variant_b)

# Select variant and record results
variant = test.select_variant(randomized=True)
response_time = 1.25
test.record_result(
    variant.id,
    MetricType.RESPONSE_TIME,
    response_time,
    metadata={"tokens": 450}
)

# Compare variants
comparison = test.get_comparison(MetricType.RESPONSE_TIME)
print(f"Comparison: {comparison}")

# Find winner
winner = test.get_winner(MetricType.RESPONSE_TIME, higher_is_better=False)
print(f"Winning variant: {winner}")

# Check statistical significance
is_sig = test.is_significant("v1_concise", "v1_detailed", MetricType.RESPONSE_TIME)
print(f"Significant difference: {is_sig}")
```

**Metric Types:**
- `QUALITY_SCORE`: Response quality
- `RESPONSE_TIME`: Latency
- `TOKEN_USAGE`: Token consumption
- `USER_SATISFACTION`: User ratings
- `CONVERSION`: Business metrics

### 6. Cost Tracker (`backend/ai/cost_tracker.py`)

Tracks and optimizes AI API costs.

**Key Classes:**
- `CostTracker`: Cost tracking engine
- `CostMetrics`: Cost summary statistics
- `Provider`: Provider enum

**Usage Example:**

```python
from backend.ai import CostTracker, Provider

tracker = CostTracker()

# Set custom pricing (optional)
tracker.set_provider_pricing(Provider.ANTHROPIC, 0.80, 2.40)  # Input, output per MTok

# Record API usage
tracker.record_usage(
    provider=Provider.ANTHROPIC,
    input_tokens=1250,
    output_tokens=850,
    metadata={"model": "claude-3.5-sonnet", "task": "analysis"}
)

# Get cost metrics
metrics = tracker.get_metrics(days_back=7)
print(f"Total cost (7d): ${metrics.total_cost:.2f}")
print(f"Requests: {metrics.requests_count}")
print(f"Avg cost/request: ${metrics.average_cost_per_request:.4f}")
print(f"Projected monthly: ${metrics.projected_monthly_cost:.2f}")

# Provider comparison
comparison = tracker.get_provider_comparison()
for provider, data in comparison.items():
    print(f"{provider}: ${data['total_cost']:.2f}")

# Get optimization recommendations
recommendations = tracker.get_optimization_recommendations(threshold=0.50)
for rec in recommendations:
    print(f"[{rec['type']}] {rec['message']}")

# Export report
tracker.export_report("/tmp/cost_report.txt")
```

**Default Pricing (as of Nov 2024):**
- Anthropic Claude 3.5: $0.80/$2.40
- OpenAI GPT-4: $2.50/$10.00
- Gemini 1.5: $0.075/$0.30

### 7. Quality Metrics (`backend/ai/quality_metrics.py`)

Measures AI response quality across multiple dimensions.

**Key Classes:**
- `MetricsCollector`: Metrics collection engine
- `QualityMetrics`: Overall quality assessment
- `QualityDimension`: Enum of quality aspects

**Usage Example:**

```python
from backend.ai import MetricsCollector

collector = MetricsCollector()

# Assess response quality
response = "Based on our analysis, we recommend..."
prompt = "Analyze the compliance risks..."
expected = "Key risks include data handling..."

metrics = collector.assess_quality(
    response=response,
    prompt=prompt,
    expected_output=expected
)

print(f"Overall score: {metrics.overall_score:.2f}/1.0")
print(f"Dimensions:")
for dim, score in metrics.dimension_scores.items():
    print(f"  {dim}: {score:.2f}")

# Get dimension trends
coherence_trend = collector.get_dimension_trend(
    collector.metrics_history[0].individual_scores[0].dimension
)
print(f"Coherence trend: {coherence_trend}")

# Get summary and alerts
summary = collector.get_summary()
alerts = collector.get_alerts()
print(f"Average score: {summary['average_overall_score']:.2f}")
print(f"Quality alerts: {len(alerts)}")
```

**Quality Dimensions:**
- `COHERENCE`: Logical flow and consistency
- `ACCURACY`: Correctness of information
- `RELEVANCE`: Alignment with prompt
- `COMPLETENESS`: Thoroughness of response
- `SAFETY`: Absence of harmful content
- `CLARITY`: Understandability

### 8. Fallback Handler (`backend/ai/fallback_handler.py`)

Manages fallback strategies for API failures.

**Key Classes:**
- `FallbackHandler`: Fallback management engine
- `FallbackStrategy`: Enum of strategies
- `FallbackAction`: Action definition

**Usage Example:**

```python
from backend.ai import FallbackHandler, FallbackAction, FallbackStrategy

handler = FallbackHandler()

# Setup fallback chain
handler.add_fallback(FallbackAction(
    strategy=FallbackStrategy.FAILOVER,
    target="openai",
    config={"provider": "openai"}
))

handler.add_fallback(FallbackAction(
    strategy=FallbackStrategy.CACHED,
    config={"ttl": 3600}
))

handler.add_fallback(FallbackAction(
    strategy=FallbackStrategy.DEGRADED,
    config={}
))

# On failure, get next action
from backend.ai.fallback_handler import FailureContext

failure = FailureContext(
    error_type="RateLimitError",
    error_message="API rate limit exceeded",
    timestamp="2024-11-11T10:00:00",
    provider="anthropic"
)

next_action = handler.get_next_fallback("anthropic", failure)
if next_action:
    print(f"Fallback strategy: {next_action.strategy}")

# Execute with retry
def api_call():
    # Your API call here
    return "response"

try:
    result = handler.execute_retry(api_call, max_attempts=3)
except Exception as e:
    result = handler.handle_degraded_service("original request")

# Health report
health = handler.get_health_report()
print(f"Provider health: {health['provider_health']}")
```

**Fallback Strategies:**
- `FAILOVER`: Switch to alternative provider
- `CACHED`: Return cached response
- `DEGRADED`: Provide simplified response
- `RETRY`: Retry with exponential backoff
- `CIRCUIT_BREAKER`: Prevent cascading failures

### 9. Explainability Engine (`backend/ai/explainability.py`)

Generates explanations for AI decisions and responses.

**Key Classes:**
- `ExplainabilityEngine`: Explanation generation engine
- `ExplainabilityReport`: Full explanation report
- `ExplanationType`: Enum of explanation types

**Usage Example:**

```python
from backend.ai import ExplainabilityEngine

engine = ExplainabilityEngine()

# Generate reasoning chain explanation
report = engine.generate_reasoning_chain(
    response="The analysis shows three main issues...",
    prompt="Analyze this document for compliance...",
    model="claude-3.5-sonnet"
)

print(report.title)
print(report.summary)
for step in report.steps:
    print(f"Step {step.step_number}: {step.description}")
    print(f"  Reasoning: {step.reasoning}")

# Get human-readable summary
summary = engine.get_explanation_summary(report.response_id)
print(summary)

# Confidence analysis
conf_report = engine.generate_confidence_analysis(
    response=response,
    domain="compliance"
)
print(f"Confidence: {conf_report.confidence_score:.0%}")

# Attribution analysis
attr_report = engine.generate_attribution_analysis(
    response=response,
    context_items=["requirement 1", "requirement 2", "best practice"]
)

# Statistics
stats = engine.get_statistics()
print(f"Total explanations: {stats['total_explanations']}")
```

**Explanation Types:**
- `DECISION_TREE`: Step-by-step decision process
- `REASONING_CHAIN`: Logical reasoning flow
- `ATTRIBUTION`: Which inputs influenced response
- `CONFIDENCE_ANALYSIS`: Confidence scoring
- `FEATURE_IMPORTANCE`: Most important features

### 10. Prompt Template Library (`backend/ai/prompt_templates.py`)

Reusable prompt templates for common tasks.

**Key Classes:**
- `PromptTemplateLibrary`: Template management
- `PromptTemplate`: Template definition
- `Predefined templates for:** analysis, compliance, correction, summarization, extraction

**Usage Example:**

```python
from backend.ai import PromptTemplateLibrary

library = PromptTemplateLibrary()

# Use built-in template
prompt = library.use_template(
    "analyze_document",
    variables={
        "document_type": "contract",
        "content": "Agreement between parties..."
    }
)
print(prompt)

# List templates
templates = library.list_templates(category="compliance")
for t in templates:
    print(f"{t.name} ({t.id}): {t.description}")

# Get recommendation
recommended = library.get_recommended_template("analyze this contract")
if recommended:
    print(f"Recommended: {recommended.name}")

# Create composite template
composite = library.create_composite_template(
    name="Full Document Analysis",
    sub_templates=["analyze_document", "check_compliance"],
    instructions="First analyze the document, then check compliance"
)

# Update quality score
library.update_template_score("analyze_document", 0.92)

# Get statistics
stats = library.get_statistics()
print(f"Templates: {stats['total_templates']}")
print(f"Total uses: {stats['total_uses']}")

# Export/import
library.export_templates("templates.json")
library.import_templates("templates.json")
```

**Built-in Templates:**
1. **analyze_document**: Document analysis
2. **check_compliance**: Compliance checking
3. **correct_content**: Content correction
4. **summarize_content**: Content summarization
5. **extract_information**: Information extraction

## Integration Pattern

### Full Integration Example

```python
from backend.ai import (
    PromptOptimizer,
    ResponseValidator,
    SemanticCache,
    ContextWindowManager,
    CostTracker,
    MetricsCollector,
    FallbackHandler,
    ExplainabilityEngine,
    PromptTemplateLibrary,
    OptimizationStrategy,
    ValidationLevel,
    CacheStrategy,
    Provider,
    FallbackAction,
    FallbackStrategy
)

class AIQualityManager:
    """Unified AI quality management"""

    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.validator = ResponseValidator(ValidationLevel.MODERATE)
        self.cache = SemanticCache(CacheStrategy.HYBRID)
        self.context = ContextWindowManager()
        self.cost_tracker = CostTracker()
        self.metrics = MetricsCollector()
        self.fallback = FallbackHandler()
        self.explainability = ExplainabilityEngine()
        self.templates = PromptTemplateLibrary()

    def process_request(self, prompt, domain="general"):
        # 1. Check cache
        cached = self.cache.get(prompt, threshold=0.85)
        if cached:
            return cached[0]

        # 2. Optimize prompt
        optimized = self.optimizer.optimize(prompt)

        # 3. Setup context
        self.context.add_context(
            f"Processing {domain} request",
            priority=0.8,
            relevance_score=0.9
        )

        # 4. Call API with fallback
        try:
            response = self._call_api(optimized.optimized)
        except Exception as e:
            action = self.fallback.get_next_fallback("anthropic", e)
            if action:
                response = self._handle_fallback(action)
            else:
                raise

        # 5. Validate response
        validation = self.validator.validate(response)
        if not validation.is_valid:
            print(f"Warnings: {validation.warnings}")

        # 6. Assess quality
        quality = self.metrics.assess_quality(response, prompt)

        # 7. Track costs
        self.cost_tracker.record_usage(
            Provider.ANTHROPIC,
            input_tokens=1250,
            output_tokens=850
        )

        # 8. Generate explanation
        explanation = self.explainability.generate_reasoning_chain(
            response, prompt
        )

        # 9. Cache result
        self.cache.set(prompt, response, ttl_minutes=60)

        return {
            "response": response,
            "validation": validation,
            "quality": quality,
            "explanation": explanation
        }
```

## Best Practices

### 1. Prompt Optimization
- Use `HYBRID` strategy for best balance
- Monitor quality scores - don't optimize below 0.7
- Cache optimized prompts for reuse
- Profile actual token counts with provider tokenizers

### 2. Response Validation
- Use `MODERATE` level for production
- Define custom rules for domain-specific validation
- Monitor validation trends over time
- Act on warnings even if response is technically valid

### 3. Semantic Caching
- Use `HYBRID` strategy for best results
- Set appropriate TTL based on content freshness requirements
- Monitor hit rates - aim for > 20% hit rate
- Cleanup expired entries regularly

### 4. Context Management
- Use `HYBRID` strategy with clear priority levels
- Keep system context separate from user context
- Monitor token utilization to avoid overflow
- Implement context summarization for long sessions

### 5. Cost Tracking
- Review costs weekly for anomalies
- Implement recommendations promptly
- Monitor provider pricing changes
- Set up cost alerts for budget tracking

### 6. Quality Metrics
- Monitor all dimensions, not just overall score
- Set thresholds appropriate for your use case
- Trend analysis more important than single scores
- Use alerts to catch quality regressions

### 7. Fallback Strategies
- Implement failover to multiple providers
- Test fallback paths regularly
- Monitor circuit breaker states
- Use exponential backoff for retries

### 8. Explainability
- Generate explanations for important decisions
- Use reasoning chains for transparency
- Track confidence scores
- Share confidence limitations with users

## Performance Considerations

### Token Reduction
- Prompt optimization: 15-30% token reduction typical
- Cache hit avoids re-computation entirely
- Context prioritization: 20-40% context efficiency gains

### Latency
- Cache lookups: <1ms (semantic matching)
- Semantic cache with 1000 entries: <100ms match time
- Validation: 10-50ms per response
- Metrics collection: 20-100ms per assessment

### Storage
- Semantic cache: ~5KB per entry (with embeddings)
- Cost log: ~1KB per API call
- Validation history: ~500B per validation
- Keep history bounded to manage memory

## Configuration Recommendations

### Production Settings
```python
# Prompt Optimization
optimizer = PromptOptimizer()
strategy = OptimizationStrategy.HYBRID

# Response Validation
validator = ResponseValidator(level=ValidationLevel.MODERATE)

# Caching
cache = SemanticCache(strategy=CacheStrategy.HYBRID, max_size=5000)

# Context
context = ContextWindowManager(max_tokens=8192, strategy=ContextStrategy.HYBRID)

# Fallback
fallback = FallbackHandler()
# Add: failover to alternative provider, cached response, then degraded
```

### Development Settings
```python
# More validation checks
validator = ResponseValidator(level=ValidationLevel.STRICT)

# Smaller cache for testing
cache = SemanticCache(max_size=100)

# Detailed logging
# Enable all quality checks
metrics = MetricsCollector()
```

## Troubleshooting

### High Costs
1. Check cost breakdown by provider
2. Implement prompt optimization
3. Enable semantic caching
4. Review token usage patterns
5. Consider provider switch

### Low Cache Hit Rate
1. Check similarity threshold setting
2. Review cache TTL values
3. Verify cache strategy is appropriate
4. Monitor cache size limits
5. Analyze query patterns

### Quality Regressions
1. Review validation alerts
2. Check metric trends
3. Validate recent prompt changes
4. Review context management
5. Check for API provider changes

### Performance Issues
1. Monitor context window utilization
2. Check cache size and cleanup frequency
3. Review metric collection overhead
4. Profile validation rule execution
5. Monitor semantic similarity computation

## Version Information

- **Suite Version**: 1.0.0
- **Last Updated**: November 2024
- **Python**: 3.8+
- **Dependencies**: None (minimal dependencies)

## Support and Resources

For issues, feature requests, or contributions:
- Check the module docstrings for detailed API documentation
- Review usage examples in each module
- Monitor quality metrics and validation results
- Use explainability features to debug issues
