'use client'

import * as React from 'react'
import { useTranslations } from 'next-intl'
import { toast } from 'sonner'
import { usersApi, ApiError, type User, type UserCreateData, type UserUpdateData } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface UserDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user?: User | null // 编辑时传入用户，创建时为 null
  onSuccess?: (user: User) => void
}

export function UserDialog({ open, onOpenChange, user, onSuccess }: UserDialogProps) {
  const t = useTranslations('users')
  const commonT = useTranslations('common')
  const authT = useTranslations('auth')
  
  const isEditing = !!user
  
  const [formData, setFormData] = React.useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    is_active: true,
  })
  const [fieldErrors, setFieldErrors] = React.useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  
  // 当 user 改变或 dialog 打开时重置表单
  React.useEffect(() => {
    if (open) {
      if (user) {
        setFormData({
          username: user.username,
          email: user.email,
          password: '',
          confirmPassword: '',
          is_active: user.is_active,
        })
      } else {
        setFormData({
          username: '',
          email: '',
          password: '',
          confirmPassword: '',
          is_active: true,
        })
      }
      setFieldErrors({})
    }
  }, [open, user])
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFieldErrors({})
    
    // 验证密码
    if (!isEditing && formData.password.length < 6) {
      setFieldErrors({ password: authT('passwordTooShort') })
      return
    }
    
    if (formData.password && formData.password !== formData.confirmPassword) {
      setFieldErrors({ confirmPassword: authT('passwordMismatch') })
      return
    }
    
    setIsSubmitting(true)
    
    try {
      let result: User
      
      if (isEditing && user) {
        // 编辑用户
        const updateData: UserUpdateData = {
          email: formData.email,
          is_active: formData.is_active,
        }
        if (formData.password) {
          updateData.password = formData.password
        }
        result = await usersApi.updateUser(user.id, updateData)
        toast.success(t('userUpdated'))
      } else {
        // 创建用户
        const createData: UserCreateData = {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          is_active: formData.is_active,
        }
        result = await usersApi.createUser(createData)
        toast.success(t('userCreated'))
      }
      
      onSuccess?.(result)
      onOpenChange(false)
    } catch (error) {
      if (error instanceof ApiError && error.isValidationError()) {
        setFieldErrors(error.getFieldErrors())
      }
    } finally {
      setIsSubmitting(false)
    }
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{isEditing ? t('editUser') : t('createUser')}</DialogTitle>
          <DialogDescription>
            {isEditing ? t('editUserDescription') : t('createUserDescription')}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="username">{authT('username')}</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              disabled={isEditing}
              required={!isEditing}
              autoFocus={!isEditing}
            />
            {fieldErrors.username && (
              <p className="text-sm text-destructive">{fieldErrors.username}</p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="email">{authT('email')}</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              autoFocus={isEditing}
            />
            {fieldErrors.email && (
              <p className="text-sm text-destructive">{fieldErrors.email}</p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="password">
              {authT('password')}
              {isEditing && <span className="text-muted-foreground ml-1">({t('leaveBlankToKeep')})</span>}
            </Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!isEditing}
              minLength={6}
            />
            {fieldErrors.password && (
              <p className="text-sm text-destructive">{fieldErrors.password}</p>
            )}
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="confirmPassword">{authT('confirmPassword')}</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              required={!isEditing && !!formData.password}
            />
            {fieldErrors.confirmPassword && (
              <p className="text-sm text-destructive">{fieldErrors.confirmPassword}</p>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <Label htmlFor="is_active">{t('active')}</Label>
            <Switch
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
            />
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              {commonT('cancel')}
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? commonT('loading')
                : isEditing
                  ? commonT('save')
                  : commonT('create')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
