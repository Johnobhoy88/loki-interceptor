/**
 * useModules Hook
 * Custom React hook for compliance module operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { moduleService } from '@/services/module-service'
import { useUIStore } from '@/stores/ui-store'

export function useModules() {
  return useQuery({
    queryKey: ['modules'],
    queryFn: () => moduleService.getModules(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export function useModule(id: string | undefined) {
  return useQuery({
    queryKey: ['module', id],
    queryFn: () => moduleService.getModule(id!),
    enabled: !!id,
    staleTime: 10 * 60 * 1000,
  })
}

export function useRecommendedModules(content: string) {
  return useQuery({
    queryKey: ['recommended-modules', content],
    queryFn: () => moduleService.getRecommendedModules(content),
    enabled: content.length > 100, // Only recommend if content is substantial
    staleTime: 5 * 60 * 1000,
  })
}

export function useToggleModule() {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      moduleService.toggleModule(id, enabled),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['modules'] })
      queryClient.invalidateQueries({ queryKey: ['module', variables.id] })
      addNotification({
        type: 'success',
        title: 'Module Updated',
        message: `Module ${variables.enabled ? 'enabled' : 'disabled'} successfully`,
        duration: 3000,
      })
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error.message,
        duration: 5000,
      })
    },
  })
}
