<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatDate } from '@/utils/format'
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
  next_maintenance_odometer: undefined,
  next_maintenance_date: '',
})

const currentDateValue = ref<string[]>(formData.value.date.split('-'))
const nextDateValue = ref<string[]>([])

const onDateConfirm = (val: any) => {
  formData.value.date = val.selectedValues.join('-')
  showDatePicker.value = false
}

const onNextDateConfirm = (val: any) => {
  formData.value.next_maintenance_date = val.selectedValues.join('-')
  showNextDatePicker.value = false
}

const maintenanceTypes = [
  '机油更换',
  '机油滤芯',
  '空气滤芯',
  '空调滤芯',
  '火花塞',
  '刹车片',
  '轮胎更换',
  '变速箱油',
  '刹车油',
  '防冻液',
  '转向助力油',
  '正时皮带',
  '其他',
]

const upcomingTypes = [
  { text: '全部', value: '' },
  { text: '即将到期', value: 'upcoming' },
  { text: '已到期', value: 'overdue' },
]

const filterType = ref('')

onMounted(async () => {
  await vehiclesStore.fetchVehicles()
  if (vehiclesStore.currentVehicle) {
    formData.value.vehicle_id = vehiclesStore.currentVehicle.id
  }
  await loadMaintenances()
})

const loadMaintenances = async () => {
  loading.value = true
  try {
    const vehicleId = vehiclesStore.currentVehicleId ?? undefined
    const [all, upcomingData] = await Promise.all([
      maintenanceApi.getMaintenances(vehicleId),
      maintenanceApi.getUpcomingMaintenances(vehicleId),
    ])
    maintenances.value = all
    upcoming.value = upcomingData
  } finally {
    loading.value = false
  }
}

const onAdd = () => {
  editingRecord.value = null
  formData.value = {
    vehicle_id: vehiclesStore.currentVehicle?.id || 0,
    type: '',
    date: new Date().toISOString().split('T')[0],
    odometer: 0,
    cost: 0,
    description: '',
    next_maintenance_odometer: undefined,
    next_maintenance_date: '',
  }
  currentDateValue.value = formData.value.date.split('-')
  showFormDialog.value = true
}

const onEdit = (record: MaintenanceRecord) => {
  editingRecord.value = record
  formData.value = {
    vehicle_id: record.vehicle_id,
    type: record.type,
    date: record.date,
    odometer: record.odometer,
    cost: record.cost,
    description: record.description,
    next_maintenance_odometer: record.next_maintenance_odometer,
    next_maintenance_date: record.next_maintenance_date || '',
  }
  currentDateValue.value = formData.value.date.split('-')
  showFormDialog.value = true
}

const onDelete = async (id: number) => {
  await showConfirmDialog({
    title: '确认删除',
    message: '确定要删除这条保养记录吗？',
  })
  await maintenanceApi.deleteMaintenance(id)
  showToast({ message: '已删除', type: 'success' })
  await loadMaintenances()
}

const onSubmit = async () => {
  if (!formData.value.type) {
    showToast({ message: '请选择保养类型' })
    return
  }

  try {
    if (editingRecord.value) {
      await maintenanceApi.updateMaintenance(editingRecord.value.id, formData.value)
      showToast({ message: '更新成功', type: 'success' })
    } else {
      await maintenanceApi.createMaintenance(formData.value)
      showToast({ message: '添加成功', type: 'success' })
    }
    showFormDialog.value = false
    await loadMaintenances()
  } catch (error: any) {
    showToast({ message: error || '操作失败', type: 'fail' })
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

const vehicleName = computed(() => {
  const vehicle = (vehiclesStore.vehicles || []).find(v => v.id === formData.value.vehicle_id)
  return vehicle?.name || '选择车辆'
})
</script>

<template>
  <div class="maintenance-container">
    <van-nav-bar title="保养提醒">
      <template #right>
        <van-dropdown-menu>
          <van-dropdown-item
            v-model="filterType"
            :options="upcomingTypes"
            @change="() => {}"
          />
        </van-dropdown-menu>
      </template>
    </van-nav-bar>

    <!-- 即将到期提醒 -->
    <div v-if="upcoming.length > 0" class="upcoming-section">
      <van-notice-bar
        left-icon="volume-o"
        :text="`有 ${upcoming.length} 个保养项目即将到期`"
        background="#fff7e6"
        color="#ed6a0c"
      />
    </div>

    <van-pull-refresh v-model="loading" @refresh="loadMaintenances">
      <div v-if="filteredMaintenances.length === 0" class="empty-state">
        <van-empty description="暂无保养记录">
          <van-button type="primary" size="small" @click="onAdd">
            添加第一条记录
          </van-button>
        </van-empty>
      </div>

      <div v-else>
        <div v-for="item in filteredMaintenances" :key="item.id" class="record-card">
          <div class="record-header">
            <div class="record-type">
              <van-tag :type="isUpcoming(item) ? 'warning' : 'primary'">
                {{ item.type }}
              </van-tag>
              <van-tag v-if="isOverdue(item)" type="danger">已到期</van-tag>
            </div>
            <div class="record-actions">
              <van-icon name="edit-o" @click="onEdit(item)" />
              <van-icon name="delete-o" @click="onDelete(item.id)" />
            </div>
          </div>
          <div class="record-info">
            <div class="info-row">
              <span class="label">日期:</span>
              <span class="value">{{ item.date }}</span>
            </div>
            <div class="info-row">
              <span class="label">里程:</span>
              <span class="value">{{ item.odometer }} km</span>
            </div>
            <div v-if="item.cost" class="info-row">
              <span class="label">费用:</span>
              <span class="value">¥{{ item.cost }}</span>
            </div>
            <div v-if="item.description" class="info-row">
              <span class="label">备注:</span>
              <span class="value">{{ item.description }}</span>
            </div>
            <div v-if="item.next_maintenance_odometer || item.next_maintenance_date" class="next-maintenance">
              <span class="next-label">下次保养:</span>
              <span v-if="item.next_maintenance_odometer" class="next-value">
                {{ item.next_maintenance_odometer }} km
              </span>
              <span v-if="item.next_maintenance_date" class="next-value">
                {{ item.next_maintenance_date }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </van-pull-refresh>

    <van-floating-bubble
      axis="xy"
      icon="plus"
      magnetic="x"
      @click="onAdd"
    />

    <!-- 添加/编辑表单 -->
    <van-popup
      v-model:show="showFormDialog"
      position="bottom"
      :style="{ height: '70%' }"
      round
    >
      <div class="form-container">
        <h3>{{ editingRecord ? '编辑' : '添加' }}保养记录</h3>
        <van-form @submit="onSubmit">
          <van-field
            :value="vehicleName"
            label="车辆"
            placeholder="请选择车辆"
            readonly
            is-link
          />

          <van-field
            :value="formData.type"
            name="type"
            label="保养类型"
            placeholder="请选择类型"
            readonly
            is-link
            @click="showTypePicker = true"
            :rules="[{ required: true, message: '请选择保养类型' }]"
          />

          <van-field
            :value="formData.date"
            name="date"
            label="保养日期"
            placeholder="请选择日期"
            readonly
            is-link
            @click="showDatePicker = true"
            :rules="[{ required: true, message: '请选择日期' }]"
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

          <van-field
            v-model.number="formData.next_maintenance_odometer"
            name="next_odometer"
            type="number"
            label="下次保养里程"
            placeholder="可选"
            suffix="km"
          />

          <van-field
            :value="formData.next_maintenance_date"
            name="next_date"
            label="下次保养日期"
            placeholder="可选"
            readonly
            is-link
            @click="showNextDatePicker = true"
          />

          <div class="form-actions">
            <van-button round block type="primary" native-type="submit">
              {{ editingRecord ? '保存' : '添加' }}
            </van-button>
            <van-button round block @click="showFormDialog = false">
              取消
            </van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- 保养类型选择弹窗 -->
    <van-popup v-model:show="showTypePicker" position="bottom">
      <van-picker
        :columns="maintenanceTypes.map(t => ({ text: t, value: t }))"
        @confirm="(val: any) => { formData.type = val.selectedValues[0]; showTypePicker = false }"
        @cancel="showTypePicker = false"
      />
    </van-popup>

    <!-- 日期选择弹窗 -->
    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="currentDateValue"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>

    <!-- 下次保养日期选择弹窗 -->
    <van-popup v-model:show="showNextDatePicker" position="bottom">
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
.maintenance-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.upcoming-section {
  padding: 8px 0;
}

.empty-state {
  padding: 60px 20px;
}

.record-card {
  margin: 12px 16px;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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

.record-actions {
  display: flex;
  gap: 16px;
  color: #6b7280;
}

.record-actions .van-icon {
  font-size: 18px;
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
  color: #6b7280;
  font-size: 14px;
}

.info-row .value {
  color: #1f2937;
  font-size: 14px;
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

.form-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.form-container h3 {
  margin: 0 0 20px 0;
  text-align: center;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 20px;
}
</style>
