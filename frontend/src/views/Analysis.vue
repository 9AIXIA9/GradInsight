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
              <label for="taskId" class="form-label">数据来源</label>
              <select v-model="analysisForm.task_id" class="form-select" id="taskId">
                <option value="">所有数据</option>
                <option v-for="task in availableTasks" :key="task.id" :value="task.id">
                  {{ task.keyword }} ({{ task.posts_collected || 0 }} 帖子)
                </option>
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
      <div class="col-md-4">
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
      <div class="col-md-4">
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
      <div class="col-md-4">
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
            <button class="nav-link" id="insights-tab" data-bs-toggle="tab" data-bs-target="#insights" type="button">
              <i class="bi bi-lightbulb me-1"></i>洞察
            </button>
          </li>
        </ul>

        <div class="tab-content mt-3" id="analysisTabContent">
          <!-- 关键词标签页 -->
          <div class="tab-pane fade show active" id="keywords">
            <div v-if="currentAnalysis.keyword_frequencies?.length > 0" class="row">
              <div v-for="keyword in currentAnalysis.keyword_frequencies.slice(0, 20)" :key="keyword.keyword" class="col-md-6 col-lg-4 mb-2">
                <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded">
                  <span class="fw-medium">{{ keyword.keyword }}</span>
                  <span class="badge bg-primary">{{ keyword.frequency }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-tags display-4"></i>
              <p class="mt-2">暂无关键词数据</p>
            </div>
          </div>

          <!-- 话题标签页 -->
          <div class="tab-pane fade" id="topics">
            <div v-if="currentAnalysis.topic_summaries?.length > 0" class="row">
              <div v-for="topic in currentAnalysis.topic_summaries" :key="topic.topic" class="col-md-6 mb-3">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">{{ topic.topic }}</h6>
                    <p class="card-text text-muted small">{{ topic.summary }}</p>
                    <span class="badge bg-secondary">{{ topic.post_count }} 帖子</span>
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
              <div v-for="uni in currentAnalysis.university_mentions" :key="uni.university_name" class="col-md-6 col-lg-4 mb-3">
                <div class="card text-center">
                  <div class="card-body">
                    <h6 class="card-title">{{ uni.university_name }}</h6>
                    <h4 class="text-primary">{{ uni.mention_count }}</h4>
                    <p class="text-muted mb-0">提及次数</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-building display-4"></i>
              <p class="mt-2">暂无高校数据</p>
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
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import apiClient from '@/services/apiClient'

const userStore = useUserStore()

// 响应式数据
const analyzing = ref(false)
const currentAnalysis = ref(null)
const analysisHistory = ref([])
const availableTasks = ref([])

// 分析表单（根据后端AnalysisRequest模型）
const analysisForm = reactive({
  analysis_types: [],
  task_id: '',
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
    const response = await apiClient.post('/analysis/analyze', analysisForm)

    if (response.success) {
      currentAnalysis.value = response.data

      // 重置表单
      Object.assign(analysisForm, {
        analysis_types: [],
        task_id: '',
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
    alert('网络错误，请稍后重试')
    console.error('分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const quickAnalysis = async () => {
  analyzing.value = true

  try {
    const response = await apiClient.post('/analysis/quick-analysis')
    if (response.success) {
      currentAnalysis.value = response.data
      alert('快速分析完成！')
    } else {
      alert(response.error?.message || '快速分析失败')
    }
  } catch (err) {
    alert('网络错误，请稍后重试')
    console.error('快速分析错误:', err)
  } finally {
    analyzing.value = false
  }
}

const universityAnalysis = () => {
  analysisForm.analysis_types = ['university_mention', 'topic_summary']
  submitAnalysis()
}

const majorAnalysis = () => {
  analysisForm.analysis_types = ['major_analysis', 'keyword_extraction']
  submitAnalysis()
}

const loadAnalysisHistory = async () => {
  try {
    const response = await apiClient.get('/analysis/history')
    if (response.success) {
      analysisHistory.value = response.data.items || []
    }
  } catch (err) {
    console.error('加载分析历史失败:', err)
  }
}

const loadTasks = async () => {
  try {
    const response = await apiClient.get('/api/crawler/tasks', {
      params: { limit: 50, status: 0 } // 只加载已完成的任务
    })
    if (response.success) {
      availableTasks.value = response.data.items || []
    }
  } catch (err) {
    console.error('加载任务列表失败:', err)
  }
}

const viewAnalysis = (analysis) => {
  currentAnalysis.value = analysis
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

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadAnalysisHistory(),
    loadTasks()
  ])
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

.border-info {
  border-color: #0dcaf0 !important;
}
</style>
