'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { Search, Settings } from 'lucide-react'

import { SidebarTrigger } from '@/components/ui/sidebar'
import { Separator } from '@/components/ui/separator'
import { Input } from '@/components/ui/input'
import { ThemeToggle } from '@/components/theme-toggle'
import { SettingsDrawer } from '@/components/settings-drawer'

export function Header() {
  const t = useTranslations('common')
  const tSettings = useTranslations('settings')
  const [settingsOpen, setSettingsOpen] = React.useState(false)

  return (
    <header className="sticky top-0 z-40 flex h-12 shrink-0 items-center gap-2 bg-background px-4 md:rounded-t-xl">
      <SidebarTrigger 
        className="-ms-1 size-8 border border-border rounded-md" 
        title={t('toggleSidebar')}
      />
      <Separator orientation="vertical" className="h-6! self-center! mx-2" />
      
      {/* Search */}
      <div className="relative w-64">
        <Search className="absolute start-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          type="search"
          placeholder={`${t('search')}...`}
          className="w-full h-8 ps-7 text-sm"
        />
      </div>

      <div className="ms-auto flex items-center gap-1.5">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Appearance Settings */}
        <button
          onClick={() => setSettingsOpen(true)}
          className="rounded-md hover:bg-muted text-muted-foreground hover:text-foreground size-8 inline-flex items-center justify-center transition-colors"
          title={tSettings('themeSettings')}
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>

      <SettingsDrawer open={settingsOpen} onOpenChange={setSettingsOpen} />
    </header>
  )
}
