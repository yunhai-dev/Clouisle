import { api } from './client'
import type { PageData } from './users'

export interface Permission {
  id: string
  scope: string
  code: string
  description: string | null
}

export interface Role {
  id: string
  name: string
  description: string | null
  is_system_role: boolean
  permissions: Permission[]
}

export interface RoleCreateInput {
  name: string
  description?: string
  permissions?: string[]
}

export interface RoleUpdateInput {
  name?: string
  description?: string
}

export interface RolePermissionsUpdateInput {
  permissions: string[]
}

export interface PermissionCreateInput {
  scope: string
  code: string
  description?: string
}

export interface PermissionUpdateInput {
  scope: string
  code: string
  description?: string
}

export const rolesApi = {
  /**
   * 获取角色列表
   */
  getRoles: async (page: number = 1, pageSize: number = 50): Promise<PageData<Role>> => {
    return api.get<PageData<Role>>(`/roles?page=${page}&page_size=${pageSize}`)
  },

  /**
   * 获取单个角色
   */
  getRole: async (id: string): Promise<Role> => {
    return api.get<Role>(`/roles/${id}`)
  },

  /**
   * 创建角色
   */
  createRole: async (data: RoleCreateInput): Promise<Role> => {
    return api.post<Role>('/roles', data)
  },

  /**
   * 更新角色
   */
  updateRole: async (id: string, data: RoleUpdateInput): Promise<Role> => {
    return api.put<Role>(`/roles/${id}`, data)
  },

  /**
   * 更新角色权限
   */
  updateRolePermissions: async (id: string, permissions: string[]): Promise<Role> => {
    return api.put<Role>(`/roles/${id}/permissions`, { permissions })
  },

  /**
   * 删除角色
   */
  deleteRole: async (id: string): Promise<Role> => {
    return api.delete<Role>(`/roles/${id}`)
  },
}

export const permissionsApi = {
  /**
   * 获取权限列表
   */
  getPermissions: async (page: number = 1, pageSize: number = 100, scope?: string): Promise<PageData<Permission>> => {
    let url = `/permissions?page=${page}&page_size=${pageSize}`
    if (scope) url += `&scope=${scope}`
    return api.get<PageData<Permission>>(url)
  },

  /**
   * 获取单个权限
   */
  getPermission: async (id: string): Promise<Permission> => {
    return api.get<Permission>(`/permissions/${id}`)
  },

  /**
   * 创建权限
   */
  createPermission: async (data: PermissionCreateInput): Promise<Permission> => {
    return api.post<Permission>('/permissions', data)
  },

  /**
   * 更新权限
   */
  updatePermission: async (id: string, data: PermissionUpdateInput): Promise<Permission> => {
    return api.put<Permission>(`/permissions/${id}`, data)
  },

  /**
   * 删除权限
   */
  deletePermission: async (id: string): Promise<Permission> => {
    return api.delete<Permission>(`/permissions/${id}`)
  },
}
