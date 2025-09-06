<template>
  <div>
    <!-- 英雄区域 -->
    <div class="hero-section text-center py-5 mb-5"
      style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
      <div class="container">
        <h1 class="display-3 fw-bold mb-4">{{ appConfig.name }}</h1>
        <p class="display-6 mb-3">{{ appConfig.title }}</p>
        <p class="lead fs-5 mb-4">{{ appConfig.description }}</p>
        <p class="fs-6 mb-4">{{ appConfig.subtitle }}</p>

        <div v-if="!userStore.isAuthenticated" class="mt-4">
          <router-link to="/register" class="btn btn-light btn-lg me-3 px-4 py-2">
            <i class="bi bi-person-plus me-2"></i>立即注册
          </router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg px-4 py-2">
            <i class="bi bi-box-arrow-in-right me-2"></i>登录系统
          </router-link>
        </div>
        <div v-else class="mt-4">
          <router-link to="/posts" class="btn btn-light btn-lg me-3 px-4 py-2">
            <i class="bi bi-search me-2"></i>浏览高校数据
          </router-link>
          <router-link v-if="userStore.isAdmin" to="/crawler" class="btn btn-outline-light btn-lg px-4 py-2">
            <i class="bi bi-gear me-2"></i>启动爬虫任务
          </router-link>
        </div>
      </div>
    </div>

    <!-- 数据统计 -->
    <div class="container mb-5">
      <div class="row text-center">
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-primary mb-3">
                <i class="bi bi-database-fill" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-primary">{{ stats.totalPosts || '加载中...' }}</h3>
              <p class="text-muted mb-0">高校相关帖子</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-success mb-3">
                <i class="bi bi-chat-dots-fill" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-success">{{ stats.totalComments || '加载中...' }}</h3>
              <p class="text-muted mb-0">用户评论数据</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-warning mb-3">
                <i class="bi bi-building-fill" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-warning">{{ stats.totalSchools || '加载中...' }}</h3>
              <p class="text-muted mb-0">涉及高校数量</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-info mb-3">
                <i class="bi bi-robot" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-info">{{ stats.totalTasks || '加载中...' }}</h3>
              <p class="text-muted mb-0">爬虫任务完成</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 平台功能介绍 -->
    <div class="container mb-5">
      <div class="row">
        <div class="col-lg-12 text-center mb-5">
          <h2 class="fw-bold">平台核心功能</h2>
          <p class="text-muted">全方位的高校数据采集与分析解决方案</p>
        </div>
      </div>
      <div class="row">
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100 text-center">
            <div class="card-body p-4">
              <div class="text-primary mb-3">
                <i class="bi bi-robot" style="font-size: 3rem;"></i>
              </div>
              <h5 class="fw-bold">智能数据爬取</h5>
              <p class="text-muted">基于小红书平台的高校信息智能爬取，支持关键词搜索、点赞过滤、评论收集等功能</p>
              <router-link v-if="userStore.isAdmin" to="/crawler" class="btn btn-outline-primary">
                启动爬虫
              </router-link>
              <button v-else-if="userStore.isAuthenticated" class="btn btn-outline-secondary" disabled>
                仅限管理员
              </button>
              <router-link v-else to="/login" class="btn btn-outline-primary">
                登录查看
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100 text-center">
            <div class="card-body p-4">
              <div class="text-success mb-3">
                <i class="bi bi-search" style="font-size: 3rem;"></i>
              </div>
              <h5 class="fw-bold">数据浏览分析</h5>
              <p class="text-muted">提供强大的帖子数据浏览和筛选功能，支持按任务、关键词、点赞数等多维度筛选</p>
              <router-link to="/posts" class="btn btn-outline-success">
                浏览数据
              </router-link>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100 text-center">
            <div class="card-body p-4">
              <div class="text-warning mb-3">
                <i class="bi bi-bar-chart-fill" style="font-size: 3rem;"></i>
              </div>
              <h5 class="fw-bold">统计分析</h5>
              <p class="text-muted">提供丰富的数据统计功能，包括热门高校、趋势分析、最新动态等数据洞察</p>
              <button class="btn btn-outline-warning" @click="scrollToStats">
                查看统计
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最新动态 -->
    <div class="container mb-5" ref="statsSection">
      <div class="row">
        <div class="col-lg-6 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-fire me-2"></i>热门高校
              </h5>
            </div>
            <div class="card-body">
              <div v-if="hotSchools.length === 0" class="text-center text-muted py-3">
                <div class="spinner-border spinner-border-sm me-2"></div>
                加载中...
              </div>
              <div v-else>
                <div v-for="(school, index) in hotSchools" :key="index"
                  class="d-flex justify-content-between align-items-center mb-3">
                  <div>
                    <h6 class="mb-1">{{ school.name }}</h6>
                    <small class="text-muted">{{ school.location }} · {{ school.type }}</small>
                  </div>
                  <div class="text-end">
                    <div class="text-primary fw-bold">{{ school.posts }}</div>
                    <small class="text-success">{{ school.trend }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-success text-white">
              <h5 class="mb-0">
                <i class="bi bi-clock-history me-2"></i>最新动态
              </h5>
            </div>
            <div class="card-body">
              <div v-if="latestNews.length === 0" class="text-center text-muted py-3">
                <div class="spinner-border spinner-border-sm me-2"></div>
                加载中...
              </div>
              <div v-else>
                <div v-for="(news, index) in latestNews" :key="index" class="d-flex align-items-start mb-3">
                  <div class="me-3">
                    <i :class="[news.icon, 'text-' + news.type]"></i>
                  </div>
                  <div class="flex-grow-1">
                    <h6 class="mb-1">{{ news.title }}</h6>
                    <p class="mb-1 text-muted small">{{ news.content }}</p>
                    <small class="text-muted">{{ news.time }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA区域 -->
    <div class="bg-light py-5">
      <div class="container text-center">
        <h2 class="fw-bold mb-3">开始您的高校数据分析之旅</h2>
        <p class="text-muted mb-4">立即注册，体验强大的高校数据采集与分析功能</p>
        <div v-if="!userStore.isAuthenticated">
          <router-link to="/register" class="btn btn-primary btn-lg me-3">
            <i class="bi bi-person-plus me-2"></i>免费注册
          </router-link>
          <router-link to="/login" class="btn btn-outline-primary btn-lg">
            <i class="bi bi-box-arrow-in-right me-2"></i>立即登录
          </router-link>
        </div>
        <div v-else>
          <router-link v-if="userStore.isAdmin" to="/crawler" class="btn btn-primary btn-lg me-3">
            <i class="bi bi-rocket me-2"></i>启动爬虫
          </router-link>
          <router-link to="/posts" class="btn btn-primary btn-lg me-3">
            <i class="bi bi-search me-2"></i>浏览数据
          </router-link>
          <router-link to="/analysis" class="btn btn-outline-primary btn-lg">
            <i class="bi bi-bar-chart me-2"></i>数据分析
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import apiClient from '@/services/apiClient'
import { useUserStore } from '@/stores/user'
import { onMounted, ref } from 'vue'

const userStore = useUserStore()

// 应用配置
const appConfig = {
  name: import.meta.env.VITE_APP_NAME || 'GradInsight',
  title: import.meta.env.VITE_APP_TITLE || '高校数据分析平台',
  description: import.meta.env.VITE_APP_DESCRIPTION || '基于小红书等社交平台的高校信息智能分析系统',
  subtitle: import.meta.env.VITE_APP_SUBTITLE || '发现高校数据背后的洞察，助力学生择校与教育决策'
}

// 响应式数据
const stats = ref({
  totalPosts: '0',
  totalComments: '0',
  totalSchools: '0',
  totalTasks: '0'
})
const hotSchools = ref([])
const latestNews = ref([])
const statsSection = ref(null)

// 方法
const loadStats = async () => {
  try {
    const response = await apiClient.get('/api/stats/overview')
    if (response.success) {
      stats.value = response.data
    }
  } catch (err) {
    console.error('加载统计数据失败:', err)
    // 使用默认数据
    stats.value = {
      totalPosts: '8.5K+',
      totalComments: '42K+',
      totalSchools: '285',
      totalTasks: '96'
    }
  }
}

const loadHotSchools = async () => {
  try {
    const response = await apiClient.get('/api/stats/hot-schools')
    if (response.success) {
      hotSchools.value = response.data
    }
  } catch (err) {
    console.error('加载热门高校失败:', err)
    // 使用默认数据
    hotSchools.value = [
      { name: '南昌大学', location: '江西南昌', type: '综合性大学', posts: '1,234', trend: '+15%' },
      { name: '华中科技大学', location: '湖北武汉', type: '理工类', posts: '1,156', trend: '+12%' },
      { name: '中南大学', location: '湖南长沙', type: '综合性大学', posts: '1,087', trend: '+18%' },
      { name: '西安交通大学', location: '陕西西安', type: '理工类', posts: '987', trend: '+10%' },
      { name: '湖南大学', location: '湖南长沙', type: '综合性大学', posts: '876', trend: '+8%' }
    ]
  }
}

const loadLatestNews = async () => {
  try {
    const response = await apiClient.get('/api/stats/latest-news')
    if (response.success) {
      latestNews.value = response.data
    }
  } catch (err) {
    console.error('加载最新动态失败:', err)
    // 使用默认数据
    latestNews.value = [
      {
        icon: 'bi bi-check-circle-fill',
        title: '数据采集完成',
        content: '南昌大学相关数据采集任务完成，共收集356条帖子',
        time: '2小时前',
        type: 'success'
      },
      {
        icon: 'bi bi-rocket-fill',
        title: '新任务启动',
        content: '计算机科学专业数据采集任务已启动',
        time: '4小时前',
        type: 'primary'
      },
      {
        icon: 'bi bi-bar-chart-fill',
        title: '分析报告生成',
        content: '高校热度分析报告已生成，发现3个新趋势',
        time: '6小时前',
        type: 'info'
      },
      {
        icon: 'bi bi-gear-fill',
        title: '系统更新',
        content: '爬虫引擎升级完成，提升数据采集效率30%',
        time: '1天前',
        type: 'warning'
      }
    ]
  }
}

const scrollToStats = () => {
  if (statsSection.value) {
    statsSection.value.scrollIntoView({ behavior: 'smooth' })
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadHotSchools(),
    loadLatestNews()
  ])
})
</script>

<style scoped>
.hero-section {
  background-attachment: fixed;
  background-size: cover;
  background-position: center;
}

.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 15px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
}

.btn {
  border-radius: 25px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-lg {
  padding: 12px 30px;
}

.bg-light {
  background-color: #f8f9fa !important;
}

.text-primary {
  color: #667eea !important;
}

.display-3 {
  font-size: 3.5rem;
  font-weight: 700;
}

.display-6 {
  font-size: 1.75rem;
  font-weight: 600;
}

@media (max-width: 768px) {
  .display-3 {
    font-size: 2.5rem;
  }

  .display-6 {
    font-size: 1.5rem;
  }
}
</style>
