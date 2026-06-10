<template>
  <div class="container-fluid">
    <!-- 调试信息面板 -->
    <div class="alert alert-warning mb-4">
      <h6>🔍 调试信息：</h6>
      <div class="row">
        <div class="col-6">
          <strong>状态变量：</strong><br>
          loading: {{ loading }}<br>
          error: {{ error }}<br>
          hasCheckedAuth: {{ userStore.hasCheckedAuth }}<br>
          isAuthenticated: {{ userStore.isAuthenticated }}<br>
          isAdmin: {{ userStore.isAdmin }}
        </div>
        <div class="col-6">
          <strong>用户信息：</strong><br>
          username: {{ userStore.user?.username || 'null' }}<br>
          role: {{ userStore.user?.role || 'null' }}<br>
          token: {{ userStore.token ? '存在' : '不存在' }}
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="d-flex justify-content-center align-items-center" style="min-height: 400px;">
      <div class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-3 text-muted">正在加载爬虫管理页面...</p>
        <small class="text-muted">如果长时间停留在此状态，请检查控制台错误</small>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
      <button type="button" class="btn btn-sm btn-outline-danger ms-3" @click="handleRetry">
        重新加载
      </button>
    </div>

    <!-- 正常内容 -->
    <div v-else>
      <div class="alert alert-success">
        ✅ 页面加载成功！用户权限验证通过。
      </div>

      <!-- 页面标题 -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="mb-0">
            <i class="bi bi-robot me-2"></i>爬虫管理
          </h2>
          <p class="text-muted mt-1">启动小红书高校数据爬虫任务</p>
        </div>
        <div>
          <button class="btn btn-outline-primary me-2" @click="refreshStatus" :disabled="refreshing">
            <span v-if="refreshing" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-arrow-clockwise me-1"></i>
            {{ refreshing ? '刷新中...' : '刷新状态' }}
          </button>
        </div>
      </div>

      <!-- 用户和权限信息 -->
      <div class="alert alert-info mb-4">
        <strong>当前用户：</strong>{{ userStore.user?.username || '未登录' }}
        <span v-if="userStore.user">({{ userStore.user.role }})</span>
        <br>
        <strong>认证状态：</strong>{{ userStore.isAuthenticated ? '已认证' : '未认证' }}
        <br>
        <strong>管理员权限：</strong>{{ userStore.isAdmin ? '是' : '否' }}
      </div>

      <!-- 爬虫配置表单 -->
      <div class="row">
        <div class="col-lg-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-gear me-2"></i>爬虫配置
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="startCrawl">
                <div class="mb-3">
                  <label for="keyword" class="form-label">搜索关键词 *</label>
                  <input
                    v-model="crawlConfig.keyword"
                    type="text"
                    class="form-control"
                    id="keyword"
                    placeholder="例如：南昌大学、计算机科学、人工智能"
                    required
                  >
                  <div class="form-text">请输入您要搜索的高校名称或专业名称</div>
                </div>

                <div class="mb-3">
                  <label for="site" class="form-label">爬取平台</label>
                  <select v-model="crawlConfig.site" class="form-select" id="site">
                    <option value="0">小红书</option>
                  </select>
                  <div class="form-text">目前仅支持小红书平台</div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <label for="postCount" class="form-label">帖子数量</label>
                    <input
                      v-model.number="crawlConfig.post_count"
                      type="number"
                      class="form-control"
                      id="postCount"
                      min="5"
                      max="50"
                    >
                    <div class="form-text">范围：5-50</div>
                  </div>
                  <div class="col-md-6">
                    <label for="minLikes" class="form-label">最少点赞数</label>
                    <input
                      v-model.number="crawlConfig.min_likes"
                      type="number"
                      class="form-control"
                      id="minLikes"
                      min="0"
                    >
                    <div class="form-text">过滤低赞帖子</div>
                  </div>
                </div>

                <div class="form-check mb-3 mt-3">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="crawlConfig.include_comments"
                    id="includeComments"
                  >
                  <label class="form-check-label" for="includeComments">
                    包含评论数据
                  </label>
                </div>

                <div v-if="crawlConfig.include_comments" class="row">
                  <div class="col-md-6">
                    <label for="commentsPerPost" class="form-label">每帖评论数</label>
                    <input
                      v-model.number="crawlConfig.comments_per_post"
                      type="number"
                      class="form-control"
                      id="commentsPerPost"
                      min="1"
                      max="30"
                    >
                    <div class="form-text">范围：1-30</div>
                  </div>
                  <div class="col-md-6">
                    <label for="commentMinLikes" class="form-label">评论最少赞数</label>
                    <input
                      v-model.number="crawlConfig.comment_min_likes"
                      type="number"
                      class="form-control"
                      id="commentMinLikes"
                      min="0"
                    >
                    <div class="form-text">过滤低赞评论</div>
                  </div>
                </div>

                <div class="form-check mb-4">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="crawlConfig.include_images"
                    id="includeImages"
                  >
                  <label class="form-check-label" for="includeImages">
                    包含图片URL（可能增加爬取时间）
                  </label>
                </div>

                <div class="d-grid">
                  <button type="submit" class="btn btn-primary btn-lg" :disabled="crawling">
                    <span v-if="crawling" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-play-fill me-2"></i>
                    {{ crawling ? '爬取中...' : '开始爬取' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <!-- 爬虫状态 -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>爬虫状态
              </h5>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-6">
                  <div class="p-3 border rounded">
                    <i class="bi bi-server display-6" :class="serviceConnected ? 'text-success' : 'text-danger'"></i>
                    <h6 class="mt-2">服务状态</h6>
                    <span class="badge" :class="serviceConnected ? 'bg-success' : 'bg-danger'">
                      {{ serviceConnected ? '已连接' : '连接断开' }}
                    </span>
                  </div>
                </div>
                <div class="col-6">
                  <div class="p-3 border rounded">
                    <i class="bi bi-activity display-6 text-info"></i>
                    <h6 class="mt-2">运行状态</h6>
                    <span class="badge" :class="crawling ? 'bg-primary' : 'bg-secondary'">
                      {{ crawling ? '爬取中' : '空闲' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 最近任务 -->
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-clock-history me-2"></i>最近任务
              </h5>
            </div>
            <div class="card-body">
              <div v-if="recentTasks.length === 0" class="text-center text-muted py-3">
                <i class="bi bi-inbox display-4"></i>
                <p class="mt-2">暂无任务记录</p>
              </div>
              <div v-else>
                <div v-for="task in recentTasks.slice(0, 5)" :key="task.id" class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                  <div>
                    <div class="fw-medium">{{ task.keyword }}</div>
                    <small class="text-muted">{{ formatDate(task.created_at) }}</small>
                  </div>
                  <div>
                    <span class="badge" :class="getStatusClass(task.status)">
                      {{ getStatusText(task.status) }}
                    </span>
                  </div>
                </div>
                <div class="text-center mt-3">
                  <router-link to="/tasks" class="btn btn-sm btn-outline-primary">
                    查看全部任务
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 成功提示模态框 -->
      <div class="modal fade" :class="{ show: showSuccessModal }" :style="{ display: showSuccessModal ? 'block' : 'none' }" @click.self="showSuccessModal = false">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="bi bi-check-circle-fill text-success me-2"></i>爬取任务启动成功
              </h5>
              <button type="button" class="btn-close" @click="showSuccessModal = false"></button>
            </div>
            <div class="modal-body" v-if="lastResult">
              <div class="alert alert-success">
                <strong>任务ID：</strong><code>{{ lastResult.task_id }}</code>
              </div>
              <p><strong>搜索关键词：</strong>{{ lastResult.keyword || crawlConfig.keyword }}</p>
              <p><strong>目标帖子数：</strong>{{ crawlConfig.post_count }}</p>
              <p><strong>任务状态：</strong>{{ lastResult.message }}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showSuccessModal = false">关闭</button>
              <router-link to="/tasks" class="btn btn-primary" @click="showSuccessModal = false">
                查看任务
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 模态框背景 -->
      <div v-if="showSuccessModal" class="modal-backdrop fade show"></div>
    </div>
  </div>
</template>

<script setup>
import apiClient from '@/services/apiClient'
import { useUserStore } from '@/stores/user'
import { onMounted, reactive, ref } from 'vue'

const userStore = useUserStore()

// 响应式数据
const crawling = ref(false)
const serviceConnected = ref(false)
const showSuccessModal = ref(false)
const lastResult = ref(null)
const recentTasks = ref([])
const loading = ref(true)
const error = ref(null)
const refreshing = ref(false)

// 爬虫配置（根据后端CrawlRequest模型）
const crawlConfig = reactive({
  keyword: '南昌大学',
  site: 0,
  post_count: 10,
  include_comments: true,
  min_likes: 0,
  comments_per_post: 10,
  comment_min_likes: 5,
  include_images: true
})

// 方法
const handleRetry = () => {
  window.location.reload()
}

const startCrawl = async () => {
  if (!crawlConfig.keyword.trim()) {
    alert('请输入搜索关键词')
    return
  }

  crawling.value = true

  try {
    const response = await apiClient.post('/api/crawler/start', crawlConfig)

    if (response.success) {
      lastResult.value = response.data
      showSuccessModal.value = true

  // 重新加载最近任务
      await loadRecentTasks()
    } else {
      alert(response.error?.message || '启动爬虫任务失败')
    }
  } catch (err) {
    console.error('启动爬虫错误:', err)
    const errorMsg = err.error?.message || err.message || '网络错误，请稍后重试'
    alert(errorMsg)
  } finally {
    crawling.value = false
  }
}

const refreshStatus = async () => {
  refreshing.value = true
  try {
    const response = await apiClient.get('/api/crawler/status')

    console.log('爬虫服务状态响应:', response)

    // 修复状态判断逻辑
    if (response.success) {
      // 检查服务状态
      const status = response.status || response.data?.status
      const isHealthy = status === 'HEALTHY' ||
                       (response.healthy_instances > 0) ||
                       response.check_method === 'direct_tcp'

      serviceConnected.value = isHealthy

      console.log('服务状态判断结果:', {
        status,
        healthy_instances: response.healthy_instances,
        check_method: response.check_method,
        serviceConnected: serviceConnected.value,
        message: response.message
      })
    } else {
      serviceConnected.value = false
      console.log('服务状态检查失败:', response.message)
    }
  } catch (err) {
    serviceConnected.value = false
    console.error('获取服务状态失败:', err)
  } finally {
    refreshing.value = false
  }
}

const loadRecentTasks = async () => {
  try {
    const response = await apiClient.get('/api/crawler/tasks', {
      params: { limit: 10 }
    })

    if (response.success) {
      recentTasks.value = response.data.items || []
    }
  } catch (err) {
    console.error('加载最近任务失败:', err)
    // 不阻止页面加载，只是记录错误
  }
}

const getStatusClass = (status) => {
  const statusMap = {
    0: 'bg-success',    // 已完成
    1: 'bg-primary',    // 运行中
    2: 'bg-danger',     // 失败
    3: 'bg-warning'     // 已停止
  }
  return statusMap[status] || 'bg-secondary'
}

const getStatusText = (status) => {
  const statusMap = {
    0: '已完成',
    1: '运行中',
    2: '失败',
    3: '已停止'
  }
  return statusMap[status] || '未知'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// 生命周期
onMounted(async () => {
  console.log('=== Crawler页面开始初始化 ===')
  loading.value = true
  error.value = null

  try {
    // 首先检查用户状态
    console.log('1. 检查用户状态:', {
      hasCheckedAuth: userStore.hasCheckedAuth,
      isAuthenticated: userStore.isAuthenticated,
      isAdmin: userStore.isAdmin,
      user: userStore.user
    })

    // 等待用户状态检查完成，但设置超时
    let attempts = 0
    const maxAttempts = 30 // 减少等待时间到3秒

    while (!userStore.hasCheckedAuth && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 100))
      attempts++
    }

    console.log('2. 用户状态检查完成:', {
      attempts,
      hasCheckedAuth: userStore.hasCheckedAuth,
      isAuthenticated: userStore.isAuthenticated,
      isAdmin: userStore.isAdmin
    })

    // 如果用户没有管理员权限，显示错误信息
    if (!userStore.isAuthenticated) {
      error.value = '请先登录系统'
      console.log('用户未登录')
      return
    }

    if (!userStore.isAdmin) {
      error.value = '您没有访问此页面的权限，需要管理员权限'
      console.log('用户非管理员')
      return
    }

    console.log('3. 开始加载页面数据...')

    // 使用Promise.allSettled来防止任何一个请求失败阻塞页面
    const results = await Promise.allSettled([
      refreshStatus(),
      loadRecentTasks()
    ])

    console.log('4. 页面数据加载结果:', results)

    // 检查加载结果
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        console.warn(`请求 ${index} 失败:`, result.reason)
      }
    })

    console.log('=== Crawler页面初始化完成 ===')

  } catch (err) {
    console.error('页面初始化失败:', err)
    error.value = '页面加载失败，请刷新重试'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.modal.show {
  display: block !important;
}

.form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
  border-color: #0d6efd;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.border {
  border-color: #dee2e6 !important;
}

.badge {
  font-size: 0.75rem;
}
</style>
