<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  email: '',
  password: '',
  confirmPassword: '',
  name: ''
})

const handleLogin = async () => {
  if (!loginForm.value.email || !loginForm.value.password) {
    showToast({ message: '请填写邮箱和密码' })
    return
  }

  loading.value = true
  try {
    await authStore.login(loginForm.value.email, loginForm.value.password)
    showToast({ message: '登录成功', type: 'success' })
    router.push('/')
  } catch (error: any) {
    showToast({ message: error || '登录失败', type: 'fail' })
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.email || !registerForm.value.password) {
    showToast({ message: '请填写完整信息' })
    return
  }

  if (!registerForm.value.name) {
    showToast({ message: '请输入用户名' })
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    showToast({ message: '两次密码不一致' })
    return
  }

  if (registerForm.value.password.length < 6) {
    showToast({ message: '密码至少需要6位' })
    return
  }

  loading.value = true
  try {
    await authStore.register(
      registerForm.value.email,
      registerForm.value.password,
      registerForm.value.name
    )
    showToast({ message: '注册成功', type: 'success' })
    // 注册成功后切换到登录
    isLogin.value = true
    // 自动填充登录表单
    loginForm.value.email = registerForm.value.email
    loginForm.value.password = ''
    registerForm.value = { email: '', password: '', confirmPassword: '', name: '' }
  } catch (error: any) {
    showToast({ message: error || '注册失败', type: 'fail' })
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isLogin.value = !isLogin.value
  // 清空表单
  loginForm.value = { email: '', password: '' }
  registerForm.value = { email: '', password: '', confirmPassword: '', name: '' }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <h1 class="title">
          油耗记录
        </h1>
        <p class="subtitle">
          轻松记录车辆加油数据
        </p>
      </div>

      <!-- 登录表单 -->
      <van-form
        v-if="isLogin"
        @submit="handleLogin"
      >
        <van-cell-group inset>
          <van-field
            v-model="loginForm.email"
            type="email"
            label="邮箱"
            placeholder="请输入邮箱"
            :rules="[{ required: true, message: '请输入邮箱' }]"
            clearable
          />
          <van-field
            v-model="loginForm.password"
            type="password"
            label="密码"
            placeholder="请输入密码"
            :rules="[{ required: true, message: '请输入密码' }]"
            clearable
          />
        </van-cell-group>

        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          登录
        </van-button>

        <div class="toggle-mode">
          还没有账号？
          <span
            class="link"
            @click="toggleMode"
          >立即注册</span>
        </div>
      </van-form>

      <!-- 注册表单 -->
      <van-form
        v-else
        @submit="handleRegister"
      >
        <van-cell-group inset>
          <van-field
            v-model="registerForm.email"
            type="email"
            label="邮箱"
            placeholder="请输入邮箱"
            :rules="[{ required: true, message: '请输入邮箱' }]"
            clearable
          />
          <van-field
            v-model="registerForm.name"
            type="text"
            label="用户名"
            placeholder="请输入用户名"
            :rules="[{ required: true, message: '请输入用户名' }]"
            clearable
          />
          <van-field
            v-model="registerForm.password"
            type="password"
            label="密码"
            placeholder="请输入密码（至少6位）"
            :rules="[{ required: true, message: '请输入密码' }]"
            clearable
          />
          <van-field
            v-model="registerForm.confirmPassword"
            type="password"
            label="确认密码"
            placeholder="请再次输入密码"
            :rules="[{ required: true, message: '请确认密码' }]"
            clearable
          />
        </van-cell-group>

        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-btn"
        >
          注册
        </van-button>

        <div class="toggle-mode">
          已有账号？
          <span
            class="link"
            @click="toggleMode"
          >立即登录</span>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.logo-section {
  text-align: center;
  margin-bottom: 28px;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.submit-btn {
  margin-top: 20px;
}

.toggle-mode {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #6b7280;
}

.toggle-mode .link {
  color: #4f46e5;
  font-weight: 500;
  cursor: pointer;
}
</style>
