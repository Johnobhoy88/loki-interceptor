/**
 * Validation Store
 * Global state management for validation operations
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ValidationResult, CorrectionResult } from '@/types'

interface ValidationState {
  currentValidation: ValidationResult | null
  currentCorrection: CorrectionResult | null
  isValidating: boolean
  isCorrecting: boolean
  error: string | null

  // Actions
  setCurrentValidation: (validation: ValidationResult | null) => void
  setCurrentCorrection: (correction: CorrectionResult | null) => void
  setIsValidating: (isValidating: boolean) => void
  setIsCorrecting: (isCorrecting: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

export const useValidationStore = create<ValidationState>()(
  persist(
    (set) => ({
      currentValidation: null,
      currentCorrection: null,
      isValidating: false,
      isCorrecting: false,
      error: null,

      setCurrentValidation: (validation) =>
        set({ currentValidation: validation, error: null }),
      setCurrentCorrection: (correction) =>
        set({ currentCorrection: correction, error: null }),
      setIsValidating: (isValidating) => set({ isValidating }),
      setIsCorrecting: (isCorrecting) => set({ isCorrecting }),
      setError: (error) => set({ error }),
      reset: () =>
        set({
          currentValidation: null,
          currentCorrection: null,
          isValidating: false,
          isCorrecting: false,
          error: null,
        }),
    }),
    {
      name: 'validation-storage',
      partialize: (state) => ({
        currentValidation: state.currentValidation,
        currentCorrection: state.currentCorrection,
      }),
    }
  )
)
