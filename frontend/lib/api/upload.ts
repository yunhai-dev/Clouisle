import { api, axiosInstance } from './client'

export interface UploadResult {
  url: string
  filename: string
  original_name: string
  size: number
  content_type: string
}

export const uploadApi = {
  /**
   * 上传图片
   */
  uploadImage: async (file: File, category: string = 'general'): Promise<UploadResult> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axiosInstance.post<{ code: number; data: UploadResult; msg: string }>(
      `/upload/image?category=${encodeURIComponent(category)}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data.data
  },

  /**
   * 上传通用文件
   */
  uploadFile: async (file: File, category: string = 'general'): Promise<UploadResult> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axiosInstance.post<{ code: number; data: UploadResult; msg: string }>(
      `/upload/file?category=${encodeURIComponent(category)}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data.data
  },

  /**
   * 删除文件
   */
  deleteFile: async (url: string): Promise<void> => {
    // 从 URL 中提取路径部分
    // 完整 URL 格式: http://localhost:8000/api/v1/upload/files/{category}/{year}/{month}/{filename}
    // 或相对路径: /api/v1/upload/files/{category}/{year}/{month}/{filename}
    let path = url
    
    // 处理完整 URL
    if (path.includes('/api/v1/upload/files/')) {
      path = path.substring(path.indexOf('/api/v1/upload/files/'))
    }
    
    // 移除前缀得到 files/{category}/{year}/{month}/{filename}
    path = path.replace('/api/v1/upload/', '')
    await api.delete<null>(`/upload/${path}`)
  },

  /**
   * 获取文件完整 URL
   */
  getFullUrl: (path: string): string => {
    if (!path) return ''
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path
    }
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
    // 移除 /api/v1 后缀，因为路径已包含
    const apiBase = baseUrl.replace('/api/v1', '')
    return `${apiBase}${path}`
  },
}
