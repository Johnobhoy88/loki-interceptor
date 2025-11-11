/**
 * Compliance Score Chart
 * Visual representation of compliance scores with Recharts
 */

import React from 'react'
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface ComplianceScoreChartProps {
  score: number
  title?: string
  className?: string
}

export function ComplianceScoreChart({
  score,
  title = 'Compliance Score',
  className,
}: ComplianceScoreChartProps) {
  const data = [{ name: 'Score', value: score, fill: getScoreColor(score) }]

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          <ResponsiveContainer width="100%" height={200}>
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="60%"
              outerRadius="90%"
              data={data}
              startAngle={90}
              endAngle={-270}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
              <RadialBar
                dataKey="value"
                cornerRadius={10}
                background={{ fill: 'hsl(var(--muted))' }}
              />
              <Tooltip
                formatter={(value: number) => [`${value}%`, 'Score']}
                contentStyle={{
                  background: 'hsl(var(--popover))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
              />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className={cn('text-4xl font-bold', getScoreTextColor(score))}>
                {score}%
              </div>
              <div className="text-xs text-muted-foreground mt-1">{getScoreLabel(score)}</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function getScoreColor(score: number): string {
  if (score >= 90) return 'hsl(142 76% 36%)' // Green
  if (score >= 70) return 'hsl(38 92% 50%)' // Yellow
  return 'hsl(0 84% 60%)' // Red
}

function getScoreTextColor(score: number): string {
  if (score >= 90) return 'text-green-600 dark:text-green-400'
  if (score >= 70) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

function getScoreLabel(score: number): string {
  if (score >= 90) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 50) return 'Fair'
  return 'Needs Improvement'
}
