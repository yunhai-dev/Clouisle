'use client'

import { useTranslations } from 'next-intl'
import { Wrench, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card'

export default function ToolsPage() {
  const t = useTranslations('platform')

  return (
    <div className="container py-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('tools.title')}</h1>
          <p className="text-muted-foreground mt-1">
            {t('tools.description')}
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          {t('tools.createTool')}
        </Button>
      </div>

      {/* Empty State */}
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Wrench className="h-12 w-12 text-muted-foreground mb-4" />
          <CardTitle className="mb-2">{t('tools.noTools')}</CardTitle>
          <CardDescription className="mb-4">
            {t('tools.createToolHint')}
          </CardDescription>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            {t('tools.createFirstTool')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
