<template>
  <div class="container-fluid">
    <!-- 页面标题和搜索 -->
    <div class="row mb-4">
      <div class="col-md-8">
        <h2 class="mb-0">
          <i class="bi bi-postcard me-2"></i>高校数据浏览
        </h2>
        <p class="text-muted mt-1">浏览从小红书爬取的高校相关帖子和评论数据</p>
      </div>
      <div class="col-md-4">
        <div class="input-group">
          <input
            v-model="searchKeyword"
            type="text"
            class="form-control"
            placeholder="搜索帖子标题或内容..."
            @keyup.enter="loadPosts"
          >
          <button class="btn btn-primary" type="button" @click="loadPosts">
            <i class="bi bi-search"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">最小点赞数</label>
            <input
              v-model.number="filters.min_likes"
              type="number"
              class="form-control"
              placeholder="0"
              min="0"
              @change="loadPosts"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">最小评论数</label>
            <input
              v-model.number="filters.min_comments"
              type="number"
              class="form-control"
              placeholder="0"
              min="0"
              @change="loadPosts"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">排序字段</label>
            <select v-model="sortConfig.field" class="form-select" @change="loadPosts">
              <option value="time">按时间排序</option>
              <option value="like_count">按点赞数排序</option>
              <option value="comment_count">按评论数排序</option>
              <option value="collect_count">按收藏数排序</option>
              <option value="hot_score">按热度分数排序</option>
            </select>
          </div>
          <div class="col-md-2">
            <label class="form-label">排序方向</label>
            <select v-model="sortConfig.order" class="form-select" @change="loadPosts">
              <option value="desc">降序 ↓</option>
              <option value="asc">升序 ↑</option>
            </select>
          </div>
          <div class="col-md-1 d-flex align-items-end">
            <button class="btn btn-outline-secondary me-2" @click="resetFilters">
              <i class="bi bi-arrow-clockwise me-1"></i>重置
            </button>
            <button class="btn btn-primary" @click="loadPosts">
              <i class="bi bi-funnel me-1"></i>筛选
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
      <p class="mt-3 text-muted">正在加载帖子数据...</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <!-- 帖子列表 -->
    <div v-else>
      <!-- 数据统计和视图切换 -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <span class="text-muted">
          共找到 {{ posts.total || 0 }} 条帖子
        </span>
        <div class="d-flex align-items-center gap-3">
          <!-- 视图模式切换 -->
          <div class="btn-group btn-group-sm" role="group">
            <input type="radio" class="btn-check" name="viewMode" id="grid" v-model="viewMode" value="grid">
            <label class="btn btn-outline-primary" for="grid">
              <i class="bi bi-grid-3x3-gap"></i>
            </label>
            <input type="radio" class="btn-check" name="viewMode" id="list" v-model="viewMode" value="list">
            <label class="btn btn-outline-primary" for="list">
              <i class="bi bi-list"></i>
            </label>
          </div>
        </div>
      </div>

      <!-- 无数据提示 -->
      <div v-if="!posts.items || posts.items.length === 0" class="text-center py-5">
        <i class="bi bi-inbox display-1 text-muted"></i>
        <h4 class="text-muted mt-3">暂无帖子数据</h4>
        <p class="text-muted">请尝试调整搜索条件或筛选器</p>
      </div>

      <!-- 帖子卡片 - 网格视图 -->
      <div v-else-if="viewMode === 'grid'" class="row">
        <div v-for="post in posts.items" :key="post.id" class="col-lg-4 col-md-6 mb-4">
          <div class="card h-100 shadow-sm post-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="badge bg-primary">小红书</span>
                <small class="text-muted">{{ formatDate(post.created_at || post.time) }}</small>
              </div>

              <h6 class="card-title">{{ getDisplayTitle(post) }}</h6>
              <p class="card-text text-muted small">
                {{ truncateText(post.content, 100) }}
              </p>

              <!-- 发帖人信息 -->
              <div class="mb-3">
                <small class="text-muted">
                  <i class="bi bi-person me-1"></i>{{ post.author || post.poster || '匿名用户' }}
                </small>
                <span v-if="post.location" class="ms-2">
                  <small class="text-muted">
                    <i class="bi bi-geo-alt me-1"></i>{{ post.location }}
                  </small>
                </span>
              </div>

              <!-- 统计信息 -->
              <div class="row text-center mb-3">
                <div class="col">
                  <div class="text-primary">
                    <i class="bi bi-heart-fill"></i>
                    <div class="small">{{ formatNumber(post.like_count || 0) }}</div>
                  </div>
                </div>
                <div class="col">
                  <div class="text-success">
                    <i class="bi bi-chat-fill"></i>
                    <div class="small">{{ formatNumber(post.comment_count || 0) }}</div>
                  </div>
                </div>
                <div class="col">
                  <div class="text-warning">
                    <i class="bi bi-bookmark-fill"></i>
                    <div class="small">{{ formatNumber(post.collect_count || 0) }}</div>
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="d-flex justify-content-between">
                <button class="btn btn-sm btn-outline-info" @click="viewPostDetails(post)">
                  <i class="bi bi-eye me-1"></i>查看详情
                </button>
                <a v-if="post.link" :href="post.link" target="_blank" class="btn btn-sm btn-outline-primary">
                  <i class="bi bi-box-arrow-up-right me-1"></i>原链接
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 帖子列表 - 列表视图 -->
      <div v-else class="card">
        <div class="list-group list-group-flush">
          <div v-for="post in posts.items" :key="post.id" class="list-group-item post-item">
            <div class="d-flex justify-content-between align-items-start">
              <div class="flex-grow-1">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0">{{ getDisplayTitle(post) }}</h6>
                  <div>
                    <span class="badge bg-primary me-2">小红书</span>
                    <small class="text-muted">{{ formatDate(post.created_at || post.time) }}</small>
                  </div>
                </div>

                <p class="mb-2 text-muted">{{ truncateText(post.content, 200) }}</p>

                <!-- 发帖人和位置 -->
                <div class="mb-2">
                  <small class="text-muted">
                    <i class="bi bi-person me-1"></i>{{ post.author || post.poster || '匿名用户' }}
                  </small>
                  <span v-if="post.location" class="ms-3">
                    <small class="text-muted">
                      <i class="bi bi-geo-alt me-1"></i>{{ post.location }}
                    </small>
                  </span>
                </div>

                <!-- 统计信息 -->
                <div class="d-flex gap-4">
                  <span class="text-muted small">
                    <i class="bi bi-heart me-1 text-primary"></i>{{ formatNumber(post.like_count || 0) }}
                  </span>
                  <span class="text-muted small">
                    <i class="bi bi-chat me-1 text-success"></i>{{ formatNumber(post.comment_count || 0) }}
                  </span>
                  <span class="text-muted small">
                    <i class="bi bi-bookmark me-1 text-warning"></i>{{ formatNumber(post.collect_count || 0) }}
                  </span>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="ms-3 d-flex flex-column gap-1">
                <button class="btn btn-sm btn-outline-info" @click="viewPostDetails(post)">
                  <i class="bi bi-eye"></i>
                </button>
                <a v-if="post.link" :href="post.link" target="_blank" class="btn btn-sm btn-outline-primary">
                  <i class="bi bi-box-arrow-up-right"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <nav v-if="posts.total > pagination.pageSize" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: pagination.currentPage === 1 }">
            <button class="page-link" @click="changePage(pagination.currentPage - 1)" :disabled="pagination.currentPage === 1">
              <i class="bi bi-chevron-left"></i>
            </button>
          </li>

          <li v-for="page in visiblePages" :key="page" class="page-item"
              :class="{ active: page === pagination.currentPage }">
            <button class="page-link" @click="changePage(page)">{{ page }}</button>
          </li>

          <li class="page-item" :class="{ disabled: pagination.currentPage === totalPages }">
            <button class="page-link" @click="changePage(pagination.currentPage + 1)" :disabled="pagination.currentPage === totalPages">
              <i class="bi bi-chevron-right"></i>
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 帖子详情模态框 -->
    <div class="modal fade" :class="{ show: showDetailsModal }" :style="{ display: showDetailsModal ? 'block' : 'none' }" @click.self="showDetailsModal = false">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-postcard me-2"></i>帖子详情
            </h5>
            <button type="button" class="btn-close" @click="showDetailsModal = false"></button>
          </div>
          <div class="modal-body" v-if="selectedPost">
            <!-- 帖子信息 -->
            <div class="border-bottom pb-4 mb-4">
              <h4>{{ getDisplayTitle(selectedPost) }}</h4>
              <div class="row mb-3">
                <div class="col-md-6">
                  <small class="text-muted">
                    <i class="bi bi-person me-1"></i>{{ selectedPost.author || selectedPost.poster || '匿名用户' }}
                  </small>
                  <span v-if="selectedPost.location" class="ms-3">
                    <small class="text-muted">
                      <i class="bi bi-geo-alt me-1"></i>{{ selectedPost.location }}
                    </small>
                  </span>
                </div>
                <div class="col-md-6 text-end">
                  <small class="text-muted">{{ formatDate(selectedPost.created_at || selectedPost.time) }}</small>
                </div>
              </div>

              <div class="post-content mb-3">
                <p class="mb-0">{{ selectedPost.content }}</p>
              </div>

              <!-- 统计信息 -->
              <div class="row text-center">
                <div class="col-4">
                  <div class="border rounded p-3">
                    <i class="bi bi-heart-fill text-primary display-6"></i>
                    <h5 class="mt-2 mb-0">{{ formatNumber(selectedPost.like_count || 0) }}</h5>
                    <small class="text-muted">点赞</small>
                  </div>
                </div>
                <div class="col-4">
                  <div class="border rounded p-3">
                    <i class="bi bi-chat-fill text-success display-6"></i>
                    <h5 class="mt-2 mb-0">{{ formatNumber(selectedPost.comment_count || 0) }}</h5>
                    <small class="text-muted">评论</small>
                  </div>
                </div>
                <div class="col-4">
                  <div class="border rounded p-3">
                    <i class="bi bi-bookmark-fill text-warning display-6"></i>
                    <h5 class="mt-2 mb-0">{{ formatNumber(selectedPost.collect_count || 0) }}</h5>
                    <small class="text-muted">收藏</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- 评论列表 -->
            <div v-if="selectedPost.comments && selectedPost.comments.length > 0">
              <h6 class="mb-3">
                <i class="bi bi-chat-dots me-2"></i>评论 ({{ selectedPost.comments.length }})
              </h6>
              <div class="comments-list" style="max-height: 400px; overflow-y: auto;">
                <div v-for="comment in selectedPost.comments" :key="comment.id" class="comment-item mb-3 p-3 border rounded">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                      <strong>{{ comment.commenter || comment.author || '匿名用户' }}</strong>
                      <span v-if="comment.location" class="ms-2 text-muted small">
                        <i class="bi bi-geo-alt"></i> {{ comment.location }}
                      </span>
                    </div>
                    <small class="text-muted">{{ formatDate(comment.created_at || comment.time) }}</small>
                  </div>
                  <p class="mb-2">{{ comment.content }}</p>
                  <div class="d-flex gap-3">
                    <small class="text-muted">
                      <i class="bi bi-heart me-1 text-primary"></i>{{ formatNumber(comment.like_count || 0) }}
                    </small>
                    <small class="text-muted">
                      <i class="bi bi-reply me-1 text-secondary"></i>{{ formatNumber(comment.reply_count || 0) }}
                    </small>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-muted py-4">
              <i class="bi bi-chat display-4"></i>
              <p class="mt-2">暂无评论</p>
            </div>
          </div>
          <div class="modal-footer">
            <a v-if="selectedPost && selectedPost.link" :href="selectedPost.link" target="_blank" class="btn btn-primary me-auto">
              <i class="bi bi-box-arrow-up-right me-1"></i>查看原文
            </a>
            <button type="button" class="btn btn-secondary" @click="showDetailsModal = false">关闭</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模态框背景 -->
    <div v-if="showDetailsModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import apiClient from '@/services/apiClient'
import { computed, onMounted, reactive, ref } from 'vue'

// 响应式数据
const loading = ref(false)
const error = ref('')
const posts = ref({ items: [], total: 0 })
const searchKeyword = ref('')
const viewMode = ref('grid')
const showDetailsModal = ref(false)
const selectedPost = ref(null)

// 筛选器
const filters = reactive({
  min_likes: '',
  min_comments: ''
})

// 排序配置
const sortConfig = reactive({
  field: 'time',
  order: 'desc'
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: parseInt(import.meta.env.VITE_DEFAULT_PAGE_SIZE) || 20
})

// 计算属性
const totalPages = computed(() => Math.ceil(posts.value.total / pagination.pageSize))

const visiblePages = computed(() => {
  const current = pagination.currentPage
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

// 方法
const loadPosts = async () => {
  loading.value = true
  error.value = ''

  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      sort_by: sortConfig.field,
      sort_order: sortConfig.order
    }

    // 添加搜索和筛选参数
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filters.min_likes) params.min_likes = filters.min_likes
    if (filters.min_comments) params.min_comments = filters.min_comments

    const response = await apiClient.get('/api/posts', { params })

    if (response.success) {
      // 修改为使用posts字段，以匹配后端返回的格式
      posts.value = {
        items: response.data.posts || [],  // 将posts字段映射到items
        total: response.data.total || 0
      }
    } else {
      error.value = response.error?.message || '加载帖子失败'
    }
  } catch (err) {
  error.value = '网络错误，请稍后重试'
    console.error('加载帖子错误:', err)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.min_likes = ''
  filters.min_comments = ''
  searchKeyword.value = ''
  sortConfig.field = 'time'
  sortConfig.order = 'desc'
  pagination.currentPage = 1
  loadPosts()
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    pagination.currentPage = page
    loadPosts()
  }
}

const viewPostDetails = (post) => {
  selectedPost.value = post
  showDetailsModal.value = true
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

const getDisplayTitle = (post) => {
  // 如果有标题且不为空（去除空白字符后）
  if (post.title && post.title.trim()) {
    return post.title
  }
  
  // 如果没有标题但有内容，使用内容前20个字符作为标题
  if (post.content && post.content.trim()) {
    const content = post.content.replace(/\n/g, ' ').replace(/\r/g, ' ').trim()
    if (content.length > 20) {
      return content.substring(0, 20) + '...'
    }
    return content
  }
  
  // 如果既没有标题也没有内容
  return '无标题'
}

// 生命周期
onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.post-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
}

.post-item {
  transition: background-color 0.2s ease;
}

.post-item:hover {
  background-color: #f8f9fa;
}

.badge {
  font-size: 0.75em;
}

.pagination .page-link {
  border-color: #dee2e6;
  color: #6c757d;
}

.pagination .page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-check:checked + .btn-outline-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
}

.modal.show {
  display: block !important;
}

.comment-item {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

.comment-item:hover {
  background-color: #e9ecef;
}

.comments-list {
  scrollbar-width: thin;
}

.comments-list::-webkit-scrollbar {
  width: 6px;
}

.comments-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.comments-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.post-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.form-select-sm {
  min-width: 100px;
}
</style>
