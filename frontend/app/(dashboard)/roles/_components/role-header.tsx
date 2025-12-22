'use client'

import { useTranslations } from 'next-intl'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface RoleHeaderProps {
  onCreateClick?: () => void
}

export function RoleHeader({ onCreateClick }: RoleHeaderProps) {
  const t = useTranslations('roles')

  return (
    <div className="flex items-center justify-between">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <Button onClick={onCreateClick}>
        <Plus className="mr-2 h-4 w-4" />
        {t('createRole')}
      </Button>
    </div>
  )
}
