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
  
  // 确保用户状态已检查
  if (!userStore.hasCheckedAuth) {
    await userStore.checkAuthStatus()
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/')
    return
  }
  
  // 检查是否只允许游客访问（已登录用户不能访问登录/注册页）
  if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

export default router
