import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 统一响应格式处理
    const data = response.data

    // 如果响应已经是包装格式（有success字段），直接返回
    if (typeof data === 'object' && data.hasOwnProperty('success')) {
      return data
    }

    // 如果是直接的数据对象（如用户注册返回的用户对象），包装成统一格式
    if (response.status >= 200 && response.status < 300) {
      return {
        success: true,
        data: data,
        message: '操作成功'
      }
    }

    return data
  },
  (error) => {
    // 不在拦截器里做硬跳转，交给各页面自己处理
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
    }

    // 统一错误格式
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.message ||
                        error.message ||
                        '请求失败'

    return Promise.reject({
      success: false,
      error: {
        message: errorMessage,
        status: error.response?.status
      }
    })
  }
)

export default apiClient
