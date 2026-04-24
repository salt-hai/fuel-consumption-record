<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { showToast, showConfirmDialog } from 'vant'
import type { Vehicle } from '@/api/vehicles'
import { VEHICLE_ICONS } from '@/api/vehicles'

const router = useRouter()
const vehiclesStore = useVehiclesStore()

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showIconPicker = ref(false)
const editingVehicle = ref<Vehicle | null>(null)

const newVehicle = ref({
  name: '',
  icon: '🚗',
  brand: '',
  model: '',
  plate_number: '',
  initial_odometer: 0,
  fuel_type: '92号汽油',
})

const iconColumns = computed(() => {
  const cols = []
  for (let i = 0; i < VEHICLE_ICONS.length; i += 4) {
    cols.push(VEHICLE_ICONS.slice(i, i + 4))
  }
  return cols
})

onMounted(async () => {
  await vehiclesStore.fetchVehicles()
})

const onAdd = () => {
  newVehicle.value = {
    name: '',
    icon: '🚗',
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
    icon: vehicle.icon,
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

const onIconSelect = (icon: string) => {
  newVehicle.value.icon = icon
  showIconPicker.value = false
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
  <div class="vehicle-page">
    <van-nav-bar title="车辆管理" />

    <!-- 空状态 -->
    <div v-if="vehiclesStore.vehicles.length === 0" class="empty-state">
      <div class="empty-icon">🚗</div>
      <p class="empty-title">还没有添加车辆</p>
      <p class="empty-desc">添加第一辆车开始记录油耗吧</p>
      <van-button type="primary" round size="small" @click="onAdd">
        添加车辆
      </van-button>
    </div>

    <!-- 车辆列表 -->
    <div v-else class="vehicle-list">
      <div
        v-for="vehicle in vehiclesStore.vehicles"
        :key="vehicle.id"
        class="vehicle-card"
      >
        <div class="vehicle-header">
          <div class="vehicle-icon">{{ vehicle.icon }}</div>
          <div class="vehicle-info">
            <div class="vehicle-name">{{ vehicle.name }}</div>
            <div class="vehicle-details">{{ vehicle.brand || '' }} {{ vehicle.model || '' }}</div>
          </div>
          <van-tag v-if="!vehicle.is_active" type="warning" round>已停用</van-tag>
        </div>
        <div class="vehicle-meta">
          <span v-if="vehicle.plate_number" class="meta-item">
            <span class="meta-label">车牌</span>
            <span class="meta-value">{{ vehicle.plate_number }}</span>
          </span>
          <span class="meta-item">
            <span class="meta-label">燃油</span>
            <span class="meta-value">{{ vehicle.fuel_type }}</span>
          </span>
          <span class="meta-item">
            <span class="meta-label">初始里程</span>
            <span class="meta-value">{{ vehicle.initial_odometer }} km</span>
          </span>
        </div>
        <div class="vehicle-actions">
          <van-button size="small" type="primary" round @click="onEdit(vehicle)">
            编辑
          </van-button>
          <van-button size="small" type="danger" plain round @click="onDelete(vehicle)">
            删除
          </van-button>
        </div>
      </div>
    </div>

    <!-- FAB 添加按钮 -->
    <van-button
      round
      icon="plus"
      class="fab-button"
      @click="onAdd"
    />

    <!-- 添加车辆弹窗 -->
    <van-popup v-model:show="showAddDialog" position="bottom" round>
      <div class="dialog-content">
        <h3>添加车辆</h3>
        <van-form @submit="onSubmitAdd">
          <van-field
            v-model="newVehicle.icon"
            label="图标"
            readonly
            is-link
            @click="showIconPicker = true"
          >
            <template #input>
              <span class="icon-preview">{{ newVehicle.icon }}</span>
            </template>
          </van-field>
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
            v-model="newVehicle.icon"
            label="图标"
            readonly
            is-link
            @click="showIconPicker = true"
          >
            <template #input>
              <span class="icon-preview">{{ newVehicle.icon }}</span>
            </template>
          </van-field>
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

    <!-- 图标选择弹窗 -->
    <van-popup v-model:show="showIconPicker" position="bottom" round>
      <div class="icon-picker-content">
        <h3>选择图标</h3>
        <div class="icon-grid">
          <div
            v-for="icon in VEHICLE_ICONS"
            :key="icon"
            class="icon-item"
            :class="{ selected: newVehicle.icon === icon }"
            @click="onIconSelect(icon)"
          >
            {{ icon }}
          </div>
        </div>
        <van-button round block @click="showIconPicker = false">
          取消
        </van-button>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.vehicle-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #323233;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #969799;
  margin: 0 0 24px 0;
}

/* 车辆列表 */
.vehicle-list {
  padding: 12px;
}

.vehicle-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.vehicle-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.vehicle-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.vehicle-icon {
  font-size: 36px;
  flex-shrink: 0;
}

.vehicle-info {
  flex: 1;
  min-width: 0;
}

.vehicle-name {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 2px;
}

.vehicle-details {
  font-size: 13px;
  color: #969799;
}

.vehicle-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #f5f6f7;
  border-bottom: 1px solid #f5f6f7;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 11px;
  color: #969799;
}

.meta-value {
  font-size: 13px;
  color: #323233;
  font-weight: 500;
}

.vehicle-actions {
  display: flex;
  gap: 8px;
}

.vehicle-actions .van-button {
  flex: 1;
}

/* FAB 按钮 */
.fab-button {
  position: fixed;
  right: 16px;
  bottom: 76px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  box-shadow: 0 4px 16px rgba(25, 137, 250, 0.35);
  border: none;
  z-index: 100;
}

.fab-button:active {
  transform: scale(0.95);
  box-shadow: 0 2px 10px rgba(25, 137, 250, 0.4);
}

/* 弹窗内容 */
.dialog-content {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-content h3 {
  margin: 0 0 16px 0;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #323233;
}

.dialog-content .van-button {
  margin-top: 8px;
}

.dialog-content .van-field {
  padding: 12px 0;
}

.icon-preview {
  font-size: 28px;
}

/* 图标选择 */
.icon-picker-content {
  padding: 20px;
}

.icon-picker-content h3 {
  margin: 0 0 16px 0;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #323233;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.icon-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  border: 1px solid #ebedf0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.icon-item.selected {
  background: linear-gradient(135deg, #1989fa 0%, #096dd9 100%);
  border-color: #1989fa;
  color: white;
  box-shadow: 0 2px 8px rgba(25, 137, 250, 0.3);
}

.icon-item:active {
  transform: scale(0.95);
}
</style>
