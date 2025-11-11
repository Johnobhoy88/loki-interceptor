/**
 * Statistics Service
 * Handles system statistics and analytics
 */

import { apiClient } from './api-client'
import type { SystemStatistics } from '@/types'

export const statsService = {
  /**
   * Get comprehensive system statistics
   */
  async getSystemStats(): Promise<SystemStatistics> {
    return apiClient.get<SystemStatistics>('/v1/stats')
  },

  /**
   * Get statistics for a specific date range
   */
  async getStatsForRange(startDate: string, endDate: string): Promise<SystemStatistics> {
    return apiClient.get<SystemStatistics>(
      `/v1/stats?start_date=${startDate}&end_date=${endDate}`
    )
  },

  /**
   * Get real-time metrics
   */
  async getRealTimeMetrics(): Promise<{
    activeValidations: number
    queuedValidations: number
    systemLoad: number
    uptime: number
  }> {
    return apiClient.get('/v1/stats/realtime')
  },
}
