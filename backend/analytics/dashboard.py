"""
Analytics Dashboard
Provides unified compliance analytics and reporting dashboard.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetric:
    """Individual dashboard metric"""
    name: str
    value: float
    target: float
    trend: str  # 'up', 'down', 'stable'
    threshold: float
    status: str  # 'healthy', 'warning', 'critical'
    last_updated: datetime


@dataclass
class DashboardWidget:
    """Dashboard widget for visualization"""
    widget_id: str
    title: str
    widget_type: str  # 'gauge', 'line_chart', 'bar_chart', 'table', 'heatmap'
    metrics: List[DashboardMetric]
    data: Dict[str, Any]
    layout_position: Dict[str, int]  # x, y, width, height


@dataclass
class AnalyticsDashboardConfig:
    """Dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    organization: str
    created_date: datetime
    last_modified: datetime
    widgets: List[DashboardWidget] = field(default_factory=list)
    refresh_interval: int = 300  # seconds
    filters: Dict[str, Any] = field(default_factory=dict)


class AnalyticsDashboard:
    """
    Comprehensive analytics dashboard.

    Features:
    - Real-time metric tracking
    - Customizable widgets
    - Drag-and-drop layout
    - Multiple dashboard profiles
    - Export capabilities
    - Alert integration
    """

    def __init__(self):
        """Initialize analytics dashboard."""
        self.dashboards: Dict[str, AnalyticsDashboardConfig] = {}
        self.default_dashboard = self._create_default_dashboard()

    def _create_default_dashboard(self) -> AnalyticsDashboardConfig:
        """Create default compliance dashboard."""
        dashboard = AnalyticsDashboardConfig(
            dashboard_id="default_compliance",
            name="Compliance Overview",
            description="Main compliance metrics and KPIs",
            organization="Enterprise",
            created_date=datetime.now(),
            last_modified=datetime.now(),
        )

        # Add default widgets
        widgets = [
            self._create_compliance_score_widget(),
            self._create_trend_widget(),
            self._create_module_comparison_widget(),
            self._create_risk_heatmap_widget(),
            self._create_alerts_widget(),
            self._create_forecast_widget(),
        ]

        dashboard.widgets = widgets
        return dashboard

    def _create_compliance_score_widget(self) -> DashboardWidget:
        """Create overall compliance score widget."""
        metrics = [
            DashboardMetric(
                name="Overall Compliance Score",
                value=78.5,
                target=90,
                trend="up",
                threshold=70,
                status="warning",
                last_updated=datetime.now()
            )
        ]

        return DashboardWidget(
            widget_id="compliance_score",
            title="Overall Compliance Score",
            widget_type="gauge",
            metrics=metrics,
            data={
                'min': 0,
                'max': 100,
                'segments': [
                    {'min': 0, 'max': 50, 'color': '#d32f2f', 'label': 'Critical'},
                    {'min': 50, 'max': 70, 'color': '#f57c00', 'label': 'Warning'},
                    {'min': 70, 'max': 85, 'color': '#fbc02d', 'label': 'Caution'},
                    {'min': 85, 'max': 100, 'color': '#388e3c', 'label': 'Healthy'},
                ]
            },
            layout_position={'x': 0, 'y': 0, 'width': 4, 'height': 3}
        )

    def _create_trend_widget(self) -> DashboardWidget:
        """Create trend chart widget."""
        metrics = []

        # Generate sample trend data
        now = datetime.now()
        trend_data = []
        for i in range(30):
            date = now - timedelta(days=30 - i)
            value = 70 + (i * 0.3) + (5 if i % 5 == 0 else 0)
            value = min(100, max(0, value))
            trend_data.append({'date': date.isoformat(), 'value': value})

        return DashboardWidget(
            widget_id="trend_chart",
            title="30-Day Compliance Trend",
            widget_type="line_chart",
            metrics=metrics,
            data={'series': trend_data},
            layout_position={'x': 4, 'y': 0, 'width': 5, 'height': 3}
        )

    def _create_module_comparison_widget(self) -> DashboardWidget:
        """Create module comparison widget."""
        modules_data = [
            {'name': 'GDPR', 'score': 85, 'target': 90},
            {'name': 'CCPA', 'score': 78, 'target': 85},
            {'name': 'HIPAA', 'score': 82, 'target': 95},
            {'name': 'SOC 2', 'score': 80, 'target': 90},
        ]

        return DashboardWidget(
            widget_id="module_comparison",
            title="Module Compliance Scores",
            widget_type="bar_chart",
            metrics=[],
            data={'modules': modules_data},
            layout_position={'x': 0, 'y': 3, 'width': 4, 'height': 3}
        )

    def _create_risk_heatmap_widget(self) -> DashboardWidget:
        """Create risk heatmap widget."""
        heatmap_data = {
            'rows': ['GDPR', 'CCPA', 'HIPAA', 'SOC2', 'ISO27001'],
            'columns': ['Data Access', 'Storage', 'Transmission', 'Retention'],
            'values': [
                [2, 1, 2, 3],
                [1, 2, 1, 2],
                [3, 3, 2, 3],
                [1, 1, 1, 1],
                [2, 2, 2, 2],
            ]
        }

        return DashboardWidget(
            widget_id="risk_heatmap",
            title="Risk Heatmap",
            widget_type="heatmap",
            metrics=[],
            data=heatmap_data,
            layout_position={'x': 4, 'y': 3, 'width': 5, 'height': 3}
        )

    def _create_alerts_widget(self) -> DashboardWidget:
        """Create alerts widget."""
        alerts = [
            {
                'severity': 'critical',
                'message': 'GDPR compliance score declining',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'module': 'GDPR'
            },
            {
                'severity': 'warning',
                'message': 'Anomaly detected in data retention metrics',
                'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
                'module': 'Data Management'
            },
            {
                'severity': 'info',
                'message': 'HIPAA audit scheduled next month',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'module': 'HIPAA'
            },
        ]

        return DashboardWidget(
            widget_id="alerts",
            title="Recent Alerts",
            widget_type="table",
            metrics=[],
            data={'alerts': alerts},
            layout_position={'x': 0, 'y': 6, 'width': 4, 'height': 3}
        )

    def _create_forecast_widget(self) -> DashboardWidget:
        """Create forecast widget."""
        forecast_data = []
        now = datetime.now()

        for i in range(30):
            date = now + timedelta(days=i)
            # Simple forecast
            forecast_value = 78.5 + (i * 0.2)
            forecast_value = min(100, max(0, forecast_value))
            forecast_data.append({
                'date': date.isoformat(),
                'predicted': forecast_value,
                'lower_bound': forecast_value - 5,
                'upper_bound': forecast_value + 5,
            })

        return DashboardWidget(
            widget_id="forecast",
            title="30-Day Forecast",
            widget_type="line_chart",
            metrics=[],
            data={'forecast': forecast_data},
            layout_position={'x': 4, 'y': 6, 'width': 5, 'height': 3}
        )

    def create_custom_dashboard(
        self,
        dashboard_id: str,
        name: str,
        description: str,
        organization: str,
        widgets: Optional[List[str]] = None
    ) -> AnalyticsDashboardConfig:
        """
        Create a custom dashboard configuration.

        Args:
            dashboard_id: Unique dashboard identifier
            name: Dashboard name
            description: Dashboard description
            organization: Organization name
            widgets: Optional list of widget IDs to include

        Returns:
            AnalyticsDashboardConfig
        """
        dashboard = AnalyticsDashboardConfig(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            organization=organization,
            created_date=datetime.now(),
            last_modified=datetime.now(),
        )

        if widgets:
            # Add selected widgets from defaults
            for widget_id in widgets:
                widget = self._get_widget_by_id(widget_id)
                if widget:
                    dashboard.widgets.append(widget)

        self.dashboards[dashboard_id] = dashboard
        return dashboard

    def _get_widget_by_id(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get default widget by ID."""
        widget_builders = {
            'compliance_score': self._create_compliance_score_widget,
            'trend': self._create_trend_widget,
            'module_comparison': self._create_module_comparison_widget,
            'risk_heatmap': self._create_risk_heatmap_widget,
            'alerts': self._create_alerts_widget,
            'forecast': self._create_forecast_widget,
        }

        builder = widget_builders.get(widget_id)
        return builder() if builder else None

    def add_widget(
        self,
        dashboard_id: str,
        widget: DashboardWidget
    ) -> bool:
        """Add widget to dashboard."""
        if dashboard_id not in self.dashboards:
            return False

        self.dashboards[dashboard_id].widgets.append(widget)
        self.dashboards[dashboard_id].last_modified = datetime.now()
        return True

    def remove_widget(
        self,
        dashboard_id: str,
        widget_id: str
    ) -> bool:
        """Remove widget from dashboard."""
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]
        original_count = len(dashboard.widgets)
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]

        if len(dashboard.widgets) < original_count:
            dashboard.last_modified = datetime.now()
            return True

        return False

    def update_dashboard_layout(
        self,
        dashboard_id: str,
        widget_layouts: Dict[str, Dict[str, int]]
    ) -> bool:
        """
        Update dashboard widget layouts.

        Args:
            dashboard_id: Dashboard to update
            widget_layouts: Dict of widget_id to layout position

        Returns:
            Success status
        """
        if dashboard_id not in self.dashboards:
            return False

        dashboard = self.dashboards[dashboard_id]

        for widget in dashboard.widgets:
            if widget.widget_id in widget_layouts:
                widget.layout_position = widget_layouts[widget.widget_id]

        dashboard.last_modified = datetime.now()
        return True

    def get_dashboard(self, dashboard_id: str) -> Optional[AnalyticsDashboardConfig]:
        """Retrieve dashboard configuration."""
        return self.dashboards.get(dashboard_id, self.default_dashboard)

    def list_dashboards(self) -> List[Dict[str, str]]:
        """List all available dashboards."""
        return [
            {
                'id': d.dashboard_id,
                'name': d.name,
                'organization': d.organization,
                'modified': d.last_modified.isoformat(),
            }
            for d in self.dashboards.values()
        ]

    def export_dashboard_data(
        self,
        dashboard_id: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Export dashboard data in specified format.

        Args:
            dashboard_id: Dashboard to export
            format: Export format (json, csv, pdf)

        Returns:
            Exported data
        """
        dashboard = self.get_dashboard(dashboard_id)

        if format == 'json':
            return {
                'dashboard_id': dashboard.dashboard_id,
                'name': dashboard.name,
                'widgets': [
                    {
                        'id': w.widget_id,
                        'title': w.title,
                        'type': w.widget_type,
                        'data': w.data,
                    }
                    for w in dashboard.widgets
                ]
            }

        return {}
