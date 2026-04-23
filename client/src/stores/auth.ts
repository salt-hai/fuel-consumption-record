import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 安全解析 localStorage，处理 "undefined" 或损坏的 JSON
  const safeGetItem = (key: string) => {
    const value = localStorage.getItem(key)
    if (!value || value === 'undefined' || value === 'null') return null
    try {
      return JSON.parse(value)
    } catch {
      return null
    }
  }

  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<any>(safeGetItem('auth_user'))
  const isAuthenticated = computed(() => !!token.value)

  // 注册
  const register = async (email: string, password: string, name: string) => {
    const res = await authApi.register({ email, password, name })
    token.value = res.token
    user.value = res.user
    localStorage.setItem('auth_token', res.token)
    localStorage.setItem('auth_user', JSON.stringify(res.user))
  }

  // 登录
  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password })
    token.value = res.token
    user.value = res.user
    localStorage.setItem('auth_token', res.token)
    localStorage.setItem('auth_user', JSON.stringify(res.user))
  }

  // 登出
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // 即使后端调用失败，也清除本地状态
      console.error('Logout API error:', error)
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    try {
      const res = await authApi.getCurrentUser()
      user.value = res
      localStorage.setItem('auth_user', JSON.stringify(res))
      return res
    } catch (error) {
      // token 可能过期，清除本地状态
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      throw error
    }
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    await authApi.changePassword({ old_password: oldPassword, new_password: newPassword })
  }

  return {
    token,
    user,
    isAuthenticated,
    register,
    login,
    logout,
    changePassword,
    fetchCurrentUser,
  }
})
