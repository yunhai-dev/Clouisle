'use client'

import * as React from 'react'

export type SidebarVariant = 'inset' | 'floating' | 'sidebar'
export type LayoutVariant = 'default' | 'compact' | 'full'
export type DirectionVariant = 'ltr' | 'rtl'

interface SettingsState {
  sidebarVariant: SidebarVariant
  layoutVariant: LayoutVariant
  direction: DirectionVariant
}

interface SettingsContextType extends SettingsState {
  mounted: boolean
  setSidebarVariant: (variant: SidebarVariant) => void
  setLayoutVariant: (variant: LayoutVariant) => void
  setDirection: (direction: DirectionVariant) => void
  resetSettings: () => void
}

const defaultSettings: SettingsState = {
  sidebarVariant: 'inset',
  layoutVariant: 'default',
  direction: 'ltr',
}

const SettingsContext = React.createContext<SettingsContextType | undefined>(undefined)

const STORAGE_KEY = 'clouisle-settings'

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = React.useState<SettingsState>(defaultSettings)
  const [mounted, setMounted] = React.useState(false)

  // Load settings from localStorage on mount
  React.useEffect(() => {
    setMounted(true)
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setSettings((prev) => ({ ...prev, ...parsed }))
      } catch (e) {
        console.error('Failed to parse settings', e)
      }
    }
  }, [])

  // Save settings to localStorage when changed
  React.useEffect(() => {
    if (mounted) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
    }
  }, [settings, mounted])

  // Apply direction to document
  React.useEffect(() => {
    if (mounted) {
      document.documentElement.dir = settings.direction
    }
  }, [settings.direction, mounted])

  const setSidebarVariant = React.useCallback((variant: SidebarVariant) => {
    setSettings((prev) => ({ ...prev, sidebarVariant: variant }))
  }, [])

  const setLayoutVariant = React.useCallback((variant: LayoutVariant) => {
    setSettings((prev) => ({ ...prev, layoutVariant: variant }))
  }, [])

  const setDirection = React.useCallback((direction: DirectionVariant) => {
    setSettings((prev) => ({ ...prev, direction }))
  }, [])

  const resetSettings = React.useCallback(() => {
    setSettings(defaultSettings)
  }, [])

  const value = React.useMemo(
    () => ({
      ...settings,
      mounted,
      setSidebarVariant,
      setLayoutVariant,
      setDirection,
      resetSettings,
    }),
    [settings, mounted, setSidebarVariant, setLayoutVariant, setDirection, resetSettings]
  )

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = React.useContext(SettingsContext)
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}
