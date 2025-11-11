/**
 * History Service
 * Handles validation history operations
 */

import { apiClient } from './api-client'
import type { ValidationHistoryItem, HistoryFilter, PaginatedResponse } from '@/types'

export const historyService = {
  /**
   * Get validation history with pagination and filters
   */
  async getHistory(
    page = 1,
    pageSize = 20,
    filter?: HistoryFilter
  ): Promise<PaginatedResponse<ValidationHistoryItem>> {
    const params = new URLSearchParams({
      page: page.toString(),
      pageSize: pageSize.toString(),
    })

    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            params.append(key, value.join(','))
          } else {
            params.append(key, String(value))
          }
        }
      })
    }

    return apiClient.get<PaginatedResponse<ValidationHistoryItem>>(
      `/v1/history?${params.toString()}`
    )
  },

  /**
   * Get history item by ID
   */
  async getHistoryItem(id: string): Promise<ValidationHistoryItem> {
    return apiClient.get<ValidationHistoryItem>(`/v1/history/${id}`)
  },

  /**
   * Delete history item
   */
  async deleteHistoryItem(id: string): Promise<void> {
    return apiClient.delete<void>(`/v1/history/${id}`)
  },

  /**
   * Clear all history
   */
  async clearHistory(): Promise<void> {
    return apiClient.delete<void>('/v1/history')
  },

  /**
   * Export history
   */
  async exportHistory(format: 'csv' | 'json', filter?: HistoryFilter): Promise<void> {
    const params = new URLSearchParams({ format })

    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            params.append(key, value.join(','))
          } else {
            params.append(key, String(value))
          }
        }
      })
    }

    const filename = `history-export-${Date.now()}.${format}`
    return apiClient.download(`/v1/history/export?${params.toString()}`, filename)
  },
}
