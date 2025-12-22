'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { toast } from 'sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Skeleton } from '@/components/ui/skeleton'
import { Loader2 } from 'lucide-react'
import { ImageUpload } from '@/components/ui/image-upload'
import { siteSettingsApi, type GeneralSettings } from '@/lib/api'
import { useSiteSettings } from '@/contexts/site-settings-context'

export default function SiteSettingsGeneralPage() {
  const t = useTranslations('siteSettings')
  const { refresh: refreshSiteSettings } = useSiteSettings()
  
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  const [settings, setSettings] = React.useState<GeneralSettings>({
    site_name: 'Clouisle',
    site_description: '',
    site_url: '',
    site_icon: '',
    allow_registration: true,
    require_approval: false,
    email_verification: true,
    allow_account_deletion: true,
  })

  React.useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await siteSettingsApi.getGeneral()
      setSettings(data)
    } catch (error) {
      console.error('Failed to load settings:', error)
      toast.error(t('loadError'))
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await siteSettingsApi.updateGeneral(settings)
      // 刷新全局站点设置
      await refreshSiteSettings()
      toast.success(t('saveSuccess'))
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error(t('saveError'))
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = <K extends keyof GeneralSettings>(key: K, value: GeneralSettings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-4 w-48" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-16 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('siteInfo')}</CardTitle>
          <CardDescription>{t('siteInfoDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="siteName">{t('siteName')}</Label>
            <Input 
              id="siteName" 
              placeholder={t('siteNamePlaceholder')} 
              value={settings.site_name}
              onChange={(e) => updateSetting('site_name', e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="siteDescription">{t('siteDescription')}</Label>
            <Textarea 
              id="siteDescription" 
              placeholder={t('siteDescriptionPlaceholder')}
              rows={3}
              value={settings.site_description}
              onChange={(e) => updateSetting('site_description', e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="siteUrl">{t('siteUrl')}</Label>
            <Input 
              id="siteUrl" 
              placeholder="https://example.com" 
              value={settings.site_url}
              onChange={(e) => updateSetting('site_url', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('siteBranding')}</CardTitle>
          <CardDescription>{t('siteBrandingDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label>{t('siteIcon')}</Label>
            <p className="text-sm text-muted-foreground">{t('siteIconDescription')}</p>
            <div className="mt-2">
              <ImageUpload
                value={settings.site_icon}
                onChange={(url) => updateSetting('site_icon', url)}
                previewSize="md"
                category="icons"
              />
              <p className="text-xs text-muted-foreground mt-2">{t('siteIconHint')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('registration')}</CardTitle>
          <CardDescription>{t('registrationDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>{t('allowRegistration')}</Label>
              <p className="text-sm text-muted-foreground">{t('allowRegistrationDescription')}</p>
            </div>
            <Switch 
              checked={settings.allow_registration}
              onCheckedChange={(checked) => updateSetting('allow_registration', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>{t('requireApproval')}</Label>
              <p className="text-sm text-muted-foreground">{t('requireApprovalDescription')}</p>
            </div>
            <Switch 
              checked={settings.require_approval}
              onCheckedChange={(checked) => updateSetting('require_approval', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>{t('emailVerification')}</Label>
              <p className="text-sm text-muted-foreground">{t('emailVerificationDescription')}</p>
            </div>
            <Switch 
              checked={settings.email_verification}
              onCheckedChange={(checked) => updateSetting('email_verification', checked)}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>{t('allowAccountDeletion')}</Label>
              <p className="text-sm text-muted-foreground">{t('allowAccountDeletionDescription')}</p>
            </div>
            <Switch 
              checked={settings.allow_account_deletion}
              onCheckedChange={(checked) => updateSetting('allow_account_deletion', checked)}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {t('saveChanges')}
        </Button>
      </div>
    </div>
  )
}
