/**
 * LOKI Interceptor - Type Definitions
 * Comprehensive TypeScript types for the compliance validation platform
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// ============================================================================
// Validation Types
// ============================================================================

export interface ValidationRequest {
  content: string
  modules?: string[]
  options?: ValidationOptions
}

export interface ValidationOptions {
  severity?: 'critical' | 'high' | 'medium' | 'low'
  autoCorrect?: boolean
  includeExplanations?: boolean
  industryContext?: string
}

export interface ValidationResult {
  id: string
  timestamp: string
  overallScore: number
  status: 'passed' | 'failed' | 'warning'
  totalIssues: number
  criticalIssues: number
  moduleResults: ModuleResult[]
  correctionSuggestions?: CorrectionSuggestion[]
  executionTime: number
  metadata?: Record<string, unknown>
}

export interface ModuleResult {
  moduleName: string
  moduleDisplayName: string
  score: number
  status: 'passed' | 'failed' | 'warning'
  issues: Issue[]
  gatesExecuted: number
  gatesPassed: number
  gatesFailed: number
}

export interface Issue {
  id: string
  gateId: string
  gateName: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  message: string
  location?: IssueLocation
  suggestion?: string
  explanation?: string
  ruleReference?: string
  canAutoCorrect: boolean
}

export interface IssueLocation {
  line?: number
  column?: number
  startOffset?: number
  endOffset?: number
  context?: string
}

export interface CorrectionSuggestion {
  issueId: string
  type: 'replace' | 'insert' | 'delete' | 'restructure'
  original: string
  corrected: string
  confidence: number
  explanation: string
  riskLevel: 'low' | 'medium' | 'high'
}

// ============================================================================
// Correction Types
// ============================================================================

export interface CorrectionRequest {
  validationId: string
  issueIds?: string[]
  reviewRequired?: boolean
}

export interface CorrectionResult {
  id: string
  validationId: string
  timestamp: string
  originalContent: string
  correctedContent: string
  appliedCorrections: AppliedCorrection[]
  diffPreview: DiffPreview
  requiresReview: boolean
  confidence: number
}

export interface AppliedCorrection {
  issueId: string
  type: string
  location: IssueLocation
  original: string
  corrected: string
  confidence: number
}

export interface DiffPreview {
  additions: number
  deletions: number
  modifications: number
  hunks: DiffHunk[]
}

export interface DiffHunk {
  oldStart: number
  oldLines: number
  newStart: number
  newLines: number
  lines: DiffLine[]
}

export interface DiffLine {
  type: 'add' | 'delete' | 'context'
  content: string
  lineNumber: number
}

// ============================================================================
// Module Types
// ============================================================================

export interface ComplianceModule {
  id: string
  name: string
  displayName: string
  description: string
  version: string
  category: 'gdpr' | 'employment' | 'financial' | 'tax' | 'legal' | 'industry'
  jurisdiction: string
  enabled: boolean
  gates: ComplianceGate[]
  statistics?: ModuleStatistics
  lastUpdated: string
}

export interface ComplianceGate {
  id: string
  name: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  enabled: boolean
  ruleReference?: string
  examples?: string[]
}

export interface ModuleStatistics {
  totalExecutions: number
  passRate: number
  averageScore: number
  commonIssues: string[]
  lastUsed?: string
}

// ============================================================================
// History Types
// ============================================================================

export interface ValidationHistoryItem {
  id: string
  timestamp: string
  documentName?: string
  modules: string[]
  score: number
  status: 'passed' | 'failed' | 'warning'
  totalIssues: number
  criticalIssues: number
  executionTime: number
  corrected: boolean
}

export interface HistoryFilter {
  startDate?: string
  endDate?: string
  modules?: string[]
  status?: 'passed' | 'failed' | 'warning'
  minScore?: number
  maxScore?: number
  searchQuery?: string
}

// ============================================================================
// Statistics Types
// ============================================================================

export interface SystemStatistics {
  overview: OverviewStats
  moduleStats: ModuleStats[]
  trendData: TrendData[]
  topIssues: TopIssue[]
  recentActivity: RecentActivity[]
}

export interface OverviewStats {
  totalValidations: number
  totalCorrections: number
  averageScore: number
  passRate: number
  criticalIssuesResolved: number
  averageResponseTime: number
}

export interface ModuleStats {
  moduleName: string
  executions: number
  passRate: number
  averageScore: number
  issueCount: number
}

export interface TrendData {
  date: string
  validations: number
  averageScore: number
  issueCount: number
}

export interface TopIssue {
  gateName: string
  moduleName: string
  count: number
  severity: string
  trend: 'up' | 'down' | 'stable'
}

export interface RecentActivity {
  id: string
  type: 'validation' | 'correction' | 'module_update'
  description: string
  timestamp: string
  status: 'success' | 'error' | 'warning'
}

// ============================================================================
// Settings Types
// ============================================================================

export interface UserSettings {
  theme: 'light' | 'dark' | 'system'
  language: string
  defaultModules: string[]
  autoCorrect: boolean
  notificationsEnabled: boolean
  emailNotifications: boolean
  validationOptions: ValidationOptions
  uiPreferences: UIPreferences
}

export interface UIPreferences {
  compactMode: boolean
  showLineNumbers: boolean
  syntaxHighlighting: boolean
  animationsEnabled: boolean
  defaultView: 'dashboard' | 'validator' | 'history'
}
