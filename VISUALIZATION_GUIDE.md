# LOKI Compliance Analytics - Visualization Library

## 📊 Overview

This comprehensive visualization library provides stunning, interactive data visualizations for compliance analytics. Built with React, TypeScript, and modern charting libraries, it delivers enterprise-grade visualization components optimized for compliance monitoring, risk analysis, and regulatory reporting.

## 🎯 Features

- **Interactive Charts**: Recharts and D3.js powered visualizations
- **Real-time Updates**: Live data streaming support
- **Responsive Design**: Mobile-friendly, adaptive layouts
- **Accessible**: WCAG AA compliant color schemes
- **Export Functionality**: PNG, SVG, and PDF export
- **TypeScript**: Full type safety and IntelliSense support
- **Performance Optimized**: Handles large datasets efficiently
- **Customizable**: Extensive theming and configuration options

## 📦 Installation

### Prerequisites

```bash
node >= 18.0.0
npm >= 9.0.0
```

### Install Dependencies

```bash
cd frontend
npm install
```

### Key Dependencies

```json
{
  "react": "^18.3.1",
  "recharts": "^2.12.7",
  "d3": "^7.9.0",
  "@visx/visx": "^3.10.2",
  "framer-motion": "^11.2.10",
  "html2canvas": "^1.4.1",
  "jspdf": "^2.5.1"
}
```

## 🚀 Quick Start

### Basic Setup

```tsx
import React from 'react';
import { ComplianceGauge, RiskTrendChart } from '@/components/charts';
import { useRiskTrendData } from '@/hooks/useChartData';

function MyDashboard() {
  const trendData = useRiskTrendData(myData);

  return (
    <div>
      <ComplianceGauge score={92} showGrade />
      <RiskTrendChart data={trendData} height={350} />
    </div>
  );
}
```

### With Export Functionality

```tsx
import { exportToPNG, exportToPDF } from '@/utils/export';
import { useRef } from 'react';

function ExportableChart() {
  const chartRef = useRef<HTMLDivElement>(null);

  const handleExport = async () => {
    if (chartRef.current) {
      await exportToPNG(chartRef.current, {
        filename: 'compliance-report.png'
      });
    }
  };

  return (
    <div>
      <div ref={chartRef}>
        <ComplianceGauge score={85} />
      </div>
      <button onClick={handleExport}>Export Chart</button>
    </div>
  );
}
```

## 📚 Component Library

### Chart Components

#### 1. ComplianceGauge

Interactive gauge chart displaying compliance scores with grade indicators.

**Props:**
```typescript
interface ComplianceGaugeProps {
  score: number;              // 0-100
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showGrade?: boolean;
  showPercentage?: boolean;
  animated?: boolean;
  className?: string;
}
```

**Example:**
```tsx
<ComplianceGauge
  score={92}
  size="lg"
  showGrade={true}
  showPercentage={true}
  animated={true}
/>
```

**Features:**
- Automatic grade calculation (A+, A, B, C, D, F)
- Color-coded risk levels
- Smooth animations
- Responsive sizing

---

#### 2. RiskTrendChart

Area/line chart showing risk trends over time with stacked visualization.

**Props:**
```typescript
interface RiskTrendChartProps {
  data: RiskTrendData[];
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  stacked?: boolean;
  animated?: boolean;
  className?: string;
}

interface RiskTrendData {
  date: string;
  Critical: number;
  High: number;
  Medium: number;
  Low: number;
  total: number;
}
```

**Example:**
```tsx
<RiskTrendChart
  data={trendData}
  height={400}
  showLegend={true}
  stacked={true}
/>
```

**Features:**
- Stacked area visualization
- Custom tooltips
- Interactive legend
- Gradient fills
- Responsive design

---

#### 3. RiskHeatmap

Interactive heatmap visualization for gate failures across modules.

**Props:**
```typescript
interface RiskHeatmapProps {
  data: HeatmapCell[];
  width?: number;
  height?: number;
  cellSize?: number;
  showLabels?: boolean;
  interactive?: boolean;
  onCellClick?: (cell: HeatmapCell) => void;
  className?: string;
}
```

**Example:**
```tsx
<RiskHeatmap
  data={heatmapData}
  width={800}
  height={400}
  interactive={true}
  onCellClick={(cell) => console.log(cell)}
/>
```

**Features:**
- Interactive hover tooltips
- Click handlers
- Color-coded severity
- Responsive grid layout
- Animated entrance

---

#### 4. ModuleRadarChart

Radar chart for comparing module performance across multiple dimensions.

**Props:**
```typescript
interface ModuleRadarChartProps {
  data: RadarChartData[];
  size?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  animated?: boolean;
  fillOpacity?: number;
  className?: string;
}
```

**Example:**
```tsx
<ModuleRadarChart
  data={moduleData}
  size={500}
  fillOpacity={0.6}
/>
```

**Features:**
- Multi-axis comparison
- Customizable opacity
- Polar grid
- Interactive tooltips

---

#### 5. GateStatusPieChart

Pie chart showing gate pass/fail/warning distribution.

**Props:**
```typescript
interface GateStatusPieChartProps {
  data: GateStatusData[];
  size?: number;
  innerRadius?: number;
  showLegend?: boolean;
  showLabels?: boolean;
  animated?: boolean;
  className?: string;
}
```

**Example:**
```tsx
<GateStatusPieChart
  data={gateStatus}
  size={300}
  innerRadius={60}
  showLabels={true}
/>
```

**Features:**
- Donut chart variant
- Percentage labels
- Interactive tooltips
- Status color-coding

---

### Dashboard Widgets

#### 1. StatCard

KPI display card with trend indicators and icons.

**Props:**
```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: number;
    label?: string;
  };
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  animated?: boolean;
  className?: string;
}
```

**Example:**
```tsx
<StatCard
  title="Total Validations"
  value={1248}
  subtitle="Last 30 days"
  trend={{ direction: 'up', value: 12.5 }}
  icon={<BarChart3 />}
  color="primary"
/>
```

**Features:**
- Trend indicators
- Custom icons
- Color themes
- Hover animations

---

#### 2. ProgressIndicator

Animated progress bar with milestone markers.

**Props:**
```typescript
interface ProgressIndicatorProps {
  label: string;
  current: number;
  total: number;
  showPercentage?: boolean;
  showValues?: boolean;
  color?: string;
  height?: number;
  animated?: boolean;
  milestones?: Array<{
    value: number;
    label: string;
  }>;
  className?: string;
}
```

**Example:**
```tsx
<ProgressIndicator
  label="GDPR Compliance"
  current={92}
  total={100}
  color="#10b981"
  milestones={[
    { value: 50, label: 'Baseline' },
    { value: 75, label: 'Target' }
  ]}
/>
```

**Features:**
- Smooth animations
- Milestone markers
- Customizable colors
- Value labels

---

### Visualization Components

#### 1. ComplianceTimeline

Interactive timeline for validation and correction events.

**Props:**
```typescript
interface ComplianceTimelineProps {
  events: TimelineEvent[];
  maxEvents?: number;
  orientation?: 'vertical' | 'horizontal';
  animated?: boolean;
  onEventClick?: (event: TimelineEvent) => void;
  className?: string;
}
```

**Example:**
```tsx
<ComplianceTimeline
  events={timelineEvents}
  orientation="vertical"
  animated={true}
  onEventClick={(event) => handleEventClick(event)}
/>
```

**Features:**
- Vertical/horizontal layouts
- Event type icons
- Risk color-coding
- Interactive cards
- Metadata display

---

## 🎨 Theming & Customization

### Color Configuration

```typescript
import { RISK_COLORS, GRADIENT_COLORS } from '@/utils/chart-config';

// Risk level colors
RISK_COLORS = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#10b981',
  NONE: '#6b7280',
};

// Gradient presets
GRADIENT_COLORS = {
  primary: ['#667eea', '#764ba2'],
  success: ['#10b981', '#059669'],
  warning: ['#f59e0b', '#d97706'],
  danger: ['#ef4444', '#dc2626'],
  info: ['#3b82f6', '#2563eb'],
};
```

### Custom Theme

```typescript
import chartConfig from '@/utils/chart-config';

// Override default colors
const customTheme = {
  ...chartConfig,
  RISK_COLORS: {
    ...chartConfig.RISK_COLORS,
    LOW: '#00ff00',  // Custom green
  },
};
```

### Accessible Colors

```typescript
import { ACCESSIBLE_COLORS } from '@/utils/chart-config';

// WCAG AA compliant palette
const accessibleChart = (
  <MyChart colors={ACCESSIBLE_COLORS} />
);
```

---

## 🔧 Data Transformation Hooks

### useRiskTrendData

Transform risk trends for visualization.

```typescript
import { useRiskTrendData } from '@/hooks/useChartData';

const transformedData = useRiskTrendData(apiTrends);
// Returns: { date, Critical, High, Medium, Low, total }[]
```

### useComplianceScore

Calculate compliance score and grade.

```typescript
import { useComplianceScore } from '@/hooks/useChartData';

const score = useComplianceScore(validationResult);
// Returns: { overall_score, module_scores, grade, benchmark_comparison }
```

### useHeatmapData

Transform validation results to heatmap format.

```typescript
import { useHeatmapData } from '@/hooks/useChartData';

const heatmapCells = useHeatmapData(validationResult);
// Returns: HeatmapCell[]
```

### useModuleRadarData

Prepare module stats for radar chart.

```typescript
import { useModuleRadarData } from '@/hooks/useChartData';

const radarData = useModuleRadarData(moduleStats);
// Returns: { module, score, fullMark }[]
```

---

## 📤 Export Functionality

### Export to PNG

```typescript
import { exportToPNG } from '@/utils/export';

await exportToPNG(element, {
  filename: 'chart.png',
  quality: 1.0,
  width: 1920,
  height: 1080,
  includeBackground: true,
});
```

### Export to SVG

```typescript
import { exportToSVG } from '@/utils/export';

await exportToSVG(element, {
  filename: 'chart.svg',
  includeBackground: true,
});
```

### Export to PDF

```typescript
import { exportToPDF } from '@/utils/export';

await exportToPDF(element, {
  filename: 'report.pdf',
  quality: 0.95,
});
```

### Export Multiple Charts

```typescript
import { exportMultipleChartsToPDF } from '@/utils/export';

await exportMultipleChartsToPDF(
  [element1, element2, element3],
  {
    filename: 'compliance-report.pdf',
    title: 'Monthly Compliance Report',
    description: 'November 2025 Analytics',
  }
);
```

### Copy to Clipboard

```typescript
import { copyToClipboard } from '@/utils/export';

await copyToClipboard(element, {
  includeBackground: true,
});
```

### Export Data to CSV/JSON

```typescript
import { exportToCSV, exportToJSON } from '@/utils/export';

// Export to CSV
exportToCSV(data, 'compliance-data.csv');

// Export to JSON
exportToJSON(data, 'compliance-data.json');
```

---

## 🎬 Animation Configuration

### Global Animation Settings

```typescript
import { ANIMATION_CONFIG } from '@/utils/chart-config';

ANIMATION_CONFIG = {
  duration: 750,
  easing: 'ease-in-out',
  delay: 0,
  stagger: 50,
};
```

### Disable Animations

```tsx
<ComplianceGauge
  score={85}
  animated={false}  // Disable animations
/>
```

---

## 📱 Responsive Design

### Breakpoint Handling

```tsx
import { CHART_DIMENSIONS } from '@/utils/chart-config';

const ResponsiveChart = () => {
  const isMobile = window.innerWidth < 768;
  const size = isMobile ? 'sm' : 'lg';

  return <ComplianceGauge size={size} score={92} />;
};
```

### Responsive Container

```tsx
<div className="w-full h-96">
  <ResponsiveContainer width="100%" height="100%">
    <MyChart data={data} />
  </ResponsiveContainer>
</div>
```

---

## 🔍 Advanced Examples

### Real-time Dashboard

```tsx
import { useEffect, useState } from 'react';
import { RiskTrendChart } from '@/components/charts';

function RealtimeDashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const newData = await fetchLatestData();
      setData(prev => [...prev.slice(-6), newData]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return <RiskTrendChart data={data} animated={true} />;
}
```

### Interactive Drill-down

```tsx
function DrilldownHeatmap() {
  const [selectedCell, setSelectedCell] = useState(null);

  return (
    <>
      <RiskHeatmap
        data={heatmapData}
        onCellClick={(cell) => setSelectedCell(cell)}
        interactive={true}
      />
      {selectedCell && (
        <DetailPanel cell={selectedCell} />
      )}
    </>
  );
}
```

### Custom Tooltip

```tsx
const CustomTooltip = ({ active, payload }) => {
  if (active && payload) {
    return (
      <div className="bg-white p-4 rounded shadow-lg">
        <h4>{payload[0].payload.label}</h4>
        <p>Value: {payload[0].value}</p>
      </div>
    );
  }
  return null;
};

<RiskTrendChart
  data={data}
  customTooltip={CustomTooltip}
/>
```

---

## 🧪 Testing

### Component Testing

```typescript
import { render } from '@testing-library/react';
import { ComplianceGauge } from '@/components/charts';

test('renders compliance gauge', () => {
  const { getByText } = render(<ComplianceGauge score={92} />);
  expect(getByText('92')).toBeInTheDocument();
});
```

### Export Testing

```typescript
import { exportToPNG } from '@/utils/export';

test('exports chart to PNG', async () => {
  const element = document.createElement('div');
  await expect(exportToPNG(element)).resolves.not.toThrow();
});
```

---

## 🚀 Performance Optimization

### Memoization

```tsx
import { useMemo } from 'react';
import { useRiskTrendData } from '@/hooks/useChartData';

const OptimizedChart = ({ rawData }) => {
  const processedData = useMemo(
    () => useRiskTrendData(rawData),
    [rawData]
  );

  return <RiskTrendChart data={processedData} />;
};
```

### Lazy Loading

```tsx
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('@/components/charts/HeavyChart'));

function LazyDashboard() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyChart data={largeDataset} />
    </Suspense>
  );
}
```

### Virtualization

For large datasets, use virtualization:

```tsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={100}
    >
      {({ index, style }) => (
        <div style={style}>
          <ComplianceCard data={items[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

---

## 📖 API Reference

### Chart Configuration

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RISK_COLORS` | `Record<RiskLevel, string>` | - | Risk level color mapping |
| `CHART_DIMENSIONS` | `Record<string, Dimensions>` | - | Preset chart sizes |
| `ANIMATION_CONFIG` | `AnimationConfig` | - | Animation settings |
| `TOOLTIP_CONFIG` | `TooltipConfig` | - | Tooltip styling |

### Type Definitions

```typescript
// Risk Levels
enum RiskLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
  NONE = 'NONE',
}

// Chart Data Point
interface ChartDataPoint {
  x: string | number;
  y: number;
  label?: string;
  color?: string;
  metadata?: Record<string, any>;
}

// Export Options
interface ExportOptions {
  format: 'png' | 'svg' | 'pdf';
  filename?: string;
  quality?: number;
  width?: number;
  height?: number;
  includeBackground?: boolean;
}
```

---

## 🐛 Troubleshooting

### Common Issues

**Charts not rendering:**
```bash
# Ensure all dependencies are installed
npm install

# Clear cache and rebuild
npm run build
```

**Export not working:**
```typescript
// Check browser permissions for clipboard access
if (!navigator.clipboard) {
  console.error('Clipboard API not available');
}
```

**Performance issues:**
- Reduce animation duration
- Implement data pagination
- Use React.memo for heavy components
- Consider virtualization for large lists

**Type errors:**
```bash
# Run type check
npm run type-check
```

---

## 📝 Best Practices

1. **Always use TypeScript** for type safety
2. **Memoize expensive computations** with useMemo
3. **Provide fallback data** for loading states
4. **Use accessible colors** (WCAG AA compliant)
5. **Test responsive behavior** on mobile devices
6. **Handle errors gracefully** with error boundaries
7. **Optimize images** before exporting
8. **Document custom components** with JSDoc
9. **Use semantic HTML** for accessibility
10. **Monitor performance** with React DevTools

---

## 🔗 Resources

- [Recharts Documentation](https://recharts.org/)
- [D3.js Documentation](https://d3js.org/)
- [Framer Motion](https://www.framer.com/motion/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Best Practices](https://react.dev/learn)

---

## 📄 License

This visualization library is part of the LOKI Compliance Platform.
© 2025 LOKI Interceptor. All rights reserved.

---

## 🤝 Support

For questions, issues, or feature requests:
- GitHub Issues: [github.com/loki-interceptor/issues]
- Email: support@loki-compliance.com
- Documentation: [docs.loki-compliance.com]

---

## 🎓 Examples Gallery

Visit `/frontend/src/pages/DashboardExample.tsx` for a comprehensive example showcasing all components with interactive features, export functionality, and real-world use cases.

**Run the example:**
```bash
npm run dev
# Navigate to http://localhost:3000/examples
```

---

**Last Updated:** November 11, 2025
**Version:** 1.0.0
**Contributors:** LOKI Development Team
