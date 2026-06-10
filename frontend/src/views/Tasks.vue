<template>
  <div class="container-fluid">
    <!-- 页面标题 -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="mb-0">
          <i class="bi bi-list-task me-2"></i>任务管理
        </h2>
        <p class="text-muted mt-1">查看和管理所有爬虫任务</p>
      </div>
      <div>
        <button class="btn btn-outline-primary me-2" @click="refreshTasks">
          <i class="bi bi-arrow-clockwise me-1"></i>刷新
        </button>
        <router-link to="/crawler" class="btn btn-primary">
          <i class="bi bi-plus-lg me-1"></i>新建任务
        </router-link>
      </div>
    </div>

    <!-- 状态卡片 -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center border-success">
          <div class="card-body">
            <i class="bi bi-check-circle-fill display-4 text-success"></i>
            <h4 class="text-success mt-2">{{ statistics.completed }}</h4>
            <p class="text-muted mb-0">已完成</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-primary">
          <div class="card-body">
            <i class="bi bi-play-circle-fill display-4 text-primary"></i>
            <h4 class="text-primary mt-2">{{ statistics.running }}</h4>
            <p class="text-muted mb-0">运行中</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-danger">
          <div class="card-body">
            <i class="bi bi-x-circle-fill display-4 text-danger"></i>
            <h4 class="text-danger mt-2">{{ statistics.failed }}</h4>
            <p class="text-muted mb-0">失败</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center border-warning">
          <div class="card-body">
            <i class="bi bi-pause-circle-fill display-4 text-warning"></i>
            <h4 class="text-warning mt-2">{{ statistics.stopped }}</h4>
            <p class="text-muted mb-0">已停止</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">状态筛选</label>
            <select v-model="filters.status" class="form-select" @change="applyFilters">
              <option value="">全部状态</option>
              <option value="0">已完成</option>
              <option value="1">失败</option>
              <option value="2">运行中</option>
              <option value="3">已停止</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">关键词搜索</label>
            <div class="input-group">
              <input
                v-model="filters.keyword"
                type="text"
                class="form-control"
                placeholder="搜索任务关键词..."
                @keyup.enter="applyFilters"
              >
              <button class="btn btn-outline-secondary" @click="applyFilters">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-clockwise me-1"></i>重置
            </button>
          </div>
          <div class="col-md-3 d-flex align-items-end">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="debugMode" id="debugMode">
              <label class="form-check-label" for="debugMode">
                调试模式
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 调试信息 -->
    <div v-if="debugMode" class="alert alert-info mb-4">
      <h6><i class="bi bi-bug me-2"></i>调试信息</h6>
      <div class="row">
        <div class="col-md-6">
          <strong>用户状态:</strong> {{ userStore.isAuthenticated ? '已登录' : '未登录' }}<br>
          <strong>管理员权限:</strong> {{ userStore.isAdmin ? '是' : '否' }}<br>
          <strong>API地址:</strong> {{ apiBaseUrl }}
        </div>
        <div class="col-md-6">
          <strong>任务总数:</strong> {{ taskList.length }}<br>
          <strong>页面状态:</strong> {{ loading ? '加载中' : '就绪' }}<br>
          <strong>错误信息:</strong> {{ errorMessage || '无' }}
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="bi bi-table me-2"></i>任务列表 (共 {{ taskList.length }} 个任务)
        </h5>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="card-body text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">加载中...</span>
        </div>
        <p class="mt-3 text-muted">正在加载任务数据...</p>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="errorMessage" class="card-body">
        <div class="alert alert-danger" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>
          <strong>加载失败:</strong>{{ errorMessage }}
          <div class="mt-3">
            <button class="btn btn-outline-danger btn-sm me-2" @click="refreshTasks">
              重新加载
            </button>
            <button class="btn btn-outline-secondary btn-sm" @click="loadMockData">
              加载示例数据
            </button>
          </div>
        </div>
      </div>

      <!-- 任务列表 -->
      <div v-else class="card-body p-0">
        <!-- 空状态 -->
        <div v-if="filteredTasks.length === 0" class="text-center py-5">
          <i class="bi bi-inbox display-4 text-muted"></i>
          <h5 class="text-muted mt-3">暂无任务数据</h5>
          <p class="text-muted">
            {{ taskList.length === 0 ? '还没有创建任何任务' : '没有符合筛选条件的任务' }}
          </p>
          <div class="mt-3">
            <router-link to="/crawler" class="btn btn-primary me-2">
              <i class="bi bi-plus-lg me-1"></i>创建新任务
            </router-link>
            <button v-if="taskList.length === 0" class="btn btn-outline-secondary" @click="loadMockData">
              加载示例数据
            </button>
          </div>
        </div>

        <!-- 任务表格 -->
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th style="width: 100px;">任务ID</th>
                <th style="width: 120px;">关键词</th>
                <th style="width: 80px;">平台</th>
                <th style="width: 100px;">状态</th>
                <th style="width: 120px;">进度</th>
                <th style="width: 80px;">帖子数</th>
                <th style="width: 140px;">创建时间</th>
                <th style="width: 160px;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in paginatedTasks" :key="task.id">
                <td>
                  <code class="text-primary">{{ task.id.slice(0, 8) }}...</code>
                </td>
                <td>
                  <span class="fw-medium">{{ task.keyword }}</span>
                </td>
                <td>
                  <span class="badge bg-info">{{ formatSiteName(task.site) }}</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadgeClass(task.status)">
                    <i :class="getStatusIcon(task.status)" class="me-1"></i>
                    {{ getStatusText(task.status) }}
                  </span>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="progress me-2" style="width: 80px; height: 6px;">
                      <div
                        class="progress-bar"
                        :class="getProgressBarClass(task.status)"
                        :style="{ width: calculateProgress(task) + '%' }"
                      ></div>
                    </div>
                    <small class="text-muted">{{ calculateProgress(task) }}%</small>
                  </div>
                </td>
                <td>
                  <span class="text-info fw-medium">{{ task.posts_collected || 0 }}</span>
                </td>
                <td>
                  <small class="text-muted">{{ formatDateTime(task.created_at) }}</small>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button
                      class="btn btn-outline-primary"
                      @click="showTaskDetail(task)"
                      title="查看详情"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button
                      v-if="task.status === 2"
                      class="btn btn-outline-warning"
                      @click="stopTask(task.id)"
                      title="停止任务"
                    >
                      <i class="bi bi-stop-fill"></i>
                    </button>
                    <button
                      class="btn btn-outline-success"
                      @click="viewTaskPosts(task.id)"
                      title="查看帖子"
                      :disabled="!task.posts_collected"
                    >
                      <i class="bi bi-postcard"></i>
                    </button>
                    <button
                      class="btn btn-outline-danger"
                      @click="deleteTask(task.id)"
                      title="删除任务"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="card-footer">
        <nav>
          <ul class="pagination justify-content-center mb-0">
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
              <button class="page-link" @click="changePage(currentPage - 1)">
                <i class="bi bi-chevron-left"></i>
              </button>
            </li>

            <li v-for="page in visiblePageNumbers" :key="page" class="page-item"
                :class="{ active: page === currentPage }">
              <button class="page-link" @click="changePage(page)">{{ page }}</button>
            </li>

            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
              <button class="page-link" @click="changePage(currentPage + 1)">
                <i class="bi bi-chevron-right"></i>
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- 任务详情模态框 -->
    <div v-if="showModal" class="modal fade show" style="display: block;" @click.self="closeModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-info-circle me-2"></i>任务详情
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedTask">
            <div class="row">
              <div class="col-md-6">
                <h6>基本信息</h6>
                <table class="table table-borderless table-sm">
                  <tbody>
                    <tr>
                      <td class="text-muted" style="width: 80px;">任务ID:</td>
                      <td><code>{{ selectedTask.id }}</code></td>
                    </tr>
                    <tr>
                      <td class="text-muted">关键词:</td>
                      <td><strong>{{ selectedTask.keyword }}</strong></td>
                    </tr>
                    <tr>
                      <td class="text-muted">状态:</td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(selectedTask.status)">
                          {{ getStatusText(selectedTask.status) }}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td class="text-muted">平台:</td>
                      <td>{{ formatSiteName(selectedTask.site) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="col-md-6">
                <h6>统计信息</h6>
                <table class="table table-borderless table-sm">
                  <tbody>
                    <tr>
                      <td class="text-muted" style="width: 100px;">收集帖子:</td>
                      <td><strong class="text-info">{{ selectedTask.posts_collected || 0 }}</strong></td>
                    </tr>
                    <tr>
                      <td class="text-muted">创建时间:</td>
                      <td>{{ formatDateTime(selectedTask.created_at) }}</td>
                    </tr>
                    <tr>
                      <td class="text-muted">完成时间:</td>
                      <td>{{ formatDateTime(selectedTask.completed_at) || '-' }}</td>
                    </tr>
                    <tr>
                      <td class="text-muted">更新时间:</td>
                      <td>{{ formatDateTime(selectedTask.updated_at) || '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-if="selectedTask.error_message" class="mt-3">
              <h6>错误信息</h6>
              <div class="alert alert-danger">
                {{ selectedTask.error_message }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">关闭</button>
            <button
              type="button"
              class="btn btn-primary"
              @click="viewTaskPosts(selectedTask.id)"
              :disabled="!selectedTask?.posts_collected"
            >
              <i class="bi bi-postcard me-1"></i>查看帖子
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模态框背景 -->
    <div v-if="showModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import apiClient from '@/services/apiClient'
import { useUserStore } from '@/stores/user'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

// 基础状态
const loading = ref(false)
const errorMessage = ref('')
const debugMode = ref(false)
const showModal = ref(false)
const selectedTask = ref(null)

// 数据状态
const taskList = ref([])
const statistics = reactive({
  completed: 0,
  running: 0,
  failed: 0,
  stopped: 0
})

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选状态
const filters = reactive({
  status: '',
  keyword: ''
})

// 计算属性
const apiBaseUrl = computed(() => import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')

// 筛选后的任务列表
const filteredTasks = computed(() => {
  let filtered = taskList.value

  // 状态筛选
  if (filters.status !== '') {
    const statusNum = parseInt(filters.status)
    filtered = filtered.filter(task => task.status === statusNum)
  }

  // 关键词筛选
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    filtered = filtered.filter(task => 
      task.keyword.toLowerCase().includes(keyword) ||
      task.id.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

// 分页后的任务列表
const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTasks.value.slice(start, end)
})

// 总页数
const totalPages = computed(() => Math.ceil(filteredTasks.value.length / pageSize.value))

// 可见的页码
const visiblePageNumbers = computed(() => {
  const current = currentPage.value
  const total = totalPages.value
  const delta = 2

  let start = Math.max(1, current - delta)
  let end = Math.min(total, current + delta)

  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4)
    } else {
      start = Math.max(1, end - 4)
    }
  }

  return Array.from({ length: end - start + 1 }, (_, i) => start + i)
})

// 格式化函数
const getStatusText = (status) => {
  const statusMap = {
    0: '已完成',
    1: '失败',
    2: '运行中',
    3: '已停止',
    4: '等待中'
  }
  return statusMap[status] || '未知'
}

const getStatusBadgeClass = (status) => {
  const classMap = {
    0: 'bg-success',
    1: 'bg-danger',
    2: 'bg-primary',
    3: 'bg-warning',
    4: 'bg-secondary'
  }
  return classMap[status] || 'bg-secondary'
}

const getStatusIcon = (status) => {
  const iconMap = {
    0: 'bi-check-circle-fill',
    1: 'bi-x-circle-fill',
    2: 'bi-play-circle-fill',
    3: 'bi-pause-circle-fill',
    4: 'bi-clock-fill'
  }
  return iconMap[status] || 'bi-question-circle-fill'
}

const getProgressBarClass = (status) => {
  const classMap = {
    0: 'bg-success',
    1: 'bg-danger',
    2: 'bg-primary',
    3: 'bg-warning',
    4: 'bg-secondary'
  }
  return classMap[status] || 'bg-secondary'
}

const formatSiteName = (site) => {
  const siteMap = {
    0: '小红书',
    'xiaohongshu': '小红书',
    'weibo': '微博',
    'zhihu': '知乎'
  }
  return siteMap[site] || ('平台' + site)
}

const calculateProgress = (task) => {
  if (task.status === 0) return 100
  if (task.status === 2) {
    const collected = task.posts_collected || 0
    const target = task.post_count || 100
    return Math.min(90, Math.floor((collected / target) * 100))
  }
  if (task.status === 1 || task.status === 3) {
    return task.posts_collected ? 50 : 0
  }
  return 0
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// 统计计算
const calculateStatistics = () => {
  statistics.completed = taskList.value.filter(t => t.status === 0).length
  statistics.running = taskList.value.filter(t => t.status === 2).length
  statistics.failed = taskList.value.filter(t => t.status === 1).length
  statistics.stopped = taskList.value.filter(t => t.status === 3 || t.status === 4).length
}

// 数据加载
const loadTasksFromAPI = async () => {
  try {
    console.log('开始从API加载任务数据...')
    loading.value = true
    errorMessage.value = ''

    const params = {
      skip: 0,
      limit: 100
    }

    const response = await apiClient.get('/api/crawler/tasks', { params })
    console.log('API响应:', response)

    if (response && response.success && response.data) {
      taskList.value = response.data.tasks || []
      calculateStatistics()
      console.log('任务数据加载成功:', taskList.value.length)
    } else {
      throw new Error(response?.error?.message || '获取任务列表失败')
    }
  } catch (error) {
    console.error('加载任务数据失败:', error)
    errorMessage.value = error.message || '网络错误，无法加载任务数据'
  } finally {
    loading.value = false
  }
}

// 加载示例数据
const loadMockData = () => {
  console.log('加载示例数据...')
  taskList.value = [
    {
      id: 'task_001_xiaohongshu_research',
      keyword: '大学生活',
      site: 'xiaohongshu',
      status: 0,
      posts_collected: 156,
      post_count: 200,
      created_at: '2024-08-30T10:30:00',
      completed_at: '2024-08-30T11:45:00',
      updated_at: '2024-08-30T11:45:00'
    },
    {
      id: 'task_002_weibo_trending',
      keyword: '高校生活',
      site: 'weibo',
      status: 2,
      posts_collected: 78,
      post_count: 150,
      created_at: '2024-08-30T14:20:00',
      updated_at: '2024-08-30T15:10:00'
    },
    {
      id: 'task_003_zhihu_qa',
      keyword: '大学专业选择',
      site: 'zhihu',
      status: 1,
      posts_collected: 23,
      post_count: 100,
      created_at: '2024-08-30T09:15:00',
      error_message: '目标网站连接超时',
      updated_at: '2024-08-30T09:45:00'
    },
    {
      id: 'task_004_xiaohongshu_food',
      keyword: '校园美食',
      site: 'xiaohongshu',
      status: 3,
      posts_collected: 45,
      post_count: 80,
      created_at: '2024-08-29T16:30:00',
      updated_at: '2024-08-29T17:00:00'
    },
    {
      id: 'task_005_weibo_sports',
      keyword: '大学运动',
      site: 'weibo',
      status: 4,
      posts_collected: 0,
      post_count: 120,
      created_at: '2024-08-31T08:00:00',
      updated_at: '2024-08-31T08:00:00'
    }
  ]
  calculateStatistics()
  errorMessage.value = ''
  console.log('示例数据加载完成')
}

// 操作方法
const refreshTasks = () => {
  console.log('刷新任务列表')
  currentPage.value = 1
  loadTasksFromAPI()
}

const applyFilters = () => {
  console.log('应用筛选条件:', filters)
  currentPage.value = 1
}

const resetFilters = () => {
  console.log('重置筛选条件')
  filters.status = ''
  filters.keyword = ''
  currentPage.value = 1
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    console.log('切换到第', page, '页')
  }
}

const showTaskDetail = (task) => {
  console.log('查看任务详情:', task.id)
  selectedTask.value = task
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedTask.value = null
}

const viewTaskPosts = (taskId) => {
  console.log('查看任务帖子:', taskId)
  router.push(`/posts?task_id=${taskId}`)
}

const stopTask = async (taskId) => {
  if (!confirm('确定要停止这个任务吗？')) return

  try {
    const response = await apiClient.post(`/api/crawler/tasks/${taskId}/stop`)
    if (response && response.success) {
      alert('任务已停止')
      await loadTasksFromAPI()
    } else {
      alert(response?.error?.message || '停止任务失败')
    }
  } catch (error) {
    alert('停止任务失败: ' + error.message)
    console.error('停止任务错误:', error)
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('确定要删除这个任务吗？此操作不可恢复！')) return

  try {
    const response = await apiClient.delete(`/api/crawler/tasks/${taskId}`)
    if (response && response.success) {
      alert('任务已删除')
      await loadTasksFromAPI()
    } else {
      alert(response?.error?.message || '删除任务失败')
    }
  } catch (error) {
    alert('删除任务失败: ' + error.message)
    console.error('删除任务错误:', error)
  }
}

// 监听筛选条件变化
watch(() => filters, () => {
  currentPage.value = 1
}, { deep: true })

// 页面初始化
onMounted(async () => {
  console.log('=== 任务页面初始化开始 ===')

  // 等待用户认证完成
  if (!userStore.hasCheckedAuth) {
    console.log('等待用户认证检查...')
    let attempts = 0
    while (!userStore.hasCheckedAuth && attempts < 50) {
      await new Promise(resolve => setTimeout(resolve, 100))
      attempts++
    }
  }

  console.log('用户状态:', {
    isAuthenticated: userStore.isAuthenticated,
    isAdmin: userStore.isAdmin,
    user: userStore.user
  })

  // 检查权限
  if (!userStore.isAuthenticated) {
    errorMessage.value = '请先登录系统'
    console.warn('用户未登录')
    return
  }

  if (!userStore.isAdmin) {
    errorMessage.value = '需要管理员权限才能访问此页面'
    console.warn('用户无管理员权限')
    return
  }

  // 尝试加载API数据，失败则加载示例数据
  console.log('开始加载任务数据')
  await loadTasksFromAPI()
  
  // 如果API加载失败且没有数据，则加载示例数据
  if (errorMessage.value && taskList.value.length === 0) {
    console.log('API加载失败，使用示例数据')
    loadMockData()
  }

  console.log('=== 任务页面初始化完成 ===')
})
</script>

<style scoped>
.modal.show {
  display: block !important;
}

.table th {
  border-top: none;
  font-weight: 600;
  font-size: 0.875rem;
  white-space: nowrap;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
}

.progress {
  border-radius: 3px;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

code {
  font-size: 0.875rem;
  background-color: #f8f9fa;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.card {
  transition: all 0.2s ease;
}

.table-responsive {
  max-height: 70vh;
  overflow-y: auto;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.alert {
  border-radius: 0.5rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>
