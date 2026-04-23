import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'

// API 基础配置
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(
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
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 后端返回格式: {code: 0, message: "xxx", data: {...}}
    // 解包返回 data 字段
    const { data } = response.data
    return data
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

export default api
