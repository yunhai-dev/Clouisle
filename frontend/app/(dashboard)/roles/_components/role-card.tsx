'use client'

import { useTranslations } from 'next-intl'
import { Shield } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export interface Role {
  name: string
  description: string
  permissions: string[]
  isSystem: boolean
  users: number
}

interface RoleCardProps {
  role: Role
  onClick?: () => void
}

export function RoleCard({ role, onClick }: RoleCardProps) {
  const t = useTranslations('roles')

  return (
    <Card 
      className="cursor-pointer hover:bg-accent/50 transition-colors"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg">{role.name}</CardTitle>
              <CardDescription>{role.description}</CardDescription>
            </div>
          </div>
          {role.isSystem && (
            <Badge variant="secondary">{t('systemRole')}</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex flex-wrap gap-1">
            {role.permissions.slice(0, 3).map((perm) => (
              <Badge key={perm} variant="outline" className="text-xs">
                {perm}
              </Badge>
            ))}
            {role.permissions.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{role.permissions.length - 3}
              </Badge>
            )}
          </div>
          <div className="text-sm text-muted-foreground">
            {role.users} {t('assignedUsers')}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface RoleGridProps {
  roles: Role[]
  onRoleClick?: (role: Role) => void
}

export function RoleGrid({ roles, onRoleClick }: RoleGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {roles.map((role, index) => (
        <RoleCard 
          key={index} 
          role={role} 
          onClick={() => onRoleClick?.(role)}
        />
      ))}
    </div>
  )
}
