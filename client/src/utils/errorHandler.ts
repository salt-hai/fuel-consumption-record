import { showToast } from 'vant'

// 错误类型
export interface ApiError {
  code?: number
  message?: string
  detail?: string
  data?: unknown
}

// 错误消息映射
const ERROR_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '请先登录',
  403: '没有权限',
  404: '请求的资源不存在',
  422: '数据验证失败',
  500: '服务器错误',
  502: '网关错误',
  503: '服务维护中',
  504: '请求超时',
}

/**
 * 从错误对象中提取错误消息
 */
function extractErrorMessage(error: unknown): string {
  // Axios 错误响应
  if (error && typeof error === 'object' && 'response' in error) {
    const err = error as { response: { data?: ApiError; status?: number } }
    const data = err.response.data
    const status = err.response.status

    // 后端统一格式 {code, message, data}
    if (data?.message) {
      return data.message as string
    }

    // FastAPI 默认错误格式 {detail}
    if (data?.detail) {
      return typeof data.detail === 'string' ? data.detail : '请求失败'
    }

    // 根据 HTTP 状态码返回默认消息
    if (status && ERROR_MESSAGES[status]) {
      return ERROR_MESSAGES[status]
    }
  }

  // 直接是错误对象
  if (error && typeof error === 'object') {
    const err = error as ApiError

    if (err.message) {
      return err.message
    }

    if (err.detail) {
      return typeof err.detail === 'string' ? err.detail : '请求失败'
    }
  }

  // 字符串错误
  if (typeof error === 'string') {
    return error
  }

  return '操作失败，请稍后重试'
}

/**
 * 显示错误提示（Toast）
 */
export function showError(error: unknown, duration = 2000): void {
  const message = extractErrorMessage(error)
  showToast({
    message,
    type: 'fail',
    duration,
  })
}

/**
 * 显示成功提示（Toast）
 */
export function showSuccess(message: string, duration = 1500): void {
  showToast({
    message,
    type: 'success',
    duration,
  })
}

/**
 * 显示加载提示（Toast）
 */
export function showLoading(message = '加载中...'): void {
  showToast({
    message,
    type: 'loading',
    duration: 0, // 不会自动关闭
    forbidClick: true,
  })
}

/**
 * 关闭所有提示
 */
export function closeToast(): void {
  showToast({
    message: '',
    duration: 1,
  })
}

/**
 * 异步操作包装器 - 自动处理错误和加载状态
 */
export async function withLoading<T>(
  asyncFn: () => Promise<T>,
  loadingMessage = '加载中...'
): Promise<T> {
  showLoading(loadingMessage)
  try {
    const result = await asyncFn()
    closeToast()
    return result
  } catch (error) {
    closeToast()
    showError(error)
    throw error
  }
}

/**
 * 异步操作包装器 - 自动处理错误和成功提示
 */
export async function withAutoToast<T>(
  asyncFn: () => Promise<T>,
  options: {
    loading?: string
    success?: string
    error?: string
  } = {}
): Promise<T> {
  const { loading = '加载中...', success, error } = options

  showLoading(loading)
  try {
    const result = await asyncFn()
    closeToast()
    if (success) {
      showSuccess(success)
    }
    return result
  } catch (err) {
    closeToast()
    if (error) {
      showToast({ message: error, type: 'fail' })
    } else {
      showError(err)
    }
    throw err
  }
}
