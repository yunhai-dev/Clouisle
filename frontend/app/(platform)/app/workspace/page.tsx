'use client'

import { useTranslations } from 'next-intl'
import { Grid3x3, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card'

export default function WorkspacePage() {
  const t = useTranslations('platform')

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('workspace.title')}</h1>
          <p className="text-muted-foreground mt-1">
            {t('workspace.description')}
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          {t('workspace.createApp')}
        </Button>
      </div>

      {/* Empty State */}
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Grid3x3 className="h-12 w-12 text-muted-foreground mb-4" />
          <CardTitle className="mb-2">{t('workspace.noApps')}</CardTitle>
          <CardDescription className="mb-4">
            {t('workspace.createAppHint')}
          </CardDescription>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            {t('workspace.createFirstApp')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
