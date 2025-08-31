<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card shadow">
        <div class="card-body p-5">
          <div class="text-center mb-4">
            <img src="@/assets/img/logo.svg" :alt="`${appConfig.name} Logo`" height="50" class="mb-3">
            <h3 class="fw-bold">用户登录</h3>
            <p class="text-muted">登录到 {{ appConfig.name }} 平台</p>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ error }}
          </div>

          <!-- 成功提示 -->
          <div v-if="success" class="alert alert-success" role="alert">
            <i class="bi bi-check-circle-fill me-2"></i>
            {{ success }}
          </div>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label for="username" class="form-label">用户名</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-person"></i>
                </span>
                <input
                  id="username"
                  v-model="form.username"
                  type="text"
                  class="form-control"
                  placeholder="请输入用户名"
                  required
                  :disabled="loading"
                >
              </div>
            </div>

            <div class="mb-3">
              <label for="password" class="form-label">密码</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-lock"></i>
                </span>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  placeholder="请输入密码"
                  required
                  :disabled="loading"
                >
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="showPassword = !showPassword"
                  :disabled="loading"
                >
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-3 form-check">
              <input
                id="remember"
                v-model="form.remember"
                type="checkbox"
                class="form-check-input"
                :disabled="loading"
              >
              <label class="form-check-label" for="remember">
                记住我
              </label>
            </div>

            <div class="d-grid mb-3">
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-box-arrow-in-right me-2"></i>
                {{ loading ? '登录中...' : '登录' }}
              </button>
            </div>
          </form>

          <div class="text-center">
            <p class="mb-0">
              还没有账号？
              <router-link to="/register" class="text-decoration-none">
                立即注册
              </router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useUserStore } from '@/stores/user'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

// 应用配置
const appConfig = {
  name: import.meta.env.VITE_APP_NAME || 'GradInsight'
}

// 响应式数据
const loading = ref(false)
const showPassword = ref(false)
const error = ref('')
const success = ref('')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

// 处理登录
const handleLogin = async () => {
  if (!form.username || !form.password) {
    error.value = '请填写完整的登录信息'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const result = await userStore.login({
      username: form.username,
      password: form.password
    })

    if (result.success) {
      success.value = '登录成功，即将跳转...'
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      error.value = result.error?.message || '登录失败'
    }
  } catch (err) {
    error.value = '登录过程中发生错误'
    console.error('登录错误:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card {
  border: none;
  border-radius: 15px;
}

.form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
  border-color: #667eea;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}
</style>
