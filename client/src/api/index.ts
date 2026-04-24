import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import type { AxiosRequestConfig } from 'axios'

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

// 请求拦截器 - 添加 token
rawInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一处理响应和错误
rawInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // 后端返回格式: {code: 0, message: "xxx", data: {...}}
    // 解包返回 data 字段
    const res = response.data
    // 检查是否有标准响应格式
    if (res && typeof res === 'object' && 'code' in res) {
      return res.data
    }
    // 如果没有标准格式，直接返回原始数据
    return res
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response

      // 401 未授权 - 跳转登录
      if (status === 401) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        window.location.href = '/login'
      }

      // 返回错误信息
      return Promise.reject(data?.detail || data?.message || '请求失败')
    }

    return Promise.reject('网络错误，请稍后重试')
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
