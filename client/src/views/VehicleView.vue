<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { showToast, showConfirmDialog } from 'vant'
import type { Vehicle } from '@/api/vehicles'

const router = useRouter()
const vehiclesStore = useVehiclesStore()

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingVehicle = ref<Vehicle | null>(null)

const newVehicle = ref({
  name: '',
  brand: '',
  model: '',
  plate_number: '',
  initial_odometer: 0,
  fuel_type: '92号汽油',
})

onMounted(async () => {
  await vehiclesStore.fetchVehicles()
})

const onAdd = () => {
  newVehicle.value = {
    name: '',
    brand: '',
    model: '',
    plate_number: '',
    initial_odometer: 0,
    fuel_type: '92号汽油',
  }
  showAddDialog.value = true
}

const onEdit = (vehicle: Vehicle) => {
  editingVehicle.value = vehicle
  newVehicle.value = {
    name: vehicle.name,
    brand: vehicle.brand || '',
    model: vehicle.model || '',
    plate_number: vehicle.plate_number || '',
    initial_odometer: vehicle.initial_odometer,
    fuel_type: vehicle.fuel_type,
  }
  showEditDialog.value = true
}

const onDelete = async (vehicle: Vehicle) => {
  await showConfirmDialog({
    title: '确认删除',
    message: `确定要删除「${vehicle.name}」吗？`,
  })
  await vehiclesStore.deleteVehicle(vehicle.id)
  showToast({ message: '已删除', type: 'success' })
}

const onSubmitAdd = async () => {
  if (!newVehicle.value.name) {
    showToast({ message: '请输入车辆名称' })
    return
  }
  await vehiclesStore.createVehicle(newVehicle.value)
  showToast({ message: '添加成功', type: 'success' })
  showAddDialog.value = false
}

const onSubmitEdit = async () => {
  if (!editingVehicle.value || !newVehicle.value.name) {
    showToast({ message: '请输入车辆名称' })
    return
  }
  await vehiclesStore.updateVehicle(editingVehicle.value.id, newVehicle.value)
  showToast({ message: '更新成功', type: 'success' })
  showEditDialog.value = false
}
</script>

<template>
  <div class="vehicle-container">
    <van-nav-bar title="车辆管理" />

    <div v-if="vehiclesStore.vehicles.length === 0" class="empty-state">
      <van-empty description="暂无车辆">
        <van-button type="primary" size="small" @click="onAdd">
          添加第一辆车
        </van-button>
      </van-empty>
    </div>

    <div v-else class="vehicle-list">
      <van-card
        v-for="vehicle in vehiclesStore.vehicles"
        :key="vehicle.id"
        :title="vehicle.name"
        :desc="`${vehicle.brand || ''} ${vehicle.model || ''}`"
      >
        <template #tags>
          <van-tag v-if="!vehicle.is_active" type="warning">已停用</van-tag>
        </template>
        <template #footer>
          <van-button size="small" @click="onEdit(vehicle)">编辑</van-button>
          <van-button size="small" type="danger" @click="onDelete(vehicle)">删除</van-button>
        </template>
      </van-card>
    </div>

    <van-floating-bubble
      axis="xy"
      icon="plus"
      magnetic="x"
      @click="onAdd"
    />

    <!-- 添加车辆弹窗 -->
    <van-popup v-model:show="showAddDialog" position="bottom" round>
      <div class="dialog-content">
        <h3>添加车辆</h3>
        <van-form @submit="onSubmitAdd">
          <van-field
            v-model="newVehicle.name"
            label="车辆名称"
            placeholder="如：我的卡罗拉"
            :rules="[{ required: true, message: '请输入车辆名称' }]"
          />
          <van-field
            v-model="newVehicle.brand"
            label="品牌"
            placeholder="如：丰田"
          />
          <van-field
            v-model="newVehicle.model"
            label="型号"
            placeholder="如：卡罗拉"
          />
          <van-field
            v-model="newVehicle.plate_number"
            label="车牌号"
            placeholder="如：京A12345"
          />
          <van-field
            v-model.number="newVehicle.initial_odometer"
            type="number"
            label="初始里程"
            placeholder="0"
            suffix="km"
          />
          <van-field
            v-model="newVehicle.fuel_type"
            label="燃油类型"
            placeholder="92号汽油"
          />
          <van-button round block type="primary" native-type="submit">
            添加
          </van-button>
          <van-button round block @click="showAddDialog = false">
            取消
          </van-button>
        </van-form>
      </div>
    </van-popup>

    <!-- 编辑车辆弹窗 -->
    <van-popup v-model:show="showEditDialog" position="bottom" round>
      <div class="dialog-content">
        <h3>编辑车辆</h3>
        <van-form @submit="onSubmitEdit">
          <van-field
            v-model="newVehicle.name"
            label="车辆名称"
            placeholder="如：我的卡罗拉"
            :rules="[{ required: true, message: '请输入车辆名称' }]"
          />
          <van-field
            v-model="newVehicle.brand"
            label="品牌"
            placeholder="如：丰田"
          />
          <van-field
            v-model="newVehicle.model"
            label="型号"
            placeholder="如：卡罗拉"
          />
          <van-field
            v-model="newVehicle.plate_number"
            label="车牌号"
            placeholder="如：京A12345"
          />
          <van-field
            v-model.number="newVehicle.initial_odometer"
            type="number"
            label="初始里程"
            placeholder="0"
            suffix="km"
          />
          <van-field
            v-model="newVehicle.fuel_type"
            label="燃油类型"
            placeholder="92号汽油"
          />
          <van-button round block type="primary" native-type="submit">
            保存
          </van-button>
          <van-button round block @click="showEditDialog = false">
            取消
          </van-button>
        </van-form>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.vehicle-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.empty-state {
  padding: 60px 20px;
}

.vehicle-list {
  padding: 16px;
}

.dialog-content {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-content h3 {
  margin: 0 0 16px 0;
  text-align: center;
}

.dialog-content .van-button {
  margin-top: 8px;
}
</style>
