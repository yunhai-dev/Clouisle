'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Loader2 } from 'lucide-react'
import { usersApi } from '@/lib/api'
import { useSiteSettings } from '@/contexts/site-settings-context'

export default function AccountPage() {
  const t = useTranslations('settings')
  const tCommon = useTranslations('common')
  const router = useRouter()
  const { settings: siteSettings } = useSiteSettings()
  
  const [saving, setSaving] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [deletePassword, setDeletePassword] = React.useState('')
  const [formData, setFormData] = React.useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  const handleChangePassword = async () => {
    // 验证
    if (!formData.currentPassword) {
      toast.error(t('currentPasswordRequired'))
      return
    }
    if (!formData.newPassword) {
      toast.error(t('newPasswordRequired'))
      return
    }
    if (formData.newPassword.length < 6) {
      toast.error(t('newPasswordTooShort'))
      return
    }
    if (formData.newPassword !== formData.confirmPassword) {
      toast.error(t('passwordMismatch'))
      return
    }

    try {
      setSaving(true)
      await usersApi.changePassword({
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
      })
      toast.success(t('passwordUpdated'))
      // 清空表单
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      })
    } catch (error) {
      // 错误已由 API 客户端处理
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      toast.error(t('currentPasswordRequired'))
      return
    }

    try {
      setDeleting(true)
      await usersApi.deleteAccount(deletePassword)
      toast.success(t('accountDeleted'))
      // 清除本地存储并跳转到登录页
      localStorage.removeItem('access_token')
      router.push('/login')
    } catch (error) {
      // 错误已由 API 客户端处理
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{t('account')}</h3>
        <p className="text-sm text-muted-foreground">{t('accountDescription')}</p>
      </div>
      <Separator />
      
      <Card>
        <CardHeader>
          <CardTitle>{t('changePassword')}</CardTitle>
          <CardDescription>{t('changePasswordDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current">{t('currentPassword')}</Label>
            <Input 
              id="current" 
              type="password"
              placeholder={t('currentPasswordPlaceholder')}
              value={formData.currentPassword}
              onChange={(e) => setFormData(prev => ({ ...prev, currentPassword: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new">{t('newPassword')}</Label>
            <Input 
              id="new" 
              type="password"
              placeholder={t('newPasswordPlaceholder')}
              value={formData.newPassword}
              onChange={(e) => setFormData(prev => ({ ...prev, newPassword: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm">{t('confirmNewPassword')}</Label>
            <Input 
              id="confirm" 
              type="password"
              placeholder={t('confirmNewPasswordPlaceholder')}
              value={formData.confirmPassword}
              onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
            />
          </div>
          <Button onClick={handleChangePassword} disabled={saving}>
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {t('updatePassword')}
          </Button>
        </CardContent>
      </Card>

      {siteSettings.allow_account_deletion && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">{t('dangerZone')}</CardTitle>
            <CardDescription>{t('dangerZoneDescription')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">{t('deleteAccountDescription')}</p>
              <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogTrigger
                  render={<Button variant="destructive">{t('deleteAccount')}</Button>}
                />
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>{t('deleteAccount')}</AlertDialogTitle>
                    <AlertDialogDescription>
                      {t('deleteAccountConfirm')}
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <div className="space-y-2">
                    <Label htmlFor="delete-password">{t('currentPassword')}</Label>
                    <Input
                      id="delete-password"
                      type="password"
                      placeholder={t('currentPasswordPlaceholder')}
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                    />
                  </div>
                  <AlertDialogFooter>
                    <AlertDialogCancel onClick={() => setDeletePassword('')}>
                      {tCommon('cancel')}
                    </AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDeleteAccount}
                      disabled={deleting || !deletePassword}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      {deleting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      {t('deleteAccount')}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
