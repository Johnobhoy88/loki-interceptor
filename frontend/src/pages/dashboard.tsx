/**
 * Dashboard Page
 * Main overview page with statistics and recent activity
 */

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Activity, FileCheck, AlertCircle, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ComplianceScoreChart } from '@/components/features/compliance-score-chart'
import { statsService } from '@/services/stats-service'
import { formatNumber, formatPercentage } from '@/lib/utils'

export function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['system-stats'],
    queryFn: () => statsService.getSystemStats(),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const overview = stats?.overview

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your compliance validation activity
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Validations"
          value={formatNumber(overview?.totalValidations || 0)}
          icon={<FileCheck className="h-4 w-4 text-muted-foreground" />}
          description="All time validations"
        />
        <StatCard
          title="Pass Rate"
          value={formatPercentage(overview?.passRate || 0)}
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
          description="Successful validations"
        />
        <StatCard
          title="Average Score"
          value={formatPercentage(overview?.averageScore || 0)}
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          description="Average compliance score"
        />
        <StatCard
          title="Issues Resolved"
          value={formatNumber(overview?.criticalIssuesResolved || 0)}
          icon={<AlertCircle className="h-4 w-4 text-muted-foreground" />}
          description="Critical issues fixed"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {overview && <ComplianceScoreChart score={overview.averageScore} />}

        {/* Top Issues */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Top Issues</CardTitle>
            <CardDescription>Most common compliance issues</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats?.topIssues.slice(0, 5).map((issue, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium">{issue.gateName}</p>
                    <p className="text-xs text-muted-foreground">{issue.moduleName}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">{issue.count}</span>
                    <span className="text-xs text-muted-foreground">
                      {issue.severity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest validation and correction operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {stats?.recentActivity.slice(0, 10).map((activity) => (
              <div key={activity.id} className="flex items-center gap-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    activity.status === 'success'
                      ? 'bg-green-600'
                      : activity.status === 'error'
                        ? 'bg-red-600'
                        : 'bg-yellow-600'
                  }`}
                />
                <div className="flex-1">
                  <p className="text-sm">{activity.description}</p>
                  <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon,
  description,
}: {
  title: string
  value: string
  icon: React.ReactNode
  description: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}
