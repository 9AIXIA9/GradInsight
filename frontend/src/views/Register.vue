<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
      <div class="card shadow">
        <div class="card-body p-5">
          <div class="text-center mb-4">
            <img src="@/assets/img/logo.svg" :alt="`${appConfig.name} Logo`" height="50" class="mb-3">
            <h3 class="fw-bold">用户注册</h3>
            <p class="text-muted">创建 {{ appConfig.name }} 账号</p>
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

          <form @submit.prevent="handleRegister">
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
              <div class="form-text">用户名长度应为3-20个字符</div>
            </div>

            <div class="mb-3">
              <label for="email" class="form-label">邮箱地址</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-envelope"></i>
                </span>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  class="form-control"
                  placeholder="请输入邮箱地址"
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
              <div class="form-text">密码长度应至少为6个字符</div>
            </div>

            <div class="mb-3">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-lock-fill"></i>
                </span>
                <input
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-control"
                  placeholder="请再次输入密码"
                  required
                  :disabled="loading"
                >
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="showConfirmPassword = !showConfirmPassword"
                  :disabled="loading"
                >
                  <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>

            <div class="mb-3 form-check">
              <input
                id="agree"
                v-model="form.agree"
                type="checkbox"
                class="form-check-input"
                required
                :disabled="loading"
              >
              <label class="form-check-label" for="agree">
                我同意 <a href="#" class="text-decoration-none">用户协议</a> 和 <a href="#" class="text-decoration-none">隐私政策</a>
              </label>
            </div>

            <div class="d-grid mb-3">
              <button type="submit" class="btn btn-primary" :disabled="loading || !isFormValid">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-person-plus me-2"></i>
                {{ loading ? '注册中...' : '注册' }}
              </button>
            </div>
          </form>

          <div class="text-center">
            <p class="mb-0">
              已有账号？
              <router-link to="/login" class="text-decoration-none">
                立即登录
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
import { computed, reactive, ref } from 'vue'
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
const showConfirmPassword = ref(false)
const error = ref('')
const success = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false
})

// 计算属性
const isFormValid = computed(() => {
  return form.username.length >= 3 &&
         form.email.includes('@') &&
         form.password.length >= 6 &&
         form.password === form.confirmPassword &&
         form.agree
})

// 处理注册
const handleRegister = async () => {
  if (!isFormValid.value) {
    error.value = '请填写完整且正确的注册信息'
    return
  }

  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const result = await userStore.register({
      username: form.username,
      email: form.email,
      password: form.password
    })

    if (result.success) {
      success.value = '注册成功，即将跳转到首页...'
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      error.value = result.error?.message || '注册失败'
    }
  } catch (err) {
    error.value = '注册过程中发生错误'
    console.error('注册错误:', err)
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

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
}

.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.form-text {
  font-size: 0.875rem;
  color: #6c757d;
}
</style>
