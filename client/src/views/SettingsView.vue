<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useVehiclesStore } from '@/stores/vehicles'
import { showToast, showConfirmDialog, showDialog } from 'vant'

const router = useRouter()
const authStore = useAuthStore()
const vehiclesStore = useVehiclesStore()

const showPasswordDialog = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
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
  authStore.logout()
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
    <van-nav-bar title="设置" />

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
  background-color: #f5f7fa;
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
