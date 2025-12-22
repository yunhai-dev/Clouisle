'use client'

import * as React from 'react'
import { Languages } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useLocale } from 'next-intl'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { locales, localeNames, type Locale } from '@/i18n/config'

export function LanguageToggle() {
  const locale = useLocale()
  const router = useRouter()

  const handleLocaleChange = React.useCallback((newLocale: Locale) => {
    // Set cookie
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`
    // Refresh to apply new locale
    router.refresh()
  }, [router])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="rounded-md hover:bg-muted text-muted-foreground hover:text-foreground size-8 inline-flex items-center justify-center transition-colors outline-none"
      >
        <Languages className="h-4 w-4" />
        <span className="sr-only">Change language</span>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {locales.map((l) => (
          <DropdownMenuItem
            key={l}
            onClick={() => handleLocaleChange(l)}
            className={locale === l ? 'bg-accent' : ''}
          >
            {localeNames[l]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
