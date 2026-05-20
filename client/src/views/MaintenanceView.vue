<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useVehiclesStore } from '@/stores/vehicles'
import * as maintenanceApi from '@/api/maintenance'
import type { MaintenanceRecord, CreateMaintenanceRequest } from '@/api/maintenance'
import { showToast, showConfirmDialog } from 'vant'

const vehiclesStore = useVehiclesStore()

const maintenances = ref<MaintenanceRecord[]>([])
const upcoming = ref<MaintenanceRecord[]>([])
const loading = ref(false)

const showFormDialog = ref(false)
const showTypePicker = ref(false)
const showDatePicker = ref(false)
const showNextDatePicker = ref(false)
const editingRecord = ref<MaintenanceRecord | null>(null)

const formData = ref<CreateMaintenanceRequest>({
  vehicle_id: 0,
  type: '',
  date: new Date().toISOString().split('T')[0],
  odometer: 0,
  cost: 0,
  description: '',
})

const currentDateValue = ref<string[]>(formData.value.date.split('-'))
const nextDateValue = ref<string[]>([])
const typeDisplayValue = ref('')
const dateDisplayValue = ref(formData.value.date)
const nextDateDisplayValue = ref('')

// 车辆选择器
const showVehiclePicker = ref(false)
const vehiclePickerValue = ref<number[]>([])

const vehicleColumns = computed(() => {
  return (vehiclesStore.vehicles || []).map(v => ({
    text: `${v.icon} ${v.name}`,
    value: v.id
  }))
})

const openVehiclePicker = () => {
  vehiclePickerValue.value = [vehiclesStore.currentVehicleId || vehiclesStore.vehicles?.[0]?.id || 0]
  showVehiclePicker.value = true
}

const onVehicleSelect = ({ selectedValues }: { selectedValues: number[] }) => {
  const vehicleId = selectedValues[0]
  if (vehicleId) {
    vehiclesStore.setCurrentVehicle(vehicleId)
  }
  showVehiclePicker.value = false
}

const currentVehicle = computed(() => vehiclesStore.currentVehicle)

const onDateConfirm = (val: any) => {
  const dateStr = val.selectedValues.join('-')
  formData.value.date = dateStr
  dateDisplayValue.value = dateStr
  currentDateValue.value = val.selectedValues
  showDatePicker.value = false
}

const onNextDateConfirm = (val: any) => {
  const dateStr = val.selectedValues.join('-')
  formData.value.next_maintenance_date = dateStr
  nextDateDisplayValue.value = dateStr
  nextDateValue.value = val.selectedValues
  showNextDatePicker.value = false
}

const maintenanceTypes = [
  { text: '机油更换', icon: '🛢️' },
  { text: '机油滤芯', icon: '🔧' },
  { text: '空气滤芯', icon: '🌬️' },
  { text: '空调滤芯', icon: '❄️' },
  { text: '火花塞', icon: '⚡' },
  { text: '刹车片', icon: '🛑' },
  { text: '轮胎更换', icon: '🛞' },
  { text: '变速箱油', icon: '⚙️' },
  { text: '刹车油', icon: '🔴' },
  { text: '防冻液', icon: '🧊' },
  { text: '转向助力油', icon: '🔄' },
  { text: '正时皮带', icon: '🔗' },
  { text: '其他', icon: '🔩' },
]

const getTypeIcon = (type: string) => {
  return maintenanceTypes.find(t => t.text === type)?.icon || '🔩'
}

const filterType = ref('')

onMounted(async () => {
  await vehiclesStore.fetchVehicles()
  if (vehiclesStore.currentVehicle) {
    formData.value.vehicle_id = vehiclesStore.currentVehicle.id
  }
  await loadMaintenances()
})

// 监听车辆切换
watch(() => vehiclesStore.currentVehicleId, async () => {
  await loadMaintenances()
})

const loadMaintenances = async () => {
  loading.value = true
  try {
    const vehicleId = vehiclesStore.currentVehicleId ?? undefined
    const [all, upcomingData] = await Promise.all([
      maintenanceApi.getMaintenanceRecords(vehicleId),
      maintenanceApi.getUpcomingMaintenance(vehicleId),
    ])
    maintenances.value = all
    upcoming.value = upcomingData
  } finally {
    loading.value = false
  }
}

const onAdd = () => {
  editingRecord.value = null
  const today = new Date().toISOString().split('T')[0]
  formData.value = {
    vehicle_id: vehiclesStore.currentVehicle?.id || 0,
    type: '',
    date: today,
    odometer: 0,
    cost: 0,
    description: '',
  }
  typeDisplayValue.value = ''
  dateDisplayValue.value = today
  nextDateDisplayValue.value = ''
  currentDateValue.value = today.split('-')
  nextDateValue.value = []
  showFormDialog.value = true
}

const onEdit = (record: MaintenanceRecord) => {
  editingRecord.value = record
  formData.value = {
    vehicle_id: record.vehicle_id,
    type: record.type,
    date: record.date,
    odometer: record.odometer,
    cost: record.cost || 0,
    description: record.description || '',
    next_maintenance_odometer: record.next_maintenance_odometer,
    next_maintenance_date: record.next_maintenance_date,
  }
  typeDisplayValue.value = `${getTypeIcon(record.type)} ${record.type}`
  dateDisplayValue.value = record.date
  nextDateDisplayValue.value = record.next_maintenance_date || ''
  currentDateValue.value = record.date.split('-')
  if (record.next_maintenance_date) {
    nextDateValue.value = record.next_maintenance_date.split('-')
  } else {
    nextDateValue.value = []
  }
  showFormDialog.value = true
}

const onDelete = async (id: number) => {
  await showConfirmDialog({
    title: '确认删除',
    message: '确定要删除这条保养记录吗？',
  })
  await maintenanceApi.deleteMaintenanceRecord(id)
  showToast({ message: '已删除', type: 'success' })
  await loadMaintenances()
}

const onToggleCompleted = async (record: MaintenanceRecord) => {
  await maintenanceApi.updateMaintenanceRecord(record.id, {
    is_completed: !record.is_completed,
  })
  showToast({ message: record.is_completed ? '已取消完成' : '已完成', type: 'success' })
  await loadMaintenances()
}

const onSubmit = async () => {
  if (!formData.value.type) {
    showToast({ message: '请选择保养类型' })
    return
  }

  try {
    if (editingRecord.value) {
      await maintenanceApi.updateMaintenanceRecord(editingRecord.value.id, formData.value)
      showToast({ message: '更新成功', type: 'success' })
    } else {
      await maintenanceApi.createMaintenanceRecord(formData.value)
      showToast({ message: '添加成功', type: 'success' })
    }
    showFormDialog.value = false
    await loadMaintenances()
  } catch (error) {
    // 错误已由 API 拦截器自动显示
  }
}

const isUpcoming = (item: MaintenanceRecord) => {
  return upcoming.value.some(u => u.id === item.id)
}

const isOverdue = (item: MaintenanceRecord) => {
  if (!item.next_maintenance_date) return false
  const today = new Date().toISOString().split('T')[0]
  return item.next_maintenance_date < today
}

const filteredMaintenances = computed(() => {
  if (filterType.value === 'upcoming') {
    return maintenances.value.filter(m => isUpcoming(m))
  } else if (filterType.value === 'overdue') {
    return maintenances.value.filter(m => isOverdue(m))
  }
  return maintenances.value
})
</script>

<template>
  <div class="maintenance-page">
    <van-nav-bar title="保养记录">
      <template #right>
        <div
          v-if="currentVehicle"
          class="nav-vehicle"
          @click="openVehiclePicker"
        >
          <span class="vehicle-icon">{{ currentVehicle.icon }}</span>
          <span class="vehicle-name">{{ currentVehicle.name }}</span>
          <van-icon
            name="arrow-down"
            size="12"
          />
        </div>
      </template>
    </van-nav-bar>

    <!-- 即将到期提醒 -->
    <div
      v-if="upcoming.length > 0"
      class="upcoming-section"
    >
      <van-notice-bar
        left-icon="volume-o"
        :text="`有 ${upcoming.length} 个保养项目即将到期`"
        background="#fff7e6"
        color="#ed6a0c"
      />
    </div>

    <!-- 筛选 -->
    <div class="filter-bar">
      <van-dropdown-menu>
        <van-dropdown-item
          v-model="filterType"
          :options="[
            { text: '全部', value: '' },
            { text: '即将到期', value: 'upcoming' },
            { text: '已到期', value: 'overdue' },
          ]"
        />
      </van-dropdown-menu>
    </div>

    <van-pull-refresh
      v-model="loading"
      @refresh="loadMaintenances"
    >
      <!-- 空状态 -->
      <div
        v-if="filteredMaintenances.length === 0"
        class="empty-state"
      >
        <van-empty description="暂无保养记录">
          <van-button
            type="primary"
            size="small"
            @click="onAdd"
          >
            添加第一条记录
          </van-button>
        </van-empty>
      </div>

      <!-- 记录列表 -->
      <div
        v-else
        class="records-list"
      >
        <van-swipe-cell
          v-for="item in filteredMaintenances"
          :key="item.id"
        >
          <div
            class="record-card"
            :class="{ 'record-completed': item.is_completed }"
            @click="onEdit(item)"
          >
            <div class="record-header">
              <div class="record-type">
                <van-tag :type="item.is_completed ? 'success' : isUpcoming(item) ? 'warning' : 'primary'">
                  <span class="tag-icon">{{ getTypeIcon(item.type) }}</span>
                  {{ item.type }}
                </van-tag>
                <van-tag
                  v-if="isOverdue(item) && !item.is_completed"
                  type="danger"
                >
                  已到期
                </van-tag>
              </div>
            </div>
            <div class="record-info">
              <div class="info-row">
                <span class="label">日期</span>
                <span class="value">{{ item.date }}</span>
              </div>
              <div class="info-row">
                <span class="label">里程</span>
                <span class="value">{{ item.odometer.toLocaleString() }} km</span>
              </div>
              <div
                v-if="item.cost"
                class="info-row"
              >
                <span class="label">费用</span>
                <span class="value cost">¥{{ item.cost }}</span>
              </div>
              <div
                v-if="item.description"
                class="info-row"
              >
                <span class="label">备注</span>
                <span class="value">{{ item.description }}</span>
              </div>
              <div
                v-if="item.next_maintenance_odometer || item.next_maintenance_date"
                class="next-maintenance"
              >
                <span class="next-label">下次保养:</span>
                <span
                  v-if="item.next_maintenance_odometer"
                  class="next-value"
                >
                  {{ item.next_maintenance_odometer.toLocaleString() }} km
                </span>
                <span
                  v-if="item.next_maintenance_date"
                  class="next-value"
                >
                  {{ item.next_maintenance_date }}
                </span>
              </div>
            </div>
            <div class="record-footer">
              <van-button
                v-if="!item.is_completed"
                size="small"
                type="success"
                plain
                @click.stop="onToggleCompleted(item)"
              >
                标记完成
              </van-button>
              <van-button
                v-else
                size="small"
                type="default"
                plain
                @click.stop="onToggleCompleted(item)"
              >
                取消完成
              </van-button>
              <van-icon
                name="arrow"
                class="arrow-icon"
              />
            </div>
          </div>

          <template #right>
            <van-button
              square
              type="danger"
              text="删除"
              class="delete-button"
              @click="onDelete(item.id)"
            />
          </template>
        </van-swipe-cell>
      </div>
    </van-pull-refresh>

    <!-- FAB 添加按钮 -->
    <van-button
      round
      icon="plus"
      class="fab-button"
      @click="onAdd"
    />

    <!-- 车辆选择器 -->
    <van-popup
      v-model:show="showVehiclePicker"
      position="bottom"
      round
    >
      <van-picker
        :columns="vehicleColumns"
        :model-value="vehiclePickerValue"
        @confirm="onVehicleSelect"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>

    <!-- 添加/编辑表单弹窗 -->
    <van-popup
      v-model:show="showFormDialog"
      position="bottom"
      :style="{ height: '70%' }"
      round
    >
      <div class="popup-content">
        <div class="popup-header">
          <h3>{{ editingRecord ? '编辑' : '添加' }}保养记录</h3>
          <van-icon
            name="cross"
            @click="showFormDialog = false"
          />
        </div>
        <van-form
          class="popup-form"
          @submit="onSubmit"
        >
          <van-field
            v-model="typeDisplayValue"
            name="type"
            label="保养类型"
            placeholder="请选择类型"
            readonly
            is-link
            :rules="[{ required: true, message: '请选择保养类型' }]"
            @click="showTypePicker = true"
          />

          <van-field
            v-model="dateDisplayValue"
            name="date"
            label="保养日期"
            placeholder="请选择日期"
            readonly
            is-link
            :rules="[{ required: true, message: '请选择日期' }]"
            @click="showDatePicker = true"
          />

          <van-field
            v-model.number="formData.odometer"
            name="odometer"
            type="number"
            label="当前里程"
            placeholder="请输入里程"
            suffix="km"
            :rules="[{ required: true, message: '请输入里程' }]"
          />

          <van-field
            v-model.number="formData.cost"
            name="cost"
            type="number"
            label="费用"
            placeholder="请输入费用"
            suffix="元"
          />

          <van-field
            v-model="formData.description"
            name="description"
            type="textarea"
            label="备注"
            placeholder="请输入备注"
            rows="2"
          />

          <div class="form-divider">
            <span>下次保养（可选）</span>
          </div>

          <van-field
            v-model.number="formData.next_maintenance_odometer"
            name="next_maintenance_odometer"
            type="number"
            label="下次里程"
            placeholder="请输入里程"
            suffix="km"
          />

          <van-field
            v-model="nextDateDisplayValue"
            name="next_maintenance_date"
            label="下次日期"
            placeholder="请选择日期"
            readonly
            is-link
            @click="showNextDatePicker = true"
          />

          <div class="popup-actions">
            <van-button
              round
              block
              @click="showFormDialog = false"
            >
              取消
            </van-button>
            <van-button
              round
              block
              type="primary"
              native-type="submit"
            >
              {{ editingRecord ? '保存' : '添加' }}
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 保养类型选择弹窗 -->
    <van-popup
      v-model:show="showTypePicker"
      position="bottom"
      round
      class="type-picker-popup"
    >
      <div class="type-picker-header">
        <h3>选择保养类型</h3>
        <van-icon
          name="cross"
          @click="showTypePicker = false"
        />
      </div>
      <div class="type-picker-grid">
        <div
          v-for="item in maintenanceTypes"
          :key="item.text"
          class="type-picker-item"
          :class="{ active: formData.type === item.text }"
          @click="formData.type = item.text; typeDisplayValue = `${item.icon} ${item.text}`; showTypePicker = false"
        >
          <span class="type-icon">{{ item.icon }}</span>
          <span class="type-name">{{ item.text }}</span>
        </div>
      </div>
    </van-popup>

    <!-- 保养日期选择弹窗 -->
    <van-popup
      v-model:show="showDatePicker"
      position="bottom"
      round
    >
      <van-date-picker
        v-model="currentDateValue"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- 下次保养日期选择弹窗 -->
    <van-popup
      v-model:show="showNextDatePicker"
      position="bottom"
      round
    >
      <van-date-picker
        v-model="nextDateValue"
        :min-date="new Date()"
        @confirm="onNextDateConfirm"
        @cancel="showNextDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.maintenance-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 导航栏车辆选择 */
.nav-vehicle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #323233;
  cursor: pointer;
}

.vehicle-icon {
  font-size: 16px;
}

.vehicle-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upcoming-section {
  padding: 8px 0;
}

.filter-bar {
  padding: 0 4px;
}

.empty-state {
  padding: 60px 20px;
}

/* 记录列表 */
.records-list {
  padding: 12px;
}

.record-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}

.record-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #1989fa;
}

.record-card.record-completed::before {
  background: #07c160;
}

.record-card.record-completed {
  opacity: 0.7;
}

.record-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.record-type {
  display: flex;
  gap: 8px;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
}

.info-row .label {
  color: #969799;
  font-size: 14px;
}

.info-row .value {
  color: #323233;
  font-size: 14px;
}

.info-row .value.cost {
  color: #ee0a24;
  font-weight: 600;
}

.next-maintenance {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
}

.next-label {
  color: #ed6a0c;
  font-size: 13px;
}

.next-value {
  color: #ed6a0c;
  font-size: 13px;
}

.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f5f6f7;
  margin-top: 12px;
}

.arrow-icon {
  color: #c8c9cc;
  font-size: 14px;
}

/* 删除按钮 */
.delete-button {
  height: 100% !important;
  border-radius: 0 12px 12px 0;
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
}

/* 弹窗样式 */
.popup-content {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f5f6f7;
  flex-shrink: 0;
}

.popup-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.popup-header .van-icon {
  font-size: 20px;
  color: #969799;
  cursor: pointer;
}

.popup-form {
  padding: 16px 20px;
  flex: 1;
  overflow-y: auto;
}

.popup-form .van-field {
  padding: 12px 0;
  background: transparent;
}

.form-divider {
  padding: 16px 0 8px;
  border-top: 1px solid #f5f6f7;
  margin-top: 8px;
}

.form-divider span {
  font-size: 14px;
  color: #969799;
}

.popup-actions {
  display: flex;
  gap: 12px;
  padding: 0 20px 20px;
  flex-shrink: 0;
}

.popup-actions .van-button {
  flex: 1;
  height: 44px;
}

/* 类型选择器 */
.type-picker-popup {
  padding: 0;
}

.type-picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f5f6f7;
}

.type-picker-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.type-picker-header .van-icon {
  font-size: 20px;
  color: #969799;
  cursor: pointer;
}

.type-picker-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px 20px;
}

.type-picker-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: 12px;
  background: #f7f8fa;
  cursor: pointer;
  transition: all 0.2s;
}

.type-picker-item:active {
  transform: scale(0.95);
}

.type-picker-item.active {
  background: rgba(25, 137, 250, 0.1);
  border: 1px solid #1989fa;
}

.type-picker-item .type-icon {
  font-size: 28px;
}

.type-picker-item .type-name {
  font-size: 12px;
  color: #323233;
  text-align: center;
}

.tag-icon {
  margin-right: 2px;
}
</style>
