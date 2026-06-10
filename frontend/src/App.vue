<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <img
            src="@/assets/img/logo.svg"
            alt="GradInsight Logo"
            height="36"
            class="d-inline-block align-text-top me-2"
          />
          GradInsight
        </router-link>
        
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/" exact-active-class="active">
                首页
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/posts" active-class="active">
                高校数据
              </router-link>
            </li>
            <li class="nav-item" v-if="userStore.isAuthenticated">
              <router-link class="nav-link" to="/analysis" active-class="active">
                <i class="bi bi-graph-up me-1"></i>内容分析
              </router-link>
            </li>
            <li class="nav-item" v-if="userStore.isAdmin">
              <router-link class="nav-link" to="/tasks" active-class="active">
                爬虫任务
              </router-link>
            </li>
            <li class="nav-item" v-if="userStore.isAdmin">
              <router-link class="nav-link" to="/crawler" active-class="active">
                启动爬虫
              </router-link>
            </li>
          </ul>
          
          <!-- 用户信息 -->
          <div class="d-flex" v-if="!userStore.isAuthenticated">
            <router-link to="/login" class="btn btn-outline-light me-2">
              <i class="bi bi-box-arrow-in-right me-1"></i>登录
            </router-link>
            <router-link to="/register" class="btn btn-light">
              <i class="bi bi-person-plus me-1"></i>注册
            </router-link>
          </div>
          
          <div class="dropdown" v-else>
            <a
              class="nav-link dropdown-toggle text-white d-flex align-items-center"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-person-circle me-1" style="font-size: 1.2rem"></i>
              <span>{{ userStore.user?.username }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <span class="dropdown-item-text">
                  <i class="bi bi-person-badge me-1"></i>
                  角色: {{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
                </span>
              </li>
              <li>
                <span class="dropdown-item-text">
                  <i class="bi bi-envelope me-1"></i>
                  邮箱: {{ userStore.user?.email }}
                </span>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right me-1"></i>
                  退出登录
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="container my-4">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="bg-light py-4 mt-4">
      <div class="container text-center">
        <p>© 2025 GradInsight 高校数据分析平台 | 版权所有</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

onMounted(async () => {
  await userStore.checkAuthStatus()
})

const handleLogout = async () => {
  await userStore.logout()
}
</script>

<style>
/* 全局样式可以在这里添加，或者导入CSS文件 */
</style>
