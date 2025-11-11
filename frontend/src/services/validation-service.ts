/**
 * Validation Service
 * Handles document validation and correction operations
 */

import { apiClient } from './api-client'
import type {
  ValidationRequest,
  ValidationResult,
  CorrectionRequest,
  CorrectionResult,
} from '@/types'

export const validationService = {
  /**
   * Validate document content
   */
  async validate(request: ValidationRequest): Promise<ValidationResult> {
    return apiClient.post<ValidationResult>('/v1/validate', request)
  },

  /**
   * Get validation result by ID
   */
  async getValidation(id: string): Promise<ValidationResult> {
    return apiClient.get<ValidationResult>(`/v1/validate/${id}`)
  },

  /**
   * Apply corrections to validation issues
   */
  async correct(request: CorrectionRequest): Promise<CorrectionResult> {
    return apiClient.post<CorrectionResult>('/v1/correct', request)
  },

  /**
   * Get correction result by ID
   */
  async getCorrection(id: string): Promise<CorrectionResult> {
    return apiClient.get<CorrectionResult>(`/v1/correct/${id}`)
  },

  /**
   * Validate and auto-correct in one step
   */
  async validateAndCorrect(request: ValidationRequest): Promise<CorrectionResult> {
    const validationResult = await this.validate({
      ...request,
      options: { ...request.options, autoCorrect: true },
    })

    return this.correct({
      validationId: validationResult.id,
      reviewRequired: false,
    })
  },

  /**
   * Export validation result
   */
  async exportValidation(id: string, format: 'json' | 'pdf' | 'html'): Promise<void> {
    const filename = `validation-${id}.${format}`
    return apiClient.download(`/v1/validate/${id}/export?format=${format}`, filename)
  },

  /**
   * Export correction result
   */
  async exportCorrection(id: string, format: 'json' | 'pdf' | 'docx'): Promise<void> {
    const filename = `correction-${id}.${format}`
    return apiClient.download(`/v1/correct/${id}/export?format=${format}`, filename)
  },
}
