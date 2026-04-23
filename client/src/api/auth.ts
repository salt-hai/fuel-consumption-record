import api from './index'

export interface RegisterRequest {
  email: string
  password: string
  name: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export interface AuthResponse {
  token: string
  user: {
    id: number
    email: string
    name: string
  }
}

// 注册
export const register = (data: RegisterRequest) => {
  return api.post<any, AuthResponse>('/v1/auth/register', data)
}

// 登录
export const login = (data: LoginRequest) => {
  return api.post<any, AuthResponse>('/v1/auth/login', data)
}

// 修改密码
export const changePassword = (data: ChangePasswordRequest) => {
  return api.put('/v1/auth/password', data)
}
