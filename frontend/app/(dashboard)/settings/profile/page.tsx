'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { toast } from 'sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { ImageUpload } from '@/components/ui/image-upload'
import { Loader2 } from 'lucide-react'
import { usersApi, authApi } from '@/lib/api'
import type { User } from '@/lib/api/auth'

export default function ProfilePage() {
  const t = useTranslations('settings')
  
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  const [user, setUser] = React.useState<User | null>(null)
  const [formData, setFormData] = React.useState({
    username: '',
    email: '',
    avatar_url: '',
  })

  React.useEffect(() => {
    loadUser()
  }, [])

  const loadUser = async () => {
    try {
      setLoading(true)
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      setFormData({
        username: userData.username,
        email: userData.email,
        avatar_url: userData.avatar_url || '',
      })
    } catch (error) {
      console.error('Failed to load user:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!user) return
    
    try {
      setSaving(true)
      const updateData: Record<string, string | null> = {}
      
      if (formData.username !== user.username) {
        updateData.username = formData.username
      }
      if (formData.email !== user.email) {
        updateData.email = formData.email
      }
      if (formData.avatar_url !== (user.avatar_url || '')) {
        updateData.avatar_url = formData.avatar_url || null
      }
      
      if (Object.keys(updateData).length === 0) {
        toast.info('没有更改')
        return
      }
      
      const updatedUser = await usersApi.updateProfile(updateData)
      setUser(updatedUser)
      toast.success(t('profileUpdated'))
    } catch (error) {
      // 错误已由 API 客户端处理
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-4 w-48 mt-1" />
        </div>
        <Separator />
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-24 w-24 rounded-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">{t('profile')}</h3>
        <p className="text-sm text-muted-foreground">{t('profileDescription')}</p>
      </div>
      <Separator />
      
      <Card>
        <CardHeader>
          <CardTitle>{t('profileInfo')}</CardTitle>
          <CardDescription>{t('profileInfoDescription')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label>{t('avatar')}</Label>
            <p className="text-sm text-muted-foreground">{t('avatarDescription')}</p>
            <div className="mt-2">
              <ImageUpload
                value={formData.avatar_url}
                onChange={(url) => setFormData(prev => ({ ...prev, avatar_url: url }))}
                previewSize="lg"
                category="avatars"
              />
              <p className="text-xs text-muted-foreground mt-2">{t('avatarHint')}</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="username">{t('username')}</Label>
            <Input 
              id="username" 
              placeholder={t('usernamePlaceholder')}
              value={formData.username}
              onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">{t('email')}</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder={t('emailPlaceholder')}
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            />
          </div>
          
          <Button onClick={handleSave} disabled={saving}>
            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {t('saveChanges')}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
