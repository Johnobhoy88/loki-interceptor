/**
 * Settings Store
 * User preferences and application settings
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { UserSettings } from '@/types'

interface SettingsState extends UserSettings {
  // Actions
  setTheme: (theme: UserSettings['theme']) => void
  setLanguage: (language: string) => void
  setDefaultModules: (modules: string[]) => void
  setAutoCorrect: (autoCorrect: boolean) => void
  setNotificationsEnabled: (enabled: boolean) => void
  setEmailNotifications: (enabled: boolean) => void
  updateUIPreferences: (preferences: Partial<UserSettings['uiPreferences']>) => void
  updateValidationOptions: (options: Partial<UserSettings['validationOptions']>) => void
  reset: () => void
}

const defaultSettings: UserSettings = {
  theme: 'system',
  language: 'en',
  defaultModules: ['gdpr_uk', 'uk_employment', 'fca_uk'],
  autoCorrect: false,
  notificationsEnabled: true,
  emailNotifications: false,
  validationOptions: {
    severity: 'medium',
    autoCorrect: false,
    includeExplanations: true,
  },
  uiPreferences: {
    compactMode: false,
    showLineNumbers: true,
    syntaxHighlighting: true,
    animationsEnabled: true,
    defaultView: 'dashboard',
  },
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...defaultSettings,

      setTheme: (theme) => {
        set({ theme })
        // Apply theme to document
        const root = window.document.documentElement
        root.classList.remove('light', 'dark')
        if (theme === 'system') {
          const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light'
          root.classList.add(systemTheme)
        } else {
          root.classList.add(theme)
        }
      },

      setLanguage: (language) => set({ language }),
      setDefaultModules: (defaultModules) => set({ defaultModules }),
      setAutoCorrect: (autoCorrect) => set({ autoCorrect }),
      setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
      setEmailNotifications: (emailNotifications) => set({ emailNotifications }),

      updateUIPreferences: (preferences) =>
        set((state) => ({
          uiPreferences: { ...state.uiPreferences, ...preferences },
        })),

      updateValidationOptions: (options) =>
        set((state) => ({
          validationOptions: { ...state.validationOptions, ...options },
        })),

      reset: () => set(defaultSettings),
    }),
    {
      name: 'settings-storage',
    }
  )
)
