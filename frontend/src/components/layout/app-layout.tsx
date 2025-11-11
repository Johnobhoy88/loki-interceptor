/**
 * App Layout
 * Main application layout with navigation and sidebar
 */

import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FileCheck,
  History,
  Settings,
  Menu,
  Moon,
  Sun,
  Shield,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/hooks/use-theme'
import { useUIStore } from '@/stores/ui-store'
import { cn } from '@/lib/utils'

export function AppLayout() {
  const location = useLocation()
  const { theme, setTheme, isDark } = useTheme()
  const { sidebarOpen, toggleSidebar } = useUIStore()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Validator', href: '/validator', icon: FileCheck },
    { name: 'History', href: '/history', icon: History },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark')
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col border-r bg-card transition-transform duration-200',
          sidebarOpen ? 'w-64 translate-x-0' : 'w-0 -translate-x-full md:w-16 md:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b px-4">
          {sidebarOpen ? (
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">LOKI</span>
            </div>
          ) : (
            <Shield className="h-6 w-6 text-primary mx-auto" />
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t p-2">
          <Button
            variant="ghost"
            size={sidebarOpen ? 'default' : 'icon'}
            onClick={toggleTheme}
            className="w-full justify-start"
            title="Toggle theme"
          >
            {isDark ? (
              <Sun className="h-5 w-5 flex-shrink-0" />
            ) : (
              <Moon className="h-5 w-5 flex-shrink-0" />
            )}
            {sidebarOpen && <span className="ml-3">Theme</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <div
        className={cn(
          'flex flex-1 flex-col transition-all duration-200',
          sidebarOpen ? 'md:pl-64' : 'md:pl-16'
        )}
      >
        {/* Header */}
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-card px-6">
          <Button variant="ghost" size="icon" onClick={toggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex-1"></div>

          {/* User Menu / Additional Actions */}
          <div className="flex items-center gap-2">
            {/* Add user profile, notifications, etc. */}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
