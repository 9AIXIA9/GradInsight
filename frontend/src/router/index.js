import { useUserStore } from '@/stores/user'
import { createRouter, createWebHistory } from 'vue-router'

// 路由懒加载
const Home = () => import('@/views/Home.vue')
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Posts = () => import('@/views/Posts.vue')
const Analysis = () => import('@/views/Analysis.vue')
const Tasks = () => import('@/views/Tasks.vue')
const Crawler = () => import('@/views/Crawler.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { requiresGuest: true }
    },
    {
      path: '/posts',
      name: 'Posts',
      component: Posts
    },
    {
      path: '/analysis',
      name: 'Analysis',
      component: Analysis,
      meta: { requiresAuth: true }
    },
    {
      path: '/tasks',
      name: 'Tasks',
      component: Tasks,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/crawler',
      name: 'Crawler',
      component: Crawler,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  console.log('路由守卫检查:', {
    path: to.path,
    hasCheckedAuth: userStore.hasCheckedAuth,
    isAuthenticated: userStore.isAuthenticated,
    isAdmin: userStore.isAdmin,
    user: userStore.user
  })

  // 确保用户状态已检查
  if (!userStore.hasCheckedAuth) {
    try {
      await userStore.checkAuthStatus()
    } catch (error) {
      console.error('检查认证状态失败:', error)
      // 即使检查失败也要继续，避免死循环
      userStore.hasCheckedAuth = true
    }
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    console.log('需要登录，重定向到登录页')
    next('/login')
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    console.log('需要管理员权限，但用户不是管理员，重定向到首页')
    // 添加一个提示消息
    if (userStore.isAuthenticated) {
      alert('您没有访问此页面的权限，需要管理员权限')
    }
    next('/')
    return
  }
  
  // 检查是否只允许游客访问（已登录用户不能访问登录/注册页）
  if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next('/')
    return
  }
  
  console.log('路由守卫通过，允许访问')
  next()
})

export default router
