<template>
  <div class="container-fluid">
    <!-- 页面标题 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-0">
          <i class="bi bi-graph-up me-2"></i>内容分析
        </h2>
        <p class="text-muted mt-1">对高校相关帖子内容进行智能分析和洞察</p>
      </div>
      <div>
        <button class="btn btn-outline-primary me-2" @click="loadAnalysisHistory">
          <i class="bi bi-clock-history me-1"></i>分析历史
        </button>
      </div>
    </div>

    <!-- 分析类型选择 -->
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="bi bi-sliders me-2"></i>分析类型选择
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="submitAnalysis">
          <div class="mb-3">
            <label class="form-label">选择分析类型 *</label>
            <div class="row">
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="topic_summary"
                    value="topic_summary"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="topic_summary">
                    <strong>话题总结</strong> - 自动生成热门话题的摘要和观点
                  </label>
                </div>
              </div>
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="content_clustering"
                    value="content_clustering"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="content_clustering">
                    <strong>内容聚类</strong> - 将相似内容进行智能分组
                  </label>
                </div>
              </div>
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="keyword_extraction"
                    value="keyword_extraction"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="keyword_extraction">
                    <strong>关键词提取</strong> - 识别高频关键词和重要术语
                  </label>
                </div>
              </div>
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="sentiment_analysis"
                    value="sentiment_analysis"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="sentiment_analysis">
                    <strong>情感分析</strong> - 分析用户对不同话题的情感倾向
                  </label>
                </div>
              </div>
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="university_mention"
                    value="university_mention"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="university_mention">
                    <strong>高校提及分析</strong> - 统计和分析各高校的讨论情况
                  </label>
                </div>
              </div>
              <div class="col-md-6 mb-2">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="major_analysis"
                    value="major_analysis"
                    v-model="analysisForm.analysis_types"
                  >
                  <label class="form-check-label" for="major_analysis">
                    <strong>专业分析</strong> - 分析不同专业的讨论热度和发展趋势
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-4">
              <label for="site" class="form-label">数据来源</label>
              <select v-model="analysisForm.site" class="form-select" id="site">
                <option value="">所有平台</option>
                <option value="0">小红书</option>
              </select>
            </div>
            <div class="col-md-4">
              <label for="keyword" class="form-label">关键词筛选</label>
              <input
                v-model="analysisForm.keyword_filter"
                type="text"
                class="form-control"
                id="keyword"
                placeholder="可选，进一步筛选数据"
              >
            </div>
            <div class="col-md-4">
              <label for="minPosts" class="form-label">最小帖子数</label>
              <input
                v-model.number="analysisForm.min_posts"
                type="number"
                class="form-control"
                id="minPosts"
                min="1"
                placeholder="5"
              >
            </div>
          </div>

          <div class="d-grid mt-4">
            <button type="submit" class="btn btn-primary btn-lg" :disabled="analyzing || analysisForm.analysis_types.length === 0">
              <span v-if="analyzing" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-play me-2"></i>
              {{ analyzing ? '分析中...' : '开始分析' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 快速分析按钮 -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center border-primary">
          <div class="card-body">
            <i class="bi bi-lightning-charge display-4 text-primary mb-3"></i>
            <h5>快速分析</h5>
            <p class="text-muted small">一键分析热门话题、关键词和情感</p>
            <button class="btn btn-primary" @click="quickAnalysis" :disabled="analyzing">
              <i class="bi bi-zap me-1"></i>立即分析
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-success">
          <div class="card-body">
            <i class="bi bi-building display-4 text-success mb-3"></i>
            <h5>高校专项分析</h5>
            <p class="text-muted small">专门分析高校提及和讨论情况</p>
            <button class="btn btn-success" @click="universityAnalysis" :disabled="analyzing">
              <i class="bi bi-bank me-1"></i>高校分析
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-info">
          <div class="card-body">
            <i class="bi bi-mortarboard display-4 text-info mb-3"></i>
            <h5>专业趋势分析</h5>
            <p class="text-muted small">分析不同专业的讨论热度和趋势</p>
            <button class="btn btn-info" @click="majorAnalysis" :disabled="analyzing">
              <i class="bi bi-graph-up me-1"></i>专业分析
            </button>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-warning">
          <div class="card-body">
            <i class="bi bi-diagram-3 display-4 text-warning mb-3"></i>
            <h5>完整分析</h5>
            <p class="text-muted small">包含所有分析类型的深度分析</p>
            <button class="btn btn-warning" @click="comprehensiveAnalysis" :disabled="analyzing">
              <i class="bi bi-stack me-1"></i>深度分析
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-if="currentAnalysis" class="card mb-4">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">
            <i class="bi bi-bar-chart me-2"></i>分析结果
          </h5>
          <span class="badge bg-primary">{{ currentAnalysis.analysis_id }}</span>
        </div>
      </div>
      <div class="card-body">
        <!-- 分析概览 -->
        <div class="row mb-4 text-center">
          <div class="col-md-3">
            <h3 class="text-primary">{{ currentAnalysis.total_posts_analyzed || 0 }}</h3>
            <p class="text-muted mb-0">分析帖子数</p>
          </div>
          <div class="col-md-3">
            <h3 class="text-success">{{ (currentAnalysis.processing_time || 0).toFixed(2) }}s</h3>
            <p class="text-muted mb-0">处理时间</p>
          </div>
          <div class="col-md-3">
            <h3 class="text-info">{{ currentAnalysis.keyword_frequencies?.length || 0 }}</h3>
            <p class="text-muted mb-0">关键词数</p>
          </div>
          <div class="col-md-3">
            <h3 class="text-warning">{{ currentAnalysis.topic_summaries?.length || 0 }}</h3>
            <p class="text-muted mb-0">话题数</p>
          </div>
        </div>

        <!-- 分析详情标签页 -->
        <ul class="nav nav-tabs" id="analysisTab" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="keywords-tab" data-bs-toggle="tab" data-bs-target="#keywords" type="button">
              <i class="bi bi-tags me-1"></i>关键词
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="topics-tab" data-bs-toggle="tab" data-bs-target="#topics" type="button">
              <i class="bi bi-chat-text me-1"></i>话题
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="universities-tab" data-bs-toggle="tab" data-bs-target="#universities" type="button">
              <i class="bi bi-building me-1"></i>高校
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="majors-tab" data-bs-toggle="tab" data-bs-target="#majors" type="button">
              <i class="bi bi-mortarboard me-1"></i>专业
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="clusters-tab" data-bs-toggle="tab" data-bs-target="#clusters" type="button">
              <i class="bi bi-diagram-3 me-1"></i>聚类
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="insights-tab" data-bs-toggle="tab" data-bs-target="#insights" type="button">
              <i class="bi bi-lightbulb me-1"></i>洞察
            </button>
          </li>
        </ul>

        <div class="tab-content mt-3" id="analysisTabContent">
          <!-- 关键词标签页 -->
          <div class="tab-pane fade show active" id="keywords">
            <div v-if="currentAnalysis.keyword_frequencies?.length > 0" class="keyword-cloud">
              <span v-for="(kw, idx) in shuffledKeywords().slice(0, 30)" :key="kw.keyword"
                class="keyword-pill"
                :style="keywordStyle(kw, idx)">
                {{ kw.keyword }}
              </span>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-tags display-4"></i><p class="mt-2">暂无关键词数据</p>
            </div>
          </div>

          <!-- 话题标签页 -->
          <div class="tab-pane fade" id="topics">
            <div v-if="currentAnalysis.topic_summaries?.length > 0" class="row">
              <div v-for="topic in currentAnalysis.topic_summaries" :key="topic.topic" class="col-md-6 mb-3">
                <div class="card">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title mb-0">{{ topic.topic }}</h6>
                      <span class="badge" :class="getSentimentBadgeClass(topic.sentiment_trend)">
                        {{ getSentimentText(topic.sentiment_trend) }}
                      </span>
                    </div>
                    <p class="card-text text-muted small">{{ topic.summary }}</p>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <span class="badge bg-secondary">{{ topic.post_count }} 帖子</span>
                    </div>
                    <div v-if="getArray(topic.related_universities).length" class="mb-2">
                      <small class="text-muted">相关高校:</small>
                      <div class="mt-1">
                        <span v-for="uni in getArray(topic.related_universities).slice(0,5)" :key="uni" class="badge bg-light text-dark me-1 mb-1">{{ uni }}</span>
                      </div>
                    </div>
                    <div v-if="getArray(topic.related_majors).length">
                      <small class="text-muted">相关专业:</small>
                      <div class="mt-1">
                        <span v-for="major in getArray(topic.related_majors).slice(0,5)" :key="major" class="badge bg-info text-white me-1 mb-1">{{ major }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-chat-text display-4"></i>
              <p class="mt-2">暂无话题数据</p>
            </div>
          </div>

          <!-- 高校标签页 -->
          <div class="tab-pane fade" id="universities">
            <div v-if="currentAnalysis.university_mentions?.length > 0" class="row">
              <div v-for="uni in currentAnalysis.university_mentions" :key="uni.university_name" class="col-md-6 mb-3">
                <div class="card h-100 university-card">
                  <div class="card-body">
                    <h6 class="card-title mb-2">{{ uni.university_name }}</h6>
                    <div class="d-flex align-items-center mb-2">
                      <h3 class="text-primary mb-0 me-2">{{ uni.mention_count }}</h3>
                      <small class="text-muted">次提及</small>
                      <span class="ms-auto badge" :class="uni.sentiment_score > 0.2 ? 'bg-success' : uni.sentiment_score < -0.2 ? 'bg-danger' : 'bg-secondary'">
                        {{ (uni.sentiment_score > 0.2 ? '😊' : uni.sentiment_score < -0.2 ? '😟' : '😐') }} {{ (uni.sentiment_score * 100).toFixed(0) }}%
                      </span>
                    </div>
                    <div v-if="getArray(uni.related_topics).length" class="mt-2">
                      <small v-for="t in getArray(uni.related_topics).slice(0,5)" :key="t" class="badge bg-light text-dark me-1 mb-1">{{ t }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-building display-4"></i><p class="mt-2">暂无高校数据</p>
            </div>
          </div>

          <!-- 专业标签页 -->
          <div class="tab-pane fade" id="majors">
            <div v-if="currentAnalysis.major_analysis?.length > 0" class="row">
              <div v-for="major in currentAnalysis.major_analysis" :key="major.major_name" class="col-md-6 col-lg-4 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">{{ major.major_name }}</h6>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <span class="badge bg-primary">{{ major.mention_count }} 次提及</span>
                      <span class="badge" :class="getDifficultyBadgeClass(major.difficulty_level)">
                        {{ getDifficultyText(major.difficulty_level) }}
                      </span>
                    </div>
                    <div class="progress mb-2" style="height: 6px;">
                      <div class="progress-bar" 
                           :class="getJobProspectProgressClass(major.job_prospect_sentiment)"
                           :style="{ width: `${Math.abs(major.job_prospect_sentiment) * 100}%` }">
                      </div>
                    </div>
                    <small class="text-muted">就业前景评价</small>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-mortarboard display-4"></i>
              <p class="mt-2">暂无专业数据</p>
            </div>
          </div>

          <!-- 聚类标签页 -->
          <div class="tab-pane fade" id="clusters">
            <div v-if="currentAnalysis.content_clusters?.length > 0" class="row">
              <div v-for="cluster in currentAnalysis.content_clusters" :key="cluster.cluster_id" class="col-md-6 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">{{ cluster.cluster_name }}</h6>
                    <p class="card-text text-muted small">{{ cluster.cluster_summary }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <span class="badge bg-secondary">{{ cluster.post_count }} 帖子</span>
                      <span class="badge bg-info">相似度: {{ (cluster.similarity_score * 100).toFixed(1) }}%</span>
                    </div>
                    <div v-if="cluster.keywords?.length > 0" class="mt-2">
                      <small class="text-muted">关键词:</small>
                      <div class="mt-1">
                        <span v-for="keyword in cluster.keywords.slice(0, 5)" 
                              :key="keyword" 
                              class="badge bg-light text-dark me-1 mb-1">
                          {{ keyword }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-diagram-3 display-4"></i>
              <p class="mt-2">暂无聚类数据</p>
            </div>
          </div>

          <!-- 洞察标签页 -->
          <div class="tab-pane fade" id="insights">
            <div v-if="currentAnalysis.insights?.length > 0">
              <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                <strong>分析洞察</strong>
              </div>
              <ul class="list-group list-group-flush">
                <li v-for="insight in currentAnalysis.insights" :key="insight" class="list-group-item">
                  <i class="bi bi-arrow-right me-2 text-primary"></i>{{ insight }}
                </li>
              </ul>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-lightbulb display-4"></i>
              <p class="mt-2">暂无分析洞察</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析历史 -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="bi bi-clock-history me-2"></i>分析历史
        </h5>
      </div>
      <div class="card-body">
        <div v-if="analysisHistory.length === 0" class="text-center py-4">
          <i class="bi bi-inbox display-4 text-muted"></i>
          <h5 class="text-muted mt-3">暂无分析历史</h5>
          <p class="text-muted">开始您的第一次内容分析吧！</p>
        </div>
        <div v-else class="row">
          <div v-for="analysis in analysisHistory" :key="analysis.analysis_id" class="col-md-6 col-lg-4 mb-3">
            <div class="card">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">分析 #{{ analysis.analysis_id.slice(-8) }}</h6>
                  <small class="text-muted">{{ formatDate(analysis.created_at) }}</small>
                </div>
                <p class="card-text text-muted small">
                  分析了 {{ analysis.total_posts_analyzed }} 个帖子
                </p>
                <button class="btn btn-outline-primary btn-sm" @click="viewAnalysis(analysis)">
                  查看结果
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import analysisService from '@/services/analysisService'
import apiClient from '@/services/apiClient'
import { useUserStore } from '@/stores/user'
import { onMounted, reactive, ref } from 'vue'

const userStore = useUserStore()

// 响应式数据
const analyzing = ref(false)
const currentAnalysis = ref(null)
const analysisHistory = ref([])

// 分析表单（根据后端AnalysisRequest模型）
const analysisForm = reactive({
  analysis_types: [],
  site: '',
  keyword_filter: '',
  min_posts: 5
})

// 方法
const submitAnalysis = async () => {
  if (analysisForm.analysis_types.length === 0) {
    alert('请至少选择一种分析类型')
    return
  }

  analyzing.value = true

  try {
    const response = await analysisService.analyzeContent(analysisForm)

    if (response.success) {
      currentAnalysis.value = response.data

      // 重置表单
      Object.assign(analysisForm, {
        analysis_types: [],
        site: '',
        keyword_filter: '',
        min_posts: 5
      })

      // 刷新历史记录
      await loadAnalysisHistory()

      alert('分析完成！')
    } else {
      alert(response.error?.message || '分析失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const quickAnalysis = async () => {
  analyzing.value = true

  try {
    const response = await analysisService.quickAnalysis()
    if (response.success) {
      currentAnalysis.value = response.data
      await loadAnalysisHistory()
      alert('快速分析完成！')
    } else {
      alert(response.error?.message || '快速分析失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('快速分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const universityAnalysis = async () => {
  analyzing.value = true

  try {
    const response = await analysisService.universityAnalysis(analysisForm.site, analysisForm.keyword_filter)
    if (response.success) {
      currentAnalysis.value = response.data
      await loadAnalysisHistory()
      alert('高校分析完成！')
    } else {
      alert(response.error?.message || '高校分析失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('高校分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const majorAnalysis = async () => {
  analyzing.value = true

  try {
    const response = await analysisService.majorAnalysis(analysisForm.site, analysisForm.keyword_filter)
    if (response.success) {
      currentAnalysis.value = response.data
      await loadAnalysisHistory()
      alert('专业分析完成！')
    } else {
      alert(response.error?.message || '专业分析失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('专业分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const comprehensiveAnalysis = async () => {
  analyzing.value = true

  try {
    const request = {
      analysis_types: [
        'topic_summary',
        'content_clustering',
        'keyword_extraction', 
        'sentiment_analysis',
        'university_mention',
        'major_analysis'
      ],
      site: analysisForm.site,
      keyword_filter: analysisForm.keyword_filter || null,
      min_posts: 5
    }
    
    const response = await analysisService.analyzeContent(request)
    if (response.success) {
      currentAnalysis.value = response.data
      await loadAnalysisHistory()
      alert('完整分析完成！包含所有分析类型的结果。')
    } else {
      alert(response.error?.message || '完整分析失败')
    }
  } catch (err) {
    const errorMessage = err.response?.data?.detail || err.message || '网络错误，请稍后重试'
    alert(errorMessage)
    console.error('完整分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const loadAnalysisHistory = async () => {
  try {
    const response = await analysisService.getAnalysisHistory()
    if (response.success) {
      analysisHistory.value = response.data.analyses || []
    }
  } catch (err) {
    console.error('加载分析历史失败:', err)
  }
}

const viewAnalysis = async (analysis) => {
  try {
    const response = await analysisService.getAnalysisDetail(analysis.analysis_id)
    if (response.success) {
      currentAnalysis.value = response.data
    } else {
      // 如果获取详情失败，使用列表中的简化数据
      currentAnalysis.value = analysis
    }
  } catch (err) {
    console.error('获取分析详情失败:', err)
    // 如果获取详情失败，使用列表中的简化数据
    currentAnalysis.value = analysis
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 关键词云
const shuffledKeywords = () => {
  const kws = [...(currentAnalysis.value?.keyword_frequencies || [])]
  for (let i = kws.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [kws[i], kws[j]] = [kws[j], kws[i]] }
  return kws
}
const maxKeywordFreq = () => Math.max(...(currentAnalysis.value?.keyword_frequencies || []).map(k => k.frequency), 1)
const keywordStyle = (kw, idx) => {
  const ratio = kw.frequency / maxKeywordFreq()
  const size = 0.85 + ratio * 1.2  // 0.85em ~ 2.05em
  const hue = [200, 340, 160, 280, 30, 45, 190, 320, 120, 15][idx % 10]
  const sat = 50 + ratio * 20
  const light = 82 - ratio * 15
  return {
    fontSize: size + 'em',
    background: `hsl(${hue}, ${sat}%, ${light}%)`,
    color: '#444',
    animationDelay: (idx * 0.04) + 's',
    padding: `${0.3 + ratio * 0.5}em ${0.6 + ratio * 0.8}em`,
    fontWeight: ratio > 0.5 ? 600 : 400,
    marginTop: `${(Math.random() - 0.5) * 8}px`,
    boxShadow: `0 1px 2px hsl(${hue}, ${sat}%, ${light - 10}%)`,
  }
}

const getArray = (val) => {
  if (!val) return []
  if (Array.isArray(val)) return val
  if (typeof val === 'string') { try { return JSON.parse(val) } catch { return [val] } }
  return []
}
// 辅助方法
const getDifficultyBadgeClass = (difficulty) => {
  switch (difficulty) {
    case 'easy': return 'bg-success'
    case 'medium': return 'bg-warning'
    case 'hard': return 'bg-danger'
    default: return 'bg-secondary'
  }
}

const getDifficultyText = (difficulty) => {
  switch (difficulty) {
    case 'easy': return '简单'
    case 'medium': return '中等'
    case 'hard': return '困难'
    default: return '未知'
  }
}

const getJobProspectProgressClass = (sentiment) => {
  if (sentiment > 0.3) return 'bg-success'
  if (sentiment > 0) return 'bg-warning'
  if (sentiment > -0.3) return 'bg-info'
  return 'bg-danger'
}

const getSentimentBadgeClass = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'bg-success'
    case 'negative': return 'bg-danger'
    case 'neutral': return 'bg-secondary'
    default: return 'bg-light text-dark'
  }
}

const getSentimentText = (sentiment) => {
  switch (sentiment) {
    case 'positive': return '积极'
    case 'negative': return '消极'
    case 'neutral': return '中性'
    default: return sentiment
  }
}

// 生命周期
onMounted(async () => {
  await loadAnalysisHistory()
})
</script>

<style scoped>
.nav-tabs .nav-link {
  color: #6c757d;
}

.nav-tabs .nav-link.active {
  color: #0d6efd;
  border-color: #0d6efd #0d6efd #fff;
}

.tab-content {
  min-height: 300px;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.badge {
  font-size: 0.75rem;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.border-primary {
  border-color: #0d6efd !important;
}

.border-success {
  border-color: #198754 !important;
}

.border-info { border-color: #0dcaf0 !important }
.keyword-cloud { display:flex; flex-wrap:wrap; justify-content:center; align-items:center; gap:8px; padding:2rem 1rem; min-height:200px }
.keyword-pill { display:inline-block; border-radius:50px; line-height:1.3; cursor:default; transition:all .25s ease; animation:fadeInUp .4s ease both }
.keyword-pill:hover { transform:scale(1.2) !important; z-index:1; box-shadow:0 4px 15px rgba(0,0,0,.2) }
@keyframes fadeInUp { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }
.university-card { border-radius:12px; transition:box-shadow .2s }
.university-card:hover { box-shadow:0 4px 12px rgba(0,0,0,.1) }
</style>
