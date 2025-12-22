'use client'

import { useTranslations } from 'next-intl'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface UserHeaderProps {
  onCreateClick?: () => void
}

export function UserHeader({ onCreateClick }: UserHeaderProps) {
  const t = useTranslations('users')

  return (
    <div className="flex items-center justify-between">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <Button onClick={onCreateClick}>
        <Plus className="mr-2 h-4 w-4" />
        {t('createUser')}
      </Button>
    </div>
  )
}
