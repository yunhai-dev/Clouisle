'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { toast } from 'sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Skeleton } from '@/components/ui/skeleton'
import { Loader2 } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { siteSettingsApi, type EmailSettings } from '@/lib/api'

export default function SiteSettingsEmailPage() {
  const t = useTranslations('siteSettings')
  
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  const [testEmail, setTestEmail] = React.useState('')
  const [sendingTest, setSendingTest] = React.useState(false)
  const [settings, setSettings] = React.useState<EmailSettings>({
    smtp_enabled: false,
    smtp_host: '',
    smtp_port: 587,
    smtp_encryption: 'tls',
    smtp_username: '',
    smtp_password: '',
    email_from_name: 'Clouisle',
    email_from_address: '',
  })

  React.useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await siteSettingsApi.getEmail()
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
      await siteSettingsApi.updateEmail(settings)
      toast.success(t('saveSuccess'))
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error(t('saveError'))
    } finally {
      setSaving(false)
    }
  }

  const handleSendTest = async () => {
    if (!testEmail) {
      toast.error(t('testEmailRequired'))
      return
    }
    try {
      setSendingTest(true)
      await siteSettingsApi.sendTestEmail(testEmail)
      toast.success(t('testEmailSent'))
    } catch (error) {
      console.error('Failed to send test email:', error)
      toast.error(t('testEmailFailed'))
    } finally {
      setSendingTest(false)
    }
  }

  const updateSetting = <K extends keyof EmailSettings>(key: K, value: EmailSettings[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-48" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('smtpSettings')}</CardTitle>
          <CardDescription>{t('smtpSettingsDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>{t('enableSmtp')}</Label>
              <p className="text-sm text-muted-foreground">{t('enableSmtpDescription')}</p>
            </div>
            <Switch 
              checked={settings.smtp_enabled}
              onCheckedChange={(checked) => updateSetting('smtp_enabled', checked)}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="smtpHost">{t('smtpHost')}</Label>
              <Input 
                id="smtpHost" 
                placeholder="smtp.example.com" 
                value={settings.smtp_host}
                onChange={(e) => updateSetting('smtp_host', e.target.value)}
                disabled={!settings.smtp_enabled}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtpPort">{t('smtpPort')}</Label>
              <Input 
                id="smtpPort" 
                type="number" 
                value={settings.smtp_port}
                onChange={(e) => updateSetting('smtp_port', parseInt(e.target.value) || 587)}
                disabled={!settings.smtp_enabled}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="smtpEncryption">{t('encryption')}</Label>
            <Select 
              value={settings.smtp_encryption}
              onValueChange={(value) => updateSetting('smtp_encryption', value as 'none' | 'ssl' | 'tls')}
              disabled={!settings.smtp_enabled}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">{t('none')}</SelectItem>
                <SelectItem value="ssl">SSL</SelectItem>
                <SelectItem value="tls">TLS</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="smtpUsername">{t('smtpUsername')}</Label>
              <Input 
                id="smtpUsername" 
                placeholder={t('smtpUsernamePlaceholder')} 
                value={settings.smtp_username}
                onChange={(e) => updateSetting('smtp_username', e.target.value)}
                disabled={!settings.smtp_enabled}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="smtpPassword">{t('smtpPassword')}</Label>
              <Input 
                id="smtpPassword" 
                type="password" 
                placeholder="••••••••" 
                value={settings.smtp_password}
                onChange={(e) => updateSetting('smtp_password', e.target.value)}
                disabled={!settings.smtp_enabled}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('senderSettings')}</CardTitle>
          <CardDescription>{t('senderSettingsDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="fromName">{t('fromName')}</Label>
            <Input 
              id="fromName" 
              placeholder="Clouisle" 
              value={settings.email_from_name}
              onChange={(e) => updateSetting('email_from_name', e.target.value)}
              disabled={!settings.smtp_enabled}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="fromEmail">{t('fromEmail')}</Label>
            <Input 
              id="fromEmail" 
              type="email" 
              placeholder="noreply@example.com" 
              value={settings.email_from_address}
              onChange={(e) => updateSetting('email_from_address', e.target.value)}
              disabled={!settings.smtp_enabled}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('testEmail')}</CardTitle>
          <CardDescription>{t('testEmailDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Input 
              placeholder={t('testEmailPlaceholder')} 
              className="flex-1" 
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              disabled={!settings.smtp_enabled}
            />
            <Button 
              variant="outline" 
              onClick={handleSendTest}
              disabled={!settings.smtp_enabled || sendingTest}
            >
              {sendingTest && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t('sendTestEmail')}
            </Button>
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
