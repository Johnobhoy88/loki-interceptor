/**
 * useValidation Hook
 * Custom React hook for validation operations with React Query
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { validationService } from '@/services/validation-service'
import { useValidationStore } from '@/stores/validation-store'
import { useUIStore } from '@/stores/ui-store'
import type { ValidationRequest, CorrectionRequest } from '@/types'

export function useValidation() {
  const queryClient = useQueryClient()
  const { setCurrentValidation, setIsValidating, setError } = useValidationStore()
  const { addNotification } = useUIStore()

  const validateMutation = useMutation({
    mutationFn: (request: ValidationRequest) => validationService.validate(request),
    onMutate: () => {
      setIsValidating(true)
      setError(null)
    },
    onSuccess: (data) => {
      setCurrentValidation(data)
      setIsValidating(false)
      addNotification({
        type: 'success',
        title: 'Validation Complete',
        message: `Compliance score: ${data.overallScore}%`,
        duration: 5000,
      })
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
    onError: (error: Error) => {
      setError(error.message)
      setIsValidating(false)
      addNotification({
        type: 'error',
        title: 'Validation Failed',
        message: error.message,
        duration: 5000,
      })
    },
  })

  return {
    validate: validateMutation.mutate,
    isValidating: validateMutation.isPending,
    error: validateMutation.error,
    data: validateMutation.data,
  }
}

export function useCorrection() {
  const queryClient = useQueryClient()
  const { setCurrentCorrection, setIsCorrecting, setError } = useValidationStore()
  const { addNotification } = useUIStore()

  const correctMutation = useMutation({
    mutationFn: (request: CorrectionRequest) => validationService.correct(request),
    onMutate: () => {
      setIsCorrecting(true)
      setError(null)
    },
    onSuccess: (data) => {
      setCurrentCorrection(data)
      setIsCorrecting(false)
      addNotification({
        type: 'success',
        title: 'Correction Complete',
        message: `Applied ${data.appliedCorrections.length} corrections`,
        duration: 5000,
      })
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
    onError: (error: Error) => {
      setError(error.message)
      setIsCorrecting(false)
      addNotification({
        type: 'error',
        title: 'Correction Failed',
        message: error.message,
        duration: 5000,
      })
    },
  })

  return {
    correct: correctMutation.mutate,
    isCorrecting: correctMutation.isPending,
    error: correctMutation.error,
    data: correctMutation.data,
  }
}

export function useValidationResult(id: string | undefined) {
  return useQuery({
    queryKey: ['validation', id],
    queryFn: () => validationService.getValidation(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
