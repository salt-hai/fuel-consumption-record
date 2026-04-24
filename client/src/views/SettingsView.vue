<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVehiclesStore } from '@/stores/vehicles'
import { showToast, showConfirmDialog, showDialog } from 'vant'

const router = useRouter()
const authStore = useAuthStore()
const vehiclesStore = useVehiclesStore()

// 当前用户信息
const currentUser = computed(() => authStore.user)
const userEmail = computed(() => authStore.user?.email || '')
const userName = computed(() => authStore.user?.name || authStore.user?.email?.split('@')[0] || '用户')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())

// 车辆统计
const vehicleCount = computed(() => (vehiclesStore.vehicles || []).length)

const showPasswordDialog = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

onMounted(async () => {
  // 加载车辆数据
  await vehiclesStore.fetchVehicles()
})

const onChangePassword = async () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    showToast({ message: '请填写完整' })
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    showToast({ message: '两次密码不一致' })
    return
  }

  await authStore.changePassword(
    passwordForm.value.old_password,
    passwordForm.value.new_password
  )
  showToast({ message: '密码修改成功', type: 'success' })
  showPasswordDialog.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: '',
  }
}

const onLogout = async () => {
  await showConfirmDialog({
    title: '确认退出',
    message: '确定要退出登录吗？',
  })
  await authStore.logout()
  router.push('/login')
}

const onExport = async (type: 'csv' | 'excel') => {
  showToast({ message: '导出中...', type: 'loading' })
  try {
    const vehicleId = vehiclesStore.currentVehicleId
    const url = `/api/v1/export/${type}?vehicle_id=${vehicleId}`
    window.open(url, '_blank')
    showToast({ message: '导出成功', type: 'success' })
  } catch {
    showToast({ message: '导出失败', type: 'fail' })
  }
}

const onAbout = () => {
  showDialog({
    title: '关于',
    message: '汽车油耗记录 v1.0.0\n\n一个简单易用的车辆油耗管理工具',
  })
}
</script>

<template>
  <div class="settings-container">
    <van-nav-bar title="我的" />

    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="user-avatar">{{ userInitial }}</div>
      <div class="user-info">
        <div class="user-name">{{ userName }}</div>
        <div class="user-email">{{ userEmail }}</div>
      </div>
      <div class="user-stats">
        <div class="stat-item">
          <div class="stat-value">{{ vehicleCount }}</div>
          <div class="stat-label">车辆</div>
        </div>
      </div>
    </div>

    <van-cell-group inset title="车辆管理">
      <van-cell
        title="我的车辆"
        is-link
        @click="router.push('/vehicles')"
      />
    </van-cell-group>

    <van-cell-group inset title="账户安全">
      <van-cell
        title="修改密码"
        is-link
        @click="showPasswordDialog = true"
      />
      <van-cell
        title="退出登录"
        is-link
        @click="onLogout"
      />
    </van-cell-group>

    <van-cell-group inset title="数据管理">
      <van-cell
        title="导出 CSV"
        is-link
        @click="onExport('csv')"
      />
      <van-cell
        title="导出 Excel"
        is-link
        @click="onExport('excel')"
      />
    </van-cell-group>

    <van-cell-group inset title="关于">
      <van-cell
        title="关于应用"
        is-link
        @click="onAbout"
      />
    </van-cell-group>

    <!-- 修改密码弹窗 -->
    <van-popup v-model:show="showPasswordDialog" position="bottom" round>
      <div class="dialog-content">
        <h3>修改密码</h3>
        <van-form @submit="onChangePassword">
          <van-field
            v-model="passwordForm.old_password"
            type="password"
            label="当前密码"
            placeholder="请输入当前密码"
            :rules="[{ required: true, message: '请输入当前密码' }]"
          />
          <van-field
            v-model="passwordForm.new_password"
            type="password"
            label="新密码"
            placeholder="请输入新密码"
            :rules="[{ required: true, message: '请输入新密码' }]"
          />
          <van-field
            v-model="passwordForm.confirm_password"
            type="password"
            label="确认密码"
            placeholder="请再次输入新密码"
            :rules="[{ required: true, message: '请确认新密码' }]"
          />
          <van-button round block type="primary" native-type="submit">
            确认修改
          </van-button>
          <van-button round block @click="showPasswordDialog = false">
            取消
          </van-button>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.settings-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 用户信息卡片 */
.user-card {
  margin: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 16px rgba(25, 137, 250, 0.25);
  color: white;
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 2px;
}

.user-email {
  font-size: 13px;
  opacity: 0.9;
}

.user-stats {
  display: flex;
  gap: 20px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.stat-label {
  font-size: 11px;
  opacity: 0.8;
}

.dialog-content {
  padding: 20px;
}

.dialog-content h3 {
  margin: 0 0 16px 0;
  text-align: center;
}

.dialog-content .van-button {
  margin-top: 8px;
}
</style>
