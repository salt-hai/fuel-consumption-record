import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import type { AxiosRequestConfig } from 'axios'
import { showToast } from 'vant'

// API 基础配置
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 原始 axios 实例
const rawInstance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 获取有效的 token（过滤掉 null、undefined 和字符串 "null"）
function getValidToken(): string | null {
  const token = localStorage.getItem('auth_token')
  if (!token || token === 'null' || token === 'undefined' || token === '""') {
    return null
  }
  return token
}

// 错误消息映射
const ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  403: '没有权限',
  404: '请求的资源不存在',
  422: '数据验证失败',
  500: '服务器错误',
  502: '网关错误',
  503: '服务维护中',
  504: '请求超时',
}

// 请求拦截器 - 添加 token
rawInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 只对需要认证的接口添加 token（登录和注册除外）
    const needsAuth = !config.url?.includes('/auth/login') && !config.url?.includes('/auth/register')

    if (needsAuth && config.headers) {
      const token = getValidToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 标记是否正在处理 401 错误（防止重复处理）
let isHandling401 = false

// 响应拦截器 - 统一处理响应和错误
rawInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    // 检查是否有标准响应格式 {code: 0, message: "xxx", data: {...}}
    if (res && typeof res === 'object' && 'code' in res) {
      // 对于认证接口（登录/注册），需要返回完整的 data（包含 token 和 user）
      // 其他接口也返回 data
      return res.data
    }
    // 如果没有标准格式，直接返回原始数据
    return res
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      const requestUrl = error.config?.url || ''

      // 401 未授权 - 清除认证信息并跳转登录
      if (status === 401) {
        // 只处理非登录/注册接口的 401 错误
        const isAuthEndpoint = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')

        if (!isAuthEndpoint && !isHandling401) {
          isHandling401 = true

          // 清除无效的认证信息
          localStorage.removeItem('auth_token')
          localStorage.removeItem('auth_user')

          // 跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }

          setTimeout(() => {
            isHandling401 = false
          }, 200)
        }

        return Promise.reject(data?.detail || data?.message || '请先登录')
      }

      // 提取错误消息
      const errorMessage = data?.message || data?.detail || ERROR_MESSAGES[status] || '请求失败'

      // 自动显示错误提示（除非是静默请求）
      const isSilent = error.config?.headers?.['X-Silent-Error']
      if (!isSilent) {
        showToast({
          message: typeof errorMessage === 'string' ? errorMessage : '请求失败',
          type: 'fail',
          duration: 2000,
        })
      }

      return Promise.reject(errorMessage)
    }

    // 网络错误
    showToast({
      message: '网络错误，请稍后重试',
      type: 'fail',
      duration: 2000,
    })

    return Promise.reject('网络错误')
  }
)

// 类型安全的 API 客户端
interface ApiClient {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T>
  patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>
}

const api: ApiClient = {
  get: (url, config) => rawInstance.get(url, config),
  post: (url, data, config) => rawInstance.post(url, data, config),
  put: (url, data, config) => rawInstance.put(url, data, config),
  delete: (url, config) => rawInstance.delete(url, config),
  patch: (url, data, config) => rawInstance.patch(url, data, config),
}

export default api
