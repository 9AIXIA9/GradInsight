import apiClient from './apiClient'

const authService = {
  // 登录
  async login(credentials) {
    try {
      const response = await apiClient.post('/api/auth/login', credentials)
      return response
    } catch (error) {
      throw new Error(error.response?.data?.error?.message || '登录失败')
    }
  },

  // 注册
  async register(userData) {
    try {
      const response = await apiClient.post('/api/auth/register', userData)
      return response
    } catch (error) {
      throw new Error(error.response?.data?.error?.message || '注册失败')
    }
  },

  // 获取当前用户信息
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/api/auth/me')
      return response
    } catch (error) {
      throw new Error(error.response?.data?.error?.message || '获取用户信息失败')
    }
  },

  // 退出登录
  async logout() {
    try {
      await apiClient.post('/api/auth/logout')
    } catch (error) {
      // 退出登录失败时不抛出错误，仍然清除本地状态
      console.error('退出登录请求失败:', error)
    }
  }
}

export default authService
