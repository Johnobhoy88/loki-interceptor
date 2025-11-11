/**
 * Data Transformation Hooks for Charts
 * Custom React hooks for transforming API data into chart-ready formats
 */

import { useMemo } from 'react';
import { format, parseISO, subDays } from 'date-fns';
import type {
  ValidationResult,
  RiskTrend,
  ModuleStats,
  AnalyticsOverview,
  ChartDataPoint,
  RadarChartData,
  HeatmapCell,
  RiskLevel,
} from '@/types';

/**
 * Transform risk trends data for line/area charts
 */
export const useRiskTrendData = (trends: RiskTrend[] = []) => {
  return useMemo(() => {
    return trends.map((trend) => ({
      date: format(parseISO(trend.date), 'MMM dd'),
      Critical: trend.critical_count,
      High: trend.high_count,
      Medium: trend.medium_count,
      Low: trend.low_count,
      total: trend.total,
    }));
  }, [trends]);
};

/**
 * Transform module stats for radar chart
 */
export const useModuleRadarData = (modules: ModuleStats[] = []) => {
  return useMemo(() => {
    return modules.map((mod) => ({
      module: mod.module_name.replace('UK', '').trim(),
      score: Math.round((1 - mod.failure_rate) * 100),
      fullMark: 100,
    }));
  }, [modules]);
};

/**
 * Transform validation result into heatmap data
 */
export const useHeatmapData = (validation: ValidationResult | null) => {
  return useMemo(() => {
    if (!validation) return [];

    const cells: HeatmapCell[] = [];
    validation.modules.forEach((module) => {
      module.gates.forEach((gate) => {
        cells.push({
          module_id: module.module_id,
          gate_id: gate.gate_id,
          value: gate.passed ? 0 : gate.severity === 'CRITICAL' ? 3 : gate.severity === 'ERROR' ? 2 : 1,
          label: gate.gate_name,
        });
      });
    });
    return cells;
  }, [validation]);
};

/**
 * Calculate compliance score from validation result
 */
export const useComplianceScore = (validation: ValidationResult | null) => {
  return useMemo(() => {
    if (!validation || validation.total_gates_checked === 0) {
      return {
        overall_score: 0,
        module_scores: {},
        grade: 'F' as const,
        benchmark_comparison: 0,
      };
    }

    const passedGates = validation.total_gates_checked - validation.total_gates_failed;
    const overall_score = (passedGates / validation.total_gates_checked) * 100;

    const module_scores: Record<string, number> = {};
    validation.modules.forEach((module) => {
      if (module.gates_checked > 0) {
        module_scores[module.module_id] = (module.gates_passed / module.gates_checked) * 100;
      }
    });

    // Calculate grade
    let grade: 'A+' | 'A' | 'B' | 'C' | 'D' | 'F' = 'F';
    if (overall_score >= 97) grade = 'A+';
    else if (overall_score >= 90) grade = 'A';
    else if (overall_score >= 80) grade = 'B';
    else if (overall_score >= 70) grade = 'C';
    else if (overall_score >= 60) grade = 'D';

    // Benchmark comparison (mock - would come from API)
    const benchmark_comparison = overall_score - 75; // Compare to 75% industry average

    return {
      overall_score: Math.round(overall_score),
      module_scores,
      grade,
      benchmark_comparison: Math.round(benchmark_comparison),
    };
  }, [validation]);
};

/**
 * Transform module stats for bar chart comparison
 */
export const useModuleComparisonData = (modules: ModuleStats[] = []) => {
  return useMemo(() => {
    return modules.map((mod) => ({
      name: mod.module_name.replace(' Compliance', '').replace(' UK', ''),
      failures: mod.total_failures,
      failureRate: Math.round(mod.failure_rate * 100),
      avgTime: Math.round(mod.average_execution_time_ms),
    }));
  }, [modules]);
};

/**
 * Transform risk distribution for pie chart
 */
export const useRiskDistribution = (riskDist: Record<string, number> = {}) => {
  return useMemo(() => {
    return Object.entries(riskDist).map(([risk, count]) => ({
      name: risk,
      value: count,
      percentage: 0, // Will be calculated by chart component
    }));
  }, [riskDist]);
};

/**
 * Calculate gate status breakdown for pie chart
 */
export const useGateStatusBreakdown = (validation: ValidationResult | null) => {
  return useMemo(() => {
    if (!validation) return [];

    const statusCount: Record<string, number> = {
      Pass: 0,
      Fail: 0,
      Warning: 0,
      Skip: 0,
    };

    validation.modules.forEach((module) => {
      module.gates.forEach((gate) => {
        if (gate.passed) {
          statusCount.Pass++;
        } else if (gate.severity === 'WARNING') {
          statusCount.Warning++;
        } else if (gate.status === 'SKIP') {
          statusCount.Skip++;
        } else {
          statusCount.Fail++;
        }
      });
    });

    return Object.entries(statusCount)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => ({
        name: status,
        value: count,
      }));
  }, [validation]);
};

/**
 * Calculate time series data for validation progress
 */
export const useValidationProgress = (days: number = 7) => {
  return useMemo(() => {
    // Mock data - would come from API
    const data = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = subDays(new Date(), i);
      data.push({
        date: format(date, 'MMM dd'),
        validations: Math.floor(Math.random() * 50) + 20,
        corrections: Math.floor(Math.random() * 30) + 10,
      });
    }
    return data;
  }, [days]);
};

/**
 * Transform module performance over time
 */
export const useModulePerformanceTrend = (moduleId: string, trends: RiskTrend[] = []) => {
  return useMemo(() => {
    return trends.map((trend) => ({
      date: format(parseISO(trend.date), 'MMM dd'),
      performance: 100 - ((trend.high_count + trend.critical_count) / trend.total) * 100,
    }));
  }, [moduleId, trends]);
};

/**
 * Calculate top failing gates from analytics
 */
export const useTopFailingGates = (analytics: AnalyticsOverview | null, limit: number = 10) => {
  return useMemo(() => {
    if (!analytics || !analytics.top_failing_gates) return [];

    return analytics.top_failing_gates.slice(0, limit).map((gate) => ({
      name: gate.gate_name,
      module: gate.module_id,
      failures: gate.failure_count,
    }));
  }, [analytics, limit]);
};

/**
 * Calculate correction impact metrics
 */
export const useCorrectionImpact = (
  originalValidation: ValidationResult | null,
  correctedValidation: ValidationResult | null
) => {
  return useMemo(() => {
    if (!originalValidation || !correctedValidation) {
      return {
        gates_fixed: 0,
        risk_improvement: 0,
        score_improvement: 0,
      };
    }

    const originalFailed = originalValidation.total_gates_failed;
    const correctedFailed = correctedValidation.total_gates_failed;
    const gates_fixed = originalFailed - correctedFailed;

    const riskLevels: Record<RiskLevel, number> = {
      CRITICAL: 4,
      HIGH: 3,
      MEDIUM: 2,
      LOW: 1,
      NONE: 0,
    };

    const originalRiskValue = riskLevels[originalValidation.overall_risk];
    const correctedRiskValue = riskLevels[correctedValidation.overall_risk];
    const risk_improvement = originalRiskValue - correctedRiskValue;

    const originalScore =
      ((originalValidation.total_gates_checked - originalFailed) / originalValidation.total_gates_checked) * 100;
    const correctedScore =
      ((correctedValidation.total_gates_checked - correctedFailed) / correctedValidation.total_gates_checked) * 100;
    const score_improvement = correctedScore - originalScore;

    return {
      gates_fixed,
      risk_improvement,
      score_improvement: Math.round(score_improvement),
    };
  }, [originalValidation, correctedValidation]);
};

/**
 * Generate compliance roadmap data
 */
export const useComplianceRoadmap = (validation: ValidationResult | null) => {
  return useMemo(() => {
    if (!validation) return [];

    const milestones = [];
    const now = new Date();

    // Current state
    milestones.push({
      id: 'current',
      title: 'Current State',
      date: format(now, 'MMM dd, yyyy'),
      status: 'completed',
      score: ((validation.total_gates_checked - validation.total_gates_failed) / validation.total_gates_checked) * 100,
    });

    // Add milestones based on failures
    if (validation.total_gates_failed > 0) {
      milestones.push({
        id: 'critical-fixes',
        title: 'Address Critical Issues',
        date: format(subDays(now, -7), 'MMM dd, yyyy'),
        status: 'pending',
        score: 70,
      });

      milestones.push({
        id: 'high-fixes',
        title: 'Resolve High Priority',
        date: format(subDays(now, -14), 'MMM dd, yyyy'),
        status: 'pending',
        score: 85,
      });

      milestones.push({
        id: 'full-compliance',
        title: 'Full Compliance',
        date: format(subDays(now, -30), 'MMM dd, yyyy'),
        status: 'pending',
        score: 100,
      });
    }

    return milestones;
  }, [validation]);
};

/**
 * Format benchmark comparison data
 */
export const useBenchmarkData = (analytics: AnalyticsOverview | null) => {
  return useMemo(() => {
    if (!analytics) return [];

    // Mock benchmark data - would come from API
    return [
      {
        metric: 'Overall Compliance',
        your_value: 82,
        industry_avg: 75,
        percentile: 68,
        trend: 'improving' as const,
      },
      {
        metric: 'Validation Speed',
        your_value: 234,
        industry_avg: 450,
        percentile: 85,
        trend: 'improving' as const,
      },
      {
        metric: 'Gate Pass Rate',
        your_value: 88,
        industry_avg: 82,
        percentile: 72,
        trend: 'stable' as const,
      },
      {
        metric: 'Correction Rate',
        your_value: 65,
        industry_avg: 58,
        percentile: 62,
        trend: 'improving' as const,
      },
    ];
  }, [analytics]);
};

export default {
  useRiskTrendData,
  useModuleRadarData,
  useHeatmapData,
  useComplianceScore,
  useModuleComparisonData,
  useRiskDistribution,
  useGateStatusBreakdown,
  useValidationProgress,
  useModulePerformanceTrend,
  useTopFailingGates,
  useCorrectionImpact,
  useComplianceRoadmap,
  useBenchmarkData,
};
