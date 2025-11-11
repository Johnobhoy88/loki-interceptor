/**
 * Validation Results Component
 * Displays detailed validation results with issues breakdown
 */

import React, { useState } from 'react'
import { AlertCircle, CheckCircle, Info, ChevronDown, ChevronUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { cn, getSeverityColor } from '@/lib/utils'
import type { ValidationResult, ModuleResult, Issue } from '@/types'

interface ValidationResultsProps {
  result: ValidationResult
  onApplyCorrection?: (issueId: string) => void
}

export function ValidationResults({ result, onApplyCorrection }: ValidationResultsProps) {
  return (
    <div className="space-y-4">
      {/* Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Validation Results</span>
            <Badge variant={getStatusVariant(result.status)}>
              {result.status.toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Stat label="Overall Score" value={`${result.overallScore}%`} />
            <Stat label="Total Issues" value={result.totalIssues} />
            <Stat
              label="Critical Issues"
              value={result.criticalIssues}
              highlight={result.criticalIssues > 0}
            />
            <Stat label="Execution Time" value={`${result.executionTime}ms`} />
          </div>
        </CardContent>
      </Card>

      {/* Module Results */}
      <div className="space-y-3">
        {result.moduleResults.map((moduleResult) => (
          <ModuleResultCard
            key={moduleResult.moduleName}
            moduleResult={moduleResult}
            onApplyCorrection={onApplyCorrection}
          />
        ))}
      </div>
    </div>
  )
}

function ModuleResultCard({
  moduleResult,
  onApplyCorrection,
}: {
  moduleResult: ModuleResult
  onApplyCorrection?: (issueId: string) => void
}) {
  const [expanded, setExpanded] = useState(moduleResult.status === 'failed')

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {moduleResult.status === 'passed' ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-600" />
            )}
            <div>
              <CardTitle className="text-base">{moduleResult.moduleDisplayName}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {moduleResult.gatesPassed} / {moduleResult.gatesExecuted} gates passed
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant={getStatusVariant(moduleResult.status)}>
              {moduleResult.score}%
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(!expanded)}
              disabled={moduleResult.issues.length === 0}
            >
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      {expanded && moduleResult.issues.length > 0 && (
        <CardContent className="pt-0">
          <div className="space-y-2">
            {moduleResult.issues.map((issue) => (
              <IssueCard
                key={issue.id}
                issue={issue}
                onApplyCorrection={onApplyCorrection}
              />
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

function IssueCard({
  issue,
  onApplyCorrection,
}: {
  issue: Issue
  onApplyCorrection?: (issueId: string) => void
}) {
  return (
    <div className="rounded-lg border p-4 space-y-2">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant={getSeverityBadgeVariant(issue.severity)}>
              {issue.severity}
            </Badge>
            <span className="text-sm font-medium">{issue.gateName}</span>
          </div>
          <p className="text-sm text-foreground">{issue.message}</p>
          {issue.suggestion && (
            <div className="flex items-start gap-2 mt-2 text-sm text-muted-foreground">
              <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span>{issue.suggestion}</span>
            </div>
          )}
          {issue.location?.context && (
            <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto">
              {issue.location.context}
            </pre>
          )}
        </div>
        {issue.canAutoCorrect && onApplyCorrection && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onApplyCorrection(issue.id)}
          >
            Fix
          </Button>
        )}
      </div>
    </div>
  )
}

function Stat({
  label,
  value,
  highlight = false,
}: {
  label: string
  value: string | number
  highlight?: boolean
}) {
  return (
    <div>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={cn('text-2xl font-bold', highlight && 'text-red-600')}>{value}</p>
    </div>
  )
}

function getStatusVariant(status: string): 'success' | 'warning' | 'destructive' | 'default' {
  switch (status) {
    case 'passed':
      return 'success'
    case 'warning':
      return 'warning'
    case 'failed':
      return 'destructive'
    default:
      return 'default'
  }
}

function getSeverityBadgeVariant(severity: string): 'destructive' | 'warning' | 'info' | 'default' {
  switch (severity) {
    case 'critical':
      return 'destructive'
    case 'high':
      return 'destructive'
    case 'medium':
      return 'warning'
    case 'low':
      return 'info'
    default:
      return 'default'
  }
}
