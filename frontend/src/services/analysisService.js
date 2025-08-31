import apiClient from './apiClient'

/**
 * 内容分析服务
 */
class AnalysisService {
  
  /**
   * 执行内容分析
   * @param {Object} analysisRequest - 分析请求参数
   * @returns {Promise} 分析结果
   */
  async analyzeContent(analysisRequest) {
    try {
      // 清理空字符串，转换为null
      const cleanedRequest = {
        ...analysisRequest,
        task_id: analysisRequest.task_id && analysisRequest.task_id.trim() ? analysisRequest.task_id : null,
        keyword_filter: analysisRequest.keyword_filter && analysisRequest.keyword_filter.trim() ? analysisRequest.keyword_filter : null
      }
      
      const response = await apiClient.post('/analysis/analyze', cleanedRequest)
      return response
    } catch (error) {
      console.error('内容分析失败:', error)
      throw error
    }
  }

  /**
   * 快速分析
   * @param {string} taskId - 任务ID（可选）
   * @param {string} keyword - 关键词（可选）
   * @returns {Promise} 分析结果
   */
  async quickAnalysis(taskId = null, keyword = null) {
    try {
      const params = {}
      if (taskId) params.task_id = taskId
      if (keyword) params.keyword = keyword
      
      const response = await apiClient.post('/analysis/quick-analysis', params)
      return response
    } catch (error) {
      console.error('快速分析失败:', error)
      throw error
    }
  }

  /**
   * 获取分析历史
   * @param {number} page - 页码
   * @param {number} pageSize - 每页大小
   * @returns {Promise} 分析历史列表
   */
  async getAnalysisHistory(page = 1, pageSize = 20) {
    try {
      const response = await apiClient.get('/analysis/history', {
        params: { page, page_size: pageSize }
      })
      return response
    } catch (error) {
      console.error('获取分析历史失败:', error)
      throw error
    }
  }

  /**
   * 获取分析详情
   * @param {string} analysisId - 分析ID
   * @returns {Promise} 分析详情
   */
  async getAnalysisDetail(analysisId) {
    try {
      const response = await apiClient.get(`/analysis/${analysisId}`)
      return response
    } catch (error) {
      console.error('获取分析详情失败:', error)
      throw error
    }
  }

  /**
   * 删除分析结果
   * @param {string} analysisId - 分析ID
   * @returns {Promise} 删除结果
   */
  async deleteAnalysis(analysisId) {
    try {
      const response = await apiClient.delete(`/analysis/${analysisId}`)
      return response
    } catch (error) {
      console.error('删除分析结果失败:', error)
      throw error
    }
  }

  /**
   * 获取支持的分析类型
   * @returns {Promise} 分析类型列表
   */
  async getAnalysisTypes() {
    try {
      const response = await apiClient.get('/analysis/types')
      return response
    } catch (error) {
      console.error('获取分析类型失败:', error)
      throw error
    }
  }

  /**
   * 获取任务摘要
   * @param {string} taskId - 任务ID
   * @returns {Promise} 任务摘要
   */
  async getTaskSummary(taskId) {
    try {
      const response = await apiClient.get(`/analysis/summary/${taskId}`)
      return response
    } catch (error) {
      console.error('获取任务摘要失败:', error)
      throw error
    }
  }

  /**
   * 专项分析 - 高校分析
   * @param {string} taskId - 任务ID（可选）
   * @param {string} keyword - 关键词（可选）
   * @returns {Promise} 分析结果
   */
  async universityAnalysis(taskId = null, keyword = null) {
    const analysisRequest = {
      analysis_types: ['university_mention', 'topic_summary'],
      task_id: taskId && taskId.trim() ? taskId : null,
      keyword_filter: keyword && keyword.trim() ? keyword : null,
      min_posts: 5
    }
    return this.analyzeContent(analysisRequest)
  }

  /**
   * 专项分析 - 专业分析
   * @param {string} taskId - 任务ID（可选）
   * @param {string} keyword - 关键词（可选）
   * @returns {Promise} 分析结果
   */
  async majorAnalysis(taskId = null, keyword = null) {
    const analysisRequest = {
      analysis_types: ['major_analysis', 'keyword_extraction'],
      task_id: taskId && taskId.trim() ? taskId : null,
      keyword_filter: keyword && keyword.trim() ? keyword : null,
      min_posts: 5
    }
    return this.analyzeContent(analysisRequest)
  }

  /**
   * 专项分析 - 情感分析
   * @param {string} taskId - 任务ID（可选）
   * @param {string} keyword - 关键词（可选）
   * @returns {Promise} 分析结果
   */
  async sentimentAnalysis(taskId = null, keyword = null) {
    const analysisRequest = {
      analysis_types: ['sentiment_analysis', 'keyword_extraction'],
      task_id: taskId && taskId.trim() ? taskId : null,
      keyword_filter: keyword && keyword.trim() ? keyword : null,
      min_posts: 5
    }
    return this.analyzeContent(analysisRequest)
  }

  /**
   * 完整分析 - 包含所有分析类型
   * @param {string} taskId - 任务ID（可选）
   * @param {string} keyword - 关键词（可选）
   * @returns {Promise} 分析结果
   */
  async comprehensiveAnalysis(taskId = null, keyword = null) {
    const analysisRequest = {
      analysis_types: [
        'topic_summary',
        'content_clustering', 
        'keyword_extraction',
        'sentiment_analysis',
        'university_mention',
        'major_analysis'
      ],
      task_id: taskId && taskId.trim() ? taskId : null,
      keyword_filter: keyword && keyword.trim() ? keyword : null,
      min_posts: 5
    }
    return this.analyzeContent(analysisRequest)
  }
}

// 创建单例实例
const analysisService = new AnalysisService()

export default analysisService
