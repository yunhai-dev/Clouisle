'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { Header } from '@/components/layout/header'
import { cn } from '@/lib/utils'

export default function SiteSettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const t = useTranslations('siteSettings')
  const pathname = usePathname()

  const settingsNav = [
    { title: t('general'), href: '/site-settings', description: t('generalDescription') },
    { title: t('security'), href: '/site-settings/security', description: t('securityDescription') },
    { title: t('email'), href: '/site-settings/email', description: t('emailDescription') },
  ]

  return (
    <div className="flex h-full flex-col">
      <Header />
      <div className="flex flex-1 flex-col gap-4 overflow-auto p-4">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <p className="text-muted-foreground">{t('description')}</p>
        
        <div className="flex flex-col md:flex-row gap-8 mt-4">
          {/* Settings Navigation */}
          <nav className="flex md:flex-col gap-2 md:w-48 overflow-x-auto">
            {settingsNav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-4 py-2 text-sm rounded-md whitespace-nowrap transition-colors",
                  pathname === item.href
                    ? "bg-muted font-medium"
                    : "hover:bg-muted/50 text-muted-foreground"
                )}
              >
                {item.title}
              </Link>
            ))}
          </nav>

          {/* Settings Content */}
          <div className="flex-1 max-w-2xl">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}
