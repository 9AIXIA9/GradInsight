import authService from '@/services/authService'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  const hasCheckedAuth = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 设置认证token
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('access_token', newToken)
    } else {
      localStorage.removeItem('access_token')
    }
  }

  // 设置用户信息
  const setUser = (userData) => {
    user.value = userData
  }

  // 登录
  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials)
      if (response.success) {
        // Java 后端 AuthResponse 返回 { token: "..." }
        const tokenData = response.data
        setToken(tokenData.token)

        // 登录成功后获取用户信息
        const userResponse = await authService.getCurrentUser()
        if (userResponse.success) {
          setUser(userResponse.data)
        }

        return { success: true }
      } else {
        return { success: false, error: response.error }
      }
    } catch (error) {
      return { success: false, error: { message: error.message } }
    }
  }

  // 注册
  const register = async (userData) => {
    try {
      const response = await authService.register(userData)
      if (response.success) {
        // 注册成功后自动登录
        return await login({
          username: userData.username,
          password: userData.password
        })
      } else {
        return { success: false, error: response.error }
      }
    } catch (error) {
      return { success: false, error: { message: error.message } }
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      setToken(null)
      setUser(null)
      hasCheckedAuth.value = false
    }
  }

  // 检查认证状态
  const checkAuthStatus = async () => {
    if (!token.value) {
      hasCheckedAuth.value = true
      return
    }

    try {
      const response = await authService.getCurrentUser()
      if (response.success) {
        setUser(response.data)
      } else {
        // Token无效，清除
        setToken(null)
        setUser(null)
      }
    } catch (error) {
      console.error('检查认证状态失败:', error)
      // 发生错误时清除认证信息
      setToken(null)
      setUser(null)
    } finally {
      hasCheckedAuth.value = true
    }
  }

  return {
    // 状态
    user,
    token,
    hasCheckedAuth,
    
    // 计算属性
    isAuthenticated,
    isAdmin,
    
    // 方法
    setToken,
    setUser,
    login,
    register,
    logout,
    checkAuthStatus
  }
})
