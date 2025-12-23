import { api } from './client'

export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface ProviderInfo {
  code: string
  name: string
  base_url: string | null
  icon: string
}

export interface ModelTypeInfo {
  code: string
  name: string
  description: string
}

export interface Model {
  id: string
  name: string
  provider: string
  model_id: string
  model_type: string
  base_url: string | null
  has_api_key: boolean
  context_length: number | null
  max_output_tokens: number | null
  input_price: number | null
  output_price: number | null
  default_params: Record<string, unknown> | null
  capabilities: Record<string, unknown> | null
  config: Record<string, unknown> | null
  is_enabled: boolean
  is_default: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ModelBrief {
  id: string
  name: string
  provider: string
  model_id: string
  model_type: string
}

export interface ModelCreateInput {
  name: string
  provider: string
  model_id: string
  model_type: string
  base_url?: string | null
  api_key?: string | null
  context_length?: number | null
  max_output_tokens?: number | null
  input_price?: number | null
  output_price?: number | null
  default_params?: Record<string, unknown> | null
  capabilities?: Record<string, unknown> | null
  config?: Record<string, unknown> | null
  is_enabled?: boolean
  is_default?: boolean
  sort_order?: number
}

export interface ModelUpdateInput {
  name?: string
  base_url?: string | null
  api_key?: string | null
  context_length?: number | null
  max_output_tokens?: number | null
  input_price?: number | null
  output_price?: number | null
  default_params?: Record<string, unknown> | null
  capabilities?: Record<string, unknown> | null
  config?: Record<string, unknown> | null
  is_enabled?: boolean
  is_default?: boolean
  sort_order?: number
}

export interface ModelQueryParams {
  page?: number
  pageSize?: number
  provider?: string
  model_type?: string
  is_enabled?: boolean
  search?: string
}

export const modelsApi = {
  /**
   * 获取支持的供应商列表
   */
  getProviders: async (): Promise<ProviderInfo[]> => {
    return api.get<ProviderInfo[]>('/models/providers')
  },

  /**
   * 获取支持的模型类型列表
   */
  getModelTypes: async (): Promise<ModelTypeInfo[]> => {
    return api.get<ModelTypeInfo[]>('/models/types')
  },

  /**
   * 获取模型列表（分页）
   */
  getModels: async (params: ModelQueryParams = {}): Promise<PageData<Model>> => {
    const { page = 1, pageSize = 20, provider, model_type, is_enabled, search } = params
    const queryParams = new URLSearchParams()
    queryParams.append('page', String(page))
    queryParams.append('page_size', String(pageSize))
    if (provider) queryParams.append('provider', provider)
    if (model_type) queryParams.append('model_type', model_type)
    if (is_enabled !== undefined) queryParams.append('is_enabled', String(is_enabled))
    if (search) queryParams.append('search', search)
    return api.get<PageData<Model>>(`/models?${queryParams.toString()}`)
  },

  /**
   * 获取可用模型列表（下拉选择用）
   */
  getAvailableModels: async (model_type?: string): Promise<ModelBrief[]> => {
    const queryParams = new URLSearchParams()
    if (model_type) queryParams.append('model_type', model_type)
    const query = queryParams.toString()
    return api.get<ModelBrief[]>(`/models/available${query ? `?${query}` : ''}`)
  },

  /**
   * 获取单个模型
   */
  getModel: async (modelId: string): Promise<Model> => {
    return api.get<Model>(`/models/${modelId}`)
  },

  /**
   * 创建模型
   */
  createModel: async (data: ModelCreateInput): Promise<Model> => {
    return api.post<Model>('/models', data)
  },

  /**
   * 更新模型
   */
  updateModel: async (modelId: string, data: ModelUpdateInput): Promise<Model> => {
    return api.put<Model>(`/models/${modelId}`, data)
  },

  /**
   * 删除模型
   */
  deleteModel: async (modelId: string): Promise<Model> => {
    return api.delete<Model>(`/models/${modelId}`)
  },

  /**
   * 测试模型连接（已有模型）
   */
  testConnection: async (modelId: string): Promise<{ success: boolean; message: string; latency_ms?: number }> => {
    return api.post<{ success: boolean; message: string; latency_ms?: number }>(`/models/${modelId}/test`)
  },

  /**
   * 测试模型配置（创建前验证）
   */
  testModelConfig: async (data: {
    provider: string
    model_id: string
    model_type: string
    base_url?: string | null
    api_key: string
    config?: Record<string, unknown> | null
  }): Promise<{ success: boolean; message: string; latency_ms?: number }> => {
    return api.post<{ success: boolean; message: string; latency_ms?: number }>('/models/test', data)
  },

  /**
   * 设置为默认模型
   */
  setDefault: async (modelId: string): Promise<Model> => {
    return api.post<Model>(`/models/${modelId}/set-default`)
  },
}
