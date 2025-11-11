/**
 * useHistory Hook
 * Custom React hook for validation history operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { historyService } from '@/services/history-service'
import { useUIStore } from '@/stores/ui-store'
import type { HistoryFilter } from '@/types'
import { useState } from 'react'

export function useHistory(page = 1, pageSize = 20, filter?: HistoryFilter) {
  return useQuery({
    queryKey: ['history', page, pageSize, filter],
    queryFn: () => historyService.getHistory(page, pageSize, filter),
    staleTime: 60 * 1000, // 1 minute
  })
}

export function useHistoryItem(id: string | undefined) {
  return useQuery({
    queryKey: ['history-item', id],
    queryFn: () => historyService.getHistoryItem(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  })
}

export function useDeleteHistoryItem() {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: (id: string) => historyService.deleteHistoryItem(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
      addNotification({
        type: 'success',
        title: 'Item Deleted',
        message: 'History item deleted successfully',
        duration: 3000,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Delete Failed',
        message: error.message,
        duration: 5000,
      })
    },
  })
}

export function useClearHistory() {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: () => historyService.clearHistory(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
      addNotification({
        type: 'success',
        title: 'History Cleared',
        message: 'All history items deleted successfully',
        duration: 3000,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Clear Failed',
        message: error.message,
        duration: 5000,
      })
    },
  })
}

export function useHistoryFilter() {
  const [filter, setFilter] = useState<HistoryFilter>({})

  const updateFilter = (updates: Partial<HistoryFilter>) => {
    setFilter((prev) => ({ ...prev, ...updates }))
  }

  const resetFilter = () => {
    setFilter({})
  }

  return {
    filter,
    updateFilter,
    resetFilter,
  }
}
