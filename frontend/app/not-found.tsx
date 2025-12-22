import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { Button } from '@/components/ui/button'

export default async function NotFound() {
  const t = await getTranslations('errors')

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold text-muted-foreground">404</h1>
        <h2 className="text-2xl font-semibold">{t('notFound')}</h2>
        <p className="text-muted-foreground">{t('notFoundDescription')}</p>
        <Link href="/dashboard">
          <Button>{t('goHome')}</Button>
        </Link>
      </div>
    </div>
  )
}
