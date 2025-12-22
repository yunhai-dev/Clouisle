'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { useTheme } from 'next-themes'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { locales, localeNames, type Locale } from '@/i18n/config'
import { useLocale } from 'next-intl'
import { useRouter } from 'next/navigation'

export default function AppearancePage() {
  const t = useTranslations('settings')
  const { theme, setTheme } = useTheme()
  const locale = useLocale()
  const router = useRouter()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const handleLocaleChange = React.useCallback((newLocale: Locale) => {
    document.cookie = `locale=${newLocale};path=/;max-age=31536000`
    router.refresh()
  }, [router])

  const themes = [
    { value: 'light', label: t('light') },
    { value: 'dark', label: t('dark') },
    { value: 'system', label: t('system') },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{t('appearance')}</h3>
        <p className="text-sm text-muted-foreground">{t('appearanceDescription')}</p>
      </div>
      <Separator />
      
      {/* Theme Selection */}
      <Card>
        <CardHeader>
          <CardTitle>{t('theme')}</CardTitle>
          <CardDescription>{t('themeDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {themes.map((item) => (
              <div
                key={item.value}
                onClick={() => setTheme(item.value)}
                className={cn(
                  "cursor-pointer rounded-lg border-2 p-4 text-center transition-colors",
                  mounted && theme === item.value
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-muted-foreground/50"
                )}
              >
                <div className={cn(
                  "mb-2 h-16 rounded-md",
                  item.value === 'light' && "bg-white border",
                  item.value === 'dark' && "bg-zinc-900",
                  item.value === 'system' && "bg-gradient-to-r from-white to-zinc-900 border"
                )} />
                <Label className="cursor-pointer">{item.label}</Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Language Selection */}
      <Card>
        <CardHeader>
          <CardTitle>{t('language')}</CardTitle>
          <CardDescription>{t('languageDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {locales.map((l) => (
              <div
                key={l}
                onClick={() => handleLocaleChange(l)}
                className={cn(
                  "cursor-pointer rounded-lg border-2 p-4 text-center transition-colors",
                  locale === l
                    ? "border-primary bg-primary/5"
                    : "border-muted hover:border-muted-foreground/50"
                )}
              >
                <div className="text-2xl mb-2">{l === 'en' ? '🇺🇸' : '🇨🇳'}</div>
                <Label className="cursor-pointer">{localeNames[l]}</Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
