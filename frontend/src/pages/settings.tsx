/**
 * Settings Page
 * User preferences and application configuration
 */

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useSettingsStore } from '@/stores/settings-store'
import { Moon, Sun, Monitor } from 'lucide-react'

export function SettingsPage() {
  const {
    theme,
    setTheme,
    autoCorrect,
    setAutoCorrect,
    notificationsEnabled,
    setNotificationsEnabled,
    uiPreferences,
    updateUIPreferences,
  } = useSettingsStore()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your preferences and application settings
        </p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the look and feel of the application</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Theme</label>
            <div className="flex gap-2 mt-2">
              <Button
                variant={theme === 'light' ? 'default' : 'outline'}
                onClick={() => setTheme('light')}
                className="flex-1"
              >
                <Sun className="h-4 w-4 mr-2" />
                Light
              </Button>
              <Button
                variant={theme === 'dark' ? 'default' : 'outline'}
                onClick={() => setTheme('dark')}
                className="flex-1"
              >
                <Moon className="h-4 w-4 mr-2" />
                Dark
              </Button>
              <Button
                variant={theme === 'system' ? 'default' : 'outline'}
                onClick={() => setTheme('system')}
                className="flex-1"
              >
                <Monitor className="h-4 w-4 mr-2" />
                System
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={uiPreferences.compactMode}
                onChange={(e) => updateUIPreferences({ compactMode: e.target.checked })}
                className="h-4 w-4"
              />
              <div>
                <p className="text-sm font-medium">Compact Mode</p>
                <p className="text-xs text-muted-foreground">Use a more compact layout</p>
              </div>
            </label>

            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={uiPreferences.animationsEnabled}
                onChange={(e) => updateUIPreferences({ animationsEnabled: e.target.checked })}
                className="h-4 w-4"
              />
              <div>
                <p className="text-sm font-medium">Animations</p>
                <p className="text-xs text-muted-foreground">Enable UI animations</p>
              </div>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Validation */}
      <Card>
        <CardHeader>
          <CardTitle>Validation Settings</CardTitle>
          <CardDescription>Configure default validation behavior</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={autoCorrect}
              onChange={(e) => setAutoCorrect(e.target.checked)}
              className="h-4 w-4"
            />
            <div>
              <p className="text-sm font-medium">Auto-Correct</p>
              <p className="text-xs text-muted-foreground">
                Automatically apply corrections during validation
              </p>
            </div>
          </label>

          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={uiPreferences.showLineNumbers}
              onChange={(e) => updateUIPreferences({ showLineNumbers: e.target.checked })}
              className="h-4 w-4"
            />
            <div>
              <p className="text-sm font-medium">Show Line Numbers</p>
              <p className="text-xs text-muted-foreground">Display line numbers in editor</p>
            </div>
          </label>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Manage notification preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={notificationsEnabled}
              onChange={(e) => setNotificationsEnabled(e.target.checked)}
              className="h-4 w-4"
            />
            <div>
              <p className="text-sm font-medium">Enable Notifications</p>
              <p className="text-xs text-muted-foreground">
                Receive notifications about validation results
              </p>
            </div>
          </label>
        </CardContent>
      </Card>
    </div>
  )
}
