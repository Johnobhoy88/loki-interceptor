/**
 * Module Service
 * Handles compliance module operations
 */

import { apiClient } from './api-client'
import type { ComplianceModule } from '@/types'

export const moduleService = {
  /**
   * Get all available compliance modules
   */
  async getModules(): Promise<ComplianceModule[]> {
    return apiClient.get<ComplianceModule[]>('/v1/modules')
  },

  /**
   * Get module by ID
   */
  async getModule(id: string): Promise<ComplianceModule> {
    return apiClient.get<ComplianceModule>(`/v1/modules/${id}`)
  },

  /**
   * Get recommended modules based on content analysis
   */
  async getRecommendedModules(content: string): Promise<string[]> {
    return apiClient.post<string[]>('/v1/modules/recommend', { content })
  },

  /**
   * Enable/disable module
   */
  async toggleModule(id: string, enabled: boolean): Promise<void> {
    return apiClient.patch<void>(`/v1/modules/${id}`, { enabled })
  },

  /**
   * Get module statistics
   */
  async getModuleStats(id: string): Promise<ComplianceModule['statistics']> {
    return apiClient.get(`/v1/modules/${id}/stats`)
  },
}
