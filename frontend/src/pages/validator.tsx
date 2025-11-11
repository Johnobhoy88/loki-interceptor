/**
 * Validator Page
 * Main document validation interface
 */

import React, { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentUploader } from '@/components/features/document-uploader'
import { ValidationResults } from '@/components/features/validation-results'
import { ComplianceScoreChart } from '@/components/features/compliance-score-chart'
import { useValidation, useCorrection } from '@/hooks/use-validation'
import { useModules } from '@/hooks/use-modules'
import { useSettingsStore } from '@/stores/settings-store'
import { CheckCircle, FileText, Upload, Play } from 'lucide-react'

export function ValidatorPage() {
  const [content, setContent] = useState('')
  const [selectedModules, setSelectedModules] = useState<string[]>([])
  const [documentName, setDocumentName] = useState('')

  const { validate, isValidating, data: validationResult } = useValidation()
  const { correct, isCorrecting } = useCorrection()
  const { data: modules } = useModules()
  const { defaultModules } = useSettingsStore()

  React.useEffect(() => {
    if (defaultModules.length > 0 && selectedModules.length === 0) {
      setSelectedModules(defaultModules)
    }
  }, [defaultModules])

  const handleFileSelect = (fileContent: string, fileName: string) => {
    setContent(fileContent)
    setDocumentName(fileName)
  }

  const handleValidate = () => {
    if (!content.trim()) return

    validate({
      content,
      modules: selectedModules.length > 0 ? selectedModules : undefined,
      options: {
        includeExplanations: true,
      },
    })
  }

  const handleApplyCorrection = (issueId: string) => {
    if (!validationResult) return

    correct({
      validationId: validationResult.id,
      issueIds: [issueId],
      reviewRequired: false,
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Document Validator</h1>
        <p className="text-muted-foreground">
          Validate documents against compliance regulations
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* File Upload */}
          <DocumentUploader onFileSelect={handleFileSelect} />

          {/* Text Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Document Content
              </CardTitle>
              <CardDescription>
                {documentName
                  ? `Editing: ${documentName}`
                  : 'Paste or type your document content here'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Enter your document content here..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="min-h-[400px] font-mono text-sm"
              />
              <div className="flex items-center justify-between mt-4">
                <span className="text-sm text-muted-foreground">
                  {content.length} characters
                </span>
                <Button
                  onClick={handleValidate}
                  disabled={!content.trim() || isValidating}
                  size="lg"
                >
                  <Play className="h-4 w-4 mr-2" />
                  {isValidating ? 'Validating...' : 'Validate Document'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {validationResult && (
            <ValidationResults
              result={validationResult}
              onApplyCorrection={handleApplyCorrection}
            />
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Module Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Compliance Modules</CardTitle>
              <CardDescription>Select modules to validate against</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {modules?.map((module) => (
                  <label
                    key={module.id}
                    className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-accent"
                  >
                    <input
                      type="checkbox"
                      checked={selectedModules.includes(module.name)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedModules([...selectedModules, module.name])
                        } else {
                          setSelectedModules(selectedModules.filter((m) => m !== module.name))
                        }
                      }}
                      className="h-4 w-4"
                    />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{module.displayName}</p>
                      <p className="text-xs text-muted-foreground">{module.jurisdiction}</p>
                    </div>
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Score Display */}
          {validationResult && (
            <ComplianceScoreChart score={validationResult.overallScore} />
          )}

          {/* Quick Stats */}
          {validationResult && (
            <Card>
              <CardHeader>
                <CardTitle>Validation Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <span className="text-sm font-medium capitalize">
                    {validationResult.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Total Issues</span>
                  <span className="text-sm font-medium">{validationResult.totalIssues}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Critical</span>
                  <span className="text-sm font-medium text-red-600">
                    {validationResult.criticalIssues}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Modules</span>
                  <span className="text-sm font-medium">
                    {validationResult.moduleResults.length}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
