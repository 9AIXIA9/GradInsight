<template>
  <div>
    <!-- 英雄区域 -->
    <div class="hero-section text-center py-5 mb-5" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
      <div class="container">
        <h1 class="display-3 fw-bold mb-4">GradInsight</h1>
        <p class="display-6 mb-3">高校数据分析平台</p>
        <p class="lead fs-5 mb-4">基于小红书等社交平台的高校信息智能分析系统</p>
        <p class="fs-6 mb-4">发现高校数据背后的洞察，助力学生择校与教育决策</p>
        
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
              <h3 class="fw-bold text-primary">{{ stats.totalPosts || '10K+' }}</h3>
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
              <h3 class="fw-bold text-success">{{ stats.totalComments || '50K+' }}</h3>
              <p class="text-muted mb-0">用户评论数据</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-warning mb-3">
                <i class="bi bi-building" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-warning">{{ stats.totalSchools || '500+' }}</h3>
              <p class="text-muted mb-0">覆盖高校数量</p>
            </div>
          </div>
        </div>
        <div class="col-md-3 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body">
              <div class="text-info mb-3">
                <i class="bi bi-graph-up" style="font-size: 2.5rem;"></i>
              </div>
              <h3 class="fw-bold text-info">{{ stats.totalTasks || '100+' }}</h3>
              <p class="text-muted mb-0">完成爬虫任务</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能特性 -->
    <div class="container mb-5">
      <h2 class="text-center mb-5">
        <i class="bi bi-star-fill text-warning me-2"></i>平台特色功能
      </h2>
      <div class="row">
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-primary mb-3">
                <i class="bi bi-search" style="font-size: 3rem;"></i>
              </div>
              <h4 class="fw-bold mb-3">智能数据搜索</h4>
              <p class="text-muted">
                基于关键词和标签的高校信息智能搜索，快速找到相关的高校数据和用户评价
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-success mb-3">
                <i class="bi bi-graph-up-arrow" style="font-size: 3rem;"></i>
              </div>
              <h4 class="fw-bold mb-3">内容分析</h4>
              <p class="text-muted">
                运用自然语言处理技术，对高校相关内容进行情感分析、关键词提取和话题聚类
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body text-center">
              <div class="text-info mb-3">
                <i class="bi bi-gear-fill" style="font-size: 3rem;"></i>
              </div>
              <h4 class="fw-bold mb-3">自动化爬虫</h4>
              <p class="text-muted">
                支持多平台数据爬取，实时更新高校相关信息，保证数据的新鲜度和准确性
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">加载中...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import statsService from '@/services/statsService'
import { useUserStore } from '@/stores/user'
import { onMounted, ref } from 'vue'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const stats = ref({
  totalPosts: '10K+',
  totalComments: '50K+',
  totalSchools: '500+',
  totalTasks: '100+'
})

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    const response = await statsService.getStats()
    if (response.success) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.hero-section {
  background-attachment: fixed;
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-5px);
}

.rank-badge {
  min-width: 40px;
}
</style>
