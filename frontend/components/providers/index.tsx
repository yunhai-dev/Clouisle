'use client'

import { ThemeProvider } from './theme-provider'
import { SettingsProvider } from '@/hooks/use-settings'
import { SiteSettingsProvider } from '@/contexts/site-settings-context'

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider>
      <SettingsProvider>
        <SiteSettingsProvider>
          {children}
        </SiteSettingsProvider>
      </SettingsProvider>
    </ThemeProvider>
  )
}
