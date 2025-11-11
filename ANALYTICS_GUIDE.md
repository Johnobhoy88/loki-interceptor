# LOKI Interceptor Analytics & Reporting Guide

## Overview

LOKI Interceptor includes comprehensive advanced analytics and reporting capabilities for compliance insights. This guide covers all analytics and reporting features, including trend analysis, predictive scoring, anomaly detection, forecasting, benchmarking, and custom reporting.

## Table of Contents

1. [Analytics Engine](#analytics-engine)
2. [Reporting Engine](#reporting-engine)
3. [API Integration](#api-integration)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)

---

## Analytics Engine

The analytics engine provides advanced compliance insights including trend analysis, predictions, anomaly detection, and benchmarking.

### Module: `backend/analytics/`

#### 1. Trend Analyzer (`trend_analyzer.py`)

**Purpose**: Analyzes historical compliance data to identify patterns and trends.

**Key Features**:
- Historical trend detection (improving, declining, stable, volatile)
- Linear regression analysis
- Moving average calculations
- Volatility measurement
- Predictive trend projections
- Anomaly-based insights

**Classes**:
- `TrendAnalyzer`: Main trend analysis class
- `TrendDirection`: Enum for trend direction
- `TrendAnalysis`: Result dataclass with insights and recommendations

**Usage Example**:

```python
from backend.analytics import TrendAnalyzer
from datetime import datetime, timedelta

analyzer = TrendAnalyzer(window_size=30)

# Sample data: list of (datetime, score) tuples
data = [
    (datetime.now() - timedelta(days=i), 70 + i*0.5)
    for i in range(30)
]

# Analyze trend
trend = analyzer.analyze_trend("gdpr_compliance", data)

print(f"Direction: {trend.direction}")  # 'improving'
print(f"Slope: {trend.slope}")          # Rate of change
print(f"Insights: {trend.insights}")    # Generated insights
print(f"Recommendations: {trend.recommendations}")
```

**Key Methods**:
- `analyze_trend()`: Analyze single metric
- `compare_trends()`: Compare multiple metrics
- `get_cached_trend()`: Retrieve cached analysis
- `clear_cache()`: Clear analysis cache

---

#### 2. Predictive Compliance Scorer (`predictive_scoring.py`)

**Purpose**: Predicts future compliance scores using machine learning.

**Key Features**:
- ARIMA-like forecasting
- Confidence interval calculations
- Risk probability estimation
- Factor importance analysis
- Ensemble predictions
- Anomaly-aware forecasting

**Classes**:
- `PredictiveComplianceScorer`: Main scorer class
- `PredictiveScoreResult`: Prediction result
- `PredictionPoint`: Individual prediction point
- `ConfidenceLevel`: Enum for confidence levels

**Usage Example**:

```python
from backend.analytics import PredictiveComplianceScorer
from datetime import datetime, timedelta

scorer = PredictiveComplianceScorer()

# Historical scores
historical = [
    (datetime.now() - timedelta(days=i), 70 + i*0.3)
    for i in range(20)
]

# Contributing factors (0-100 scale)
factors = {
    'gate_compliance': 75,
    'policy_adherence': 80,
    'documentation': 70,
    'audit_findings': 65,
    'corrective_actions': 78,
}

# Generate prediction
result = scorer.predict_compliance_score(
    module_name="GDPR",
    historical_scores=historical,
    contributing_factors=factors,
    periods_ahead=30,
    threshold=70.0
)

print(f"Current Score: {result.current_score}")
print(f"Risk Probability: {result.risk_probability}")
print(f"Trajectory: {result.improvement_trajectory}")
for prediction in result.predictions:
    print(f"  {prediction.timestamp.date()}: {prediction.predicted_score:.1f}")
```

**Key Methods**:
- `predict_compliance_score()`: Generate prediction
- `update_predictions()`: Update with new data
- `get_ensemble_prediction()`: Combine multiple models

---

#### 3. Anomaly Detector (`anomaly_detector.py`)

**Purpose**: Identifies unusual patterns and deviations in compliance data.

**Key Features**:
- Statistical anomaly detection (Z-score)
- Isolation Forest algorithm
- Seasonal decomposition
- Moving average deviation
- Contextual anomalies
- Multi-method detection

**Classes**:
- `AnomalyDetector`: Main anomaly detection class
- `Anomaly`: Detected anomaly dataclass
- `AnomalySeverity`: Enum for severity levels

**Usage Example**:

```python
from backend.analytics import AnomalyDetector
from datetime import datetime, timedelta

detector = AnomalyDetector(sensitivity=2.0)

# Data points
data = [
    (datetime.now() - timedelta(days=i), 70 + (i*0.5) if i % 5 != 0 else 50)
    for i in range(30)
]

# Detect anomalies
anomalies = detector.detect_anomalies("gdpr_score", data)

for anomaly in anomalies:
    print(f"{anomaly.severity}: {anomaly.description}")
    print(f"  Impact: {anomaly.impact}")
```

**Key Methods**:
- `detect_anomalies()`: Detect all anomalies
- `get_anomalies_by_metric()`: Filter by metric
- `get_critical_anomalies()`: Get critical issues

---

#### 4. Forecasting Engine (`forecasting_engine.py`)

**Purpose**: Forecasts future compliance states with scenario analysis.

**Key Features**:
- Multiple scenario generation (optimistic, base, pessimistic)
- Assumption-based forecasting
- Risk/opportunity identification
- Sensitivity analysis
- Monte Carlo simulations

**Classes**:
- `ComplianceForecastingEngine`: Main forecasting class
- `ComplianceForecast`: Forecast result
- `ScenarioForecast`: Individual scenario
- `Scenario`: Enum for forecast scenarios

**Usage Example**:

```python
from backend.analytics import ComplianceForecastingEngine
from datetime import datetime, timedelta

engine = ComplianceForecastingEngine()

# Historical data
historical = [
    (datetime.now() - timedelta(days=i), 70 + i*0.2)
    for i in range(20)
]

# External factors
factors = {'regulatory_changes': 15, 'resource_availability': 70}

# Generate forecast
forecast = engine.forecast(
    module_name="GDPR",
    historical_data=historical,
    external_factors=factors,
    forecast_periods=90
)

print(f"Most Likely: {forecast.most_likely_scenario}")
print(f"Risks: {forecast.key_risks}")
print(f"Opportunities: {forecast.key_opportunities}")

for scenario, scenario_data in forecast.scenarios.items():
    print(f"\n{scenario.value}:")
    print(f"  Probability: {scenario_data.probability:.0%}")
    for point in scenario_data.forecast_points[:5]:
        print(f"    {point.timestamp.date()}: {point.value:.1f}")
```

**Key Methods**:
- `forecast()`: Generate scenario forecast
- `sensitivity_analysis()`: Analyze parameter sensitivity

---

#### 5. Industry Benchmarking Engine (`benchmarking_engine.py`)

**Purpose**: Compares compliance metrics against industry standards.

**Key Features**:
- Benchmark database by industry/size
- Percentile ranking
- Gap analysis
- Best practice comparison
- Peer group analysis
- Target setting

**Classes**:
- `IndustryBenchmarkingEngine`: Main benchmarking class
- `BenchmarkComparison`: Comparison result
- `BenchmarkData`: Industry benchmark data
- `IndustryType`: Enum for industries
- `CompanySize`: Enum for company sizes

**Usage Example**:

```python
from backend.analytics import IndustryBenchmarkingEngine
from backend.analytics.benchmarking_engine import IndustryType, CompanySize

engine = IndustryBenchmarkingEngine()

# Compare single metric
comparison = engine.compare_to_benchmark(
    metric_name="gdpr_compliance",
    your_score=78.5,
    industry=IndustryType.FINANCIAL,
    company_size=CompanySize.ENTERPRISE
)

print(f"Your Score: {comparison.your_score}")
print(f"Benchmark Median: {comparison.benchmark_median}")
print(f"Percentile: {comparison.percentile:.0f}th")
print(f"Gap: {comparison.gap:+.1f} points")
print(f"Recommended Target: {comparison.recommended_target}")

# Compare multiple metrics
scores = {
    'gdpr_compliance': 78.5,
    'data_security': 82.0,
    'privacy_controls': 75.0,
}

comparisons = engine.benchmark_multiple_metrics(
    scores=scores,
    industry=IndustryType.FINANCIAL,
    company_size=CompanySize.ENTERPRISE
)

# Identify improvement opportunities
opportunities = engine.identify_improvement_opportunities(
    scores=scores,
    industry=IndustryType.FINANCIAL,
    company_size=CompanySize.ENTERPRISE
)

for opp in opportunities:
    print(f"Improve {opp['metric']} by {opp['improvement_needed']:.1f} points")
```

**Key Methods**:
- `compare_to_benchmark()`: Single metric comparison
- `benchmark_multiple_metrics()`: Compare multiple metrics
- `get_best_practices()`: Industry best practices
- `identify_improvement_opportunities()`: Gap areas
- `identify_competitive_advantages()`: Strength areas

---

#### 6. Analytics Dashboard (`dashboard.py`)

**Purpose**: Unified compliance analytics dashboard.

**Key Features**:
- Real-time metric tracking
- Customizable widgets
- Multiple dashboard profiles
- Export capabilities
- Alert integration

**Classes**:
- `AnalyticsDashboard`: Main dashboard class
- `AnalyticsDashboardConfig`: Dashboard configuration
- `DashboardWidget`: Individual widget

**Usage Example**:

```python
from backend.analytics import AnalyticsDashboard

dashboard = AnalyticsDashboard()

# Get default dashboard
default = dashboard.get_dashboard("default_compliance")
print(f"Widgets: {len(default.widgets)}")

# Create custom dashboard
custom = dashboard.create_custom_dashboard(
    dashboard_id="exec_dashboard",
    name="Executive Dashboard",
    description="High-level compliance overview",
    organization="My Org",
    widgets=['compliance_score', 'trend', 'module_comparison', 'alerts']
)

# Export dashboard data
data = dashboard.export_dashboard_data("exec_dashboard", format='json')
```

**Key Methods**:
- `create_custom_dashboard()`: Create new dashboard
- `add_widget()`: Add widget to dashboard
- `remove_widget()`: Remove widget
- `export_dashboard_data()`: Export data

---

## Reporting Engine

The reporting engine provides custom report generation, scheduling, and export.

### Module: `backend/reporting/`

#### 1. Report Builder (`report_builder.py`)

**Purpose**: Generates compliance reports with flexible customization.

**Key Features**:
- Customizable report templates
- Multi-section reports
- Professional formatting
- Branding support
- Multi-format export

**Classes**:
- `ReportBuilder`: Main report builder class
- `ReportTemplate`: Report template configuration
- `GeneratedReport`: Generated report instance
- `ReportType`: Enum for report types
- `ReportFormat`: Enum for output formats

**Usage Example**:

```python
from backend.reporting import ReportBuilder
from backend.reporting.report_builder import ReportType, ReportSection
from datetime import datetime, timedelta

builder = ReportBuilder()

# Create custom template
sections = [
    ReportSection(
        section_id="overview",
        title="Compliance Overview",
        section_type="summary",
        content_template="templates/overview.html",
        order=1
    ),
    ReportSection(
        section_id="metrics",
        title="Key Metrics",
        section_type="metrics",
        content_template="templates/metrics.html",
        order=2
    ),
]

template = builder.create_custom_template(
    template_id="custom_report",
    name="Custom Compliance Report",
    description="Company-specific report",
    report_type=ReportType.COMPLIANCE_OVERVIEW,
    sections=sections
)

# Generate report
data = {
    'overview': {'status': 'Compliant', 'score': 85},
    'metrics': {'GDPR': 82, 'CCPA': 78, 'HIPAA': 85},
}

report = builder.generate_report(
    template_id="custom_report",
    data=data,
    organization="My Organization",
    period_start=datetime.now() - timedelta(days=30),
    period_end=datetime.now()
)

print(f"Report ID: {report.report_id}")
print(f"Sections: {len(report.content)}")
```

**Key Methods**:
- `create_custom_template()`: Create template
- `generate_report()`: Generate report
- `add_section_to_template()`: Add section
- `clone_template()`: Clone template
- `bulk_generate_reports()`: Multiple reports

---

#### 2. Export Engine (`export_engine.py`)

**Purpose**: Exports reports in multiple formats.

**Supported Formats**:
- JSON
- CSV
- HTML
- PDF (requires reportlab)
- Excel (requires openpyxl)
- Word (requires python-docx)

**Usage Example**:

```python
from backend.reporting import ExportEngine
from backend.reporting.export_engine import ExportFormat, ExportConfig

engine = ExportEngine()

# Export data
data = {
    'compliance_metrics': {
        'GDPR': 85,
        'CCPA': 78,
        'HIPAA': 82
    },
    'findings': [
        'Finding 1: Data retention policy needs update',
        'Finding 2: Access controls require strengthening'
    ]
}

# Export to JSON
result = engine.export(
    data=data,
    format=ExportFormat.JSON,
    filename="report.json"
)

# Export to HTML with styling
html_result = engine.export(
    data=data,
    format=ExportFormat.HTML,
    filename="report.html",
    config=ExportConfig(
        format=ExportFormat.HTML,
        include_toc=True,
        include_charts=True
    )
)

# Export in multiple formats
multi = engine.export_report_with_format(
    report_data=data,
    formats=[ExportFormat.JSON, ExportFormat.CSV, ExportFormat.HTML],
    base_filename="compliance_report"
)
```

**Key Methods**:
- `export()`: Export in single format
- `export_report_with_format()`: Multi-format export
- `batch_export()`: Export multiple reports
- `validate_export_data()`: Data validation

---

#### 3. Report Scheduler (`scheduler.py`)

**Purpose**: Schedules and automates report generation and distribution.

**Supported Frequencies**:
- Daily
- Weekly
- Monthly
- Quarterly
- Annually

**Recipient Types**:
- Email
- API Webhooks
- Cloud Storage

**Usage Example**:

```python
from backend.reporting import ReportScheduler
from backend.reporting.scheduler import (
    Frequency, DayOfWeek, ScheduleConfig, RecipientConfig
)

scheduler = ReportScheduler()

# Create schedule
schedule = scheduler.create_schedule(
    schedule_id="weekly_compliance",
    name="Weekly Compliance Report",
    description="Sent every Monday morning",
    template_id="compliance_overview",
    frequency=Frequency.WEEKLY,
    time_of_day="09:00",
    day_of_week=DayOfWeek.MONDAY,
)

# Add recipients
scheduler.add_recipient(
    "weekly_compliance",
    RecipientConfig(
        recipient_type="email",
        recipient_address="compliance@company.com",
        format_preference="pdf"
    )
)

scheduler.add_recipient(
    "weekly_compliance",
    RecipientConfig(
        recipient_type="api_webhook",
        recipient_address="https://api.company.com/reports",
        format_preference="json"
    )
)

# Execute schedule
result = scheduler.execute_schedule("weekly_compliance")

# List schedules
schedules = scheduler.list_schedules(active_only=True)

# Get execution history
history = scheduler.get_execution_history("weekly_compliance", limit=10)
```

**Key Methods**:
- `create_schedule()`: Create scheduled report
- `add_recipient()`: Add recipient
- `execute_schedule()`: Run schedule
- `enable_schedule()` / `disable_schedule()`: Control schedule
- `get_execution_history()`: View history

---

#### 4. Executive Summary Generator (`executive_summary.py`)

**Purpose**: Creates concise executive-level compliance summaries.

**Features**:
- One-page executive overview
- Key metrics highlighted
- Risk assessment summary
- Critical actions identified
- Trend and forecast summaries
- Actionable recommendations

**Usage Example**:

```python
from backend.reporting import ExecutiveSummaryGenerator
from datetime import datetime, timedelta

generator = ExecutiveSummaryGenerator()

# Compliance data
compliance_data = {
    'overall_score': 78.5,
    'modules': {
        'GDPR': {'score': 85, 'findings': 2},
        'CCPA': {'score': 78, 'findings': 3},
        'HIPAA': {'score': 82, 'findings': 1},
    },
    'findings': [
        {'description': 'Data retention policy outdated', 'severity': 'high'},
        {'description': 'Access logs incomplete', 'severity': 'medium'},
    ]
}

# Analytics data (optional)
analytics = {
    'trends': {
        'GDPR': {'direction': 'improving'},
        'CCPA': {'direction': 'declining'},
    },
    'anomalies': []
}

# Generate summary
summary = generator.generate_summary(
    organization="My Organization",
    compliance_data=compliance_data,
    period_start=datetime.now() - timedelta(days=30),
    period_end=datetime.now(),
    analytics_data=analytics
)

# Export as text
text = generator.export_summary_text(summary)
print(text)
```

**Key Methods**:
- `generate_summary()`: Generate executive summary
- `export_summary_text()`: Export as formatted text

---

## API Integration

### Analytics API Endpoints (Example)

```python
# Trend Analysis
GET /api/analytics/trends/{metric_name}
  ?period=30&module={module_name}

# Predictions
GET /api/analytics/predictions/{module_name}
  ?periods=30&threshold=70

# Anomalies
GET /api/analytics/anomalies
  ?metric={metric}&severity=critical

# Forecasts
GET /api/analytics/forecasts/{module_name}
  ?scenarios=true

# Benchmarks
GET /api/analytics/benchmarks
  ?industry=financial&size=enterprise

# Dashboard
GET /api/analytics/dashboards/{dashboard_id}
POST /api/analytics/dashboards
  ?action=create
```

### Reporting API Endpoints (Example)

```python
# Report Templates
GET /api/reporting/templates
POST /api/reporting/templates
  ?action=create

# Generate Report
POST /api/reporting/reports
  {
    "template_id": "compliance_overview",
    "data": {...},
    "organization": "Company",
    "period": {"start": "2024-01-01", "end": "2024-01-31"}
  }

# Export Report
GET /api/reporting/reports/{report_id}/export
  ?format=pdf

# Scheduled Reports
GET /api/reporting/schedules
POST /api/reporting/schedules
  {
    "name": "Weekly Report",
    "frequency": "weekly",
    "recipients": [...]
  }
```

---

## Usage Examples

### Complete Analytics Workflow

```python
from backend.analytics import (
    TrendAnalyzer,
    PredictiveComplianceScorer,
    AnomalyDetector,
    ComplianceForecastingEngine,
    IndustryBenchmarkingEngine,
    AnalyticsDashboard
)
from backend.reporting import (
    ReportBuilder,
    ExportEngine,
    ReportScheduler,
    ExecutiveSummaryGenerator
)
from datetime import datetime, timedelta

# 1. Analyze trends
analyzer = TrendAnalyzer()
trends = analyzer.analyze_trend("gdpr_compliance", historical_data)

# 2. Predict future performance
scorer = PredictiveComplianceScorer()
prediction = scorer.predict_compliance_score(
    "GDPR", historical_data, factors
)

# 3. Detect anomalies
detector = AnomalyDetector()
anomalies = detector.detect_anomalies("gdpr_score", historical_data)

# 4. Generate forecast
forecaster = ComplianceForecastingEngine()
forecast = forecaster.forecast("GDPR", historical_data)

# 5. Compare to benchmarks
benchmarker = IndustryBenchmarkingEngine()
comparison = benchmarker.compare_to_benchmark(
    "gdpr_compliance", 85, IndustryType.FINANCIAL, CompanySize.ENTERPRISE
)

# 6. Generate report
builder = ReportBuilder()
report = builder.generate_report(
    "compliance_overview", report_data, "My Org",
    period_start, period_end
)

# 7. Create executive summary
summary_gen = ExecutiveSummaryGenerator()
summary = summary_gen.generate_summary(
    "My Org", compliance_data, period_start, period_end
)

# 8. Export to multiple formats
exporter = ExportEngine()
exports = exporter.export_report_with_format(
    report.content,
    [ExportFormat.PDF, ExportFormat.EXCEL],
    "compliance_report"
)

# 9. Schedule distribution
scheduler = ReportScheduler()
schedule = scheduler.create_schedule(
    "weekly_report", "Weekly Report", "GDPR",
    Frequency.WEEKLY, "09:00", DayOfWeek.MONDAY
)
scheduler.add_recipient(
    "weekly_report",
    RecipientConfig("email", "compliance@company.com")
)

# 10. View dashboard
dashboard = AnalyticsDashboard()
dash = dashboard.get_dashboard("default_compliance")
```

---

## Best Practices

### 1. Data Quality
- Ensure historical data is accurate and complete
- Validate data before analytics processing
- Handle missing data appropriately
- Regular data quality audits

### 2. Analytics
- Use appropriate window sizes for trend analysis
- Consider seasonal factors in forecasting
- Adjust sensitivity levels based on domain
- Validate predictions against actuals

### 3. Reporting
- Tailor reports to audience level (executive vs. technical)
- Include actionable recommendations
- Keep executive summaries concise
- Use clear, consistent naming conventions

### 4. Scheduling
- Test schedules before enabling
- Monitor execution history
- Implement error handling and retries
- Archive reports for compliance

### 5. Performance
- Cache frequently accessed analyses
- Use batch operations for bulk exports
- Limit historical data window when possible
- Implement pagination for large datasets

### 6. Security
- Validate all report data
- Sanitize HTML exports
- Secure scheduled report distribution
- Encrypt exported files containing sensitive data

---

## Configuration

### Environment Variables

```bash
# Analytics
ANALYTICS_CACHE_TTL=3600
ANALYTICS_TREND_WINDOW=30
ANALYTICS_FORECAST_PERIODS=90

# Reporting
REPORTING_TEMP_DIR=/tmp/loki_reports
REPORTING_MAX_FILE_SIZE=52428800  # 50MB
REPORT_SCHEDULE_INTERVAL=60  # seconds

# Export
EXPORT_FORMAT_PDF_ENABLED=true
EXPORT_FORMAT_EXCEL_ENABLED=true
EXPORT_COMPRESSION=gzip
```

---

## Troubleshooting

### Common Issues

1. **Insufficient Data for Analysis**
   - Ensure at least 3 data points for trend analysis
   - Use longer period for anomaly detection
   - Provide historical context for predictions

2. **Inaccurate Predictions**
   - Verify input data quality
   - Check for seasonal patterns
   - Adjust model sensitivity parameters
   - Review external factors

3. **Report Generation Failures**
   - Validate report template exists
   - Check data format compatibility
   - Ensure sufficient disk space for exports
   - Review error logs

4. **Schedule Execution Issues**
   - Verify schedule timing and frequency
   - Check recipient configuration
   - Review execution history
   - Test manually first

---

## Integration with Compliance System

The analytics and reporting engines integrate with:

- **Compliance Modules**: GDPR, CCPA, HIPAA, SOC 2, ISO 27001
- **Scoring Engine**: Compliance scores and metrics
- **Risk Assessment**: Risk levels and findings
- **Audit Trails**: Historical compliance records
- **Database**: Persistent storage of reports and metrics

---

## Performance Metrics

- Trend Analysis: < 100ms for 30-day window
- Prediction Generation: < 200ms per module
- Anomaly Detection: < 150ms for 100 data points
- Report Generation: < 500ms to 2s depending on size
- Export: < 1s for JSON/CSV, 2-5s for PDF

---

## License and Support

For issues, questions, or feature requests:
- Review the ANALYTICS_GUIDE.md (this document)
- Check the module docstrings
- Review example code in this guide
- Contact compliance team

---

## Changelog

### Version 1.0 (Current)
- Complete analytics engine with 6 major components
- Multi-format reporting system
- Advanced scheduling capabilities
- Executive summary generation
- Industry benchmarking
- Dashboard framework
