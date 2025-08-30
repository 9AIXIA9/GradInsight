import apiClient from './apiClient'

const statsService = {
  // 获取统计数据
  async getStats() {
    try {
      const response = await apiClient.get('/api/stats')
      return response
    } catch (error) {
      throw new Error(error.response?.data?.error?.message || '获取统计数据失败')
    }
  }
}

export default statsService
