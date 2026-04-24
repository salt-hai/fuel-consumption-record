<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useVehiclesStore } from '@/stores/vehicles'
import { showToast } from 'vant'
import type { CreateRecordRequest, UpdateRecordRequest, FuelRecord } from '@/api/records'

const router = useRouter()
const route = useRoute()
const recordsStore = useRecordsStore()
const vehiclesStore = useVehiclesStore()

const recordId = computed(() => parseInt(route.params.id as string))
const isEdit = computed(() => !!recordId.value)

const formData = ref({
  vehicle_id: 0,
  date: new Date().toISOString().split('T')[0],
  odometer: 0,
  volume: 0,
  total_cost: 0,
  unit_price: 0,
  full_tank: true,
  gas_station: '',
  notes: '',
})

const lastOdometer = ref(0)
const loading = ref(false)
const submitting = ref(false)
const showVehiclePicker = ref(false)
const showDatePicker = ref(false)
const currentDateValue = ref<string[]>(formData.value.date.split('-'))
const vehiclePickerValue = ref<number[]>([])
const vehicleDisplayValue = ref('点击选择车辆')
const dateDisplayValue = ref(formData.value.date)
const unitPriceDisplay = ref('0.00')
const showCalcInfo = ref(false)

// 计算单价
watch(() => [formData.value.volume, formData.value.total_cost], ([newVolume, newCost]) => {
  if (newVolume > 0 && newCost > 0) {
    unitPriceDisplay.value = (newCost / newVolume).toFixed(2)
    formData.value.unit_price = parseFloat(unitPriceDisplay.value)
  } else {
    unitPriceDisplay.value = '0.00'
    formData.value.unit_price = 0
  }
}, { immediate: true })

watch(() => unitPriceDisplay.value, (newVal) => {
  const parsed = parseFloat(newVal)
  if (!isNaN(parsed)) {
    formData.value.unit_price = parsed
  }
})

const onDateConfirm = ({ selectedValues }: any) => {
  formData.value.date = selectedValues.join('-')
  currentDateValue.value = selectedValues
  dateDisplayValue.value = selectedValues.join('-')
  showDatePicker.value = false
}

const updateVehicleDisplay = () => {
  const vehicle = (vehiclesStore.vehicles || []).find(v => v.id === formData.value.vehicle_id)
  vehicleDisplayValue.value = vehicle ? `${vehicle.icon} ${vehicle.name}` : '点击选择车辆'
}

onMounted(async () => {
  await vehiclesStore.fetchVehicles()

  if (vehiclesStore.currentVehicle) {
    formData.value.vehicle_id = vehiclesStore.currentVehicle.id
    vehiclePickerValue.value = [vehiclesStore.currentVehicle.id]
  }
  updateVehicleDisplay()

  if (isEdit.value) {
    await loadRecord()
  } else {
    lastOdometer.value = vehiclesStore.currentVehicle?.initial_odometer || 0
    await recordsStore.fetchRecords({ vehicle_id: formData.value.vehicle_id, page_size: 1 })
    if (recordsStore.records.length > 0) {
      lastOdometer.value = recordsStore.records[0].odometer
    }
  }
})

const loadRecord = async () => {
  loading.value = true
  try {
    const record = await recordsStore.fetchRecord(recordId.value)
    formData.value = {
      vehicle_id: record.vehicle_id,
      date: record.date,
      odometer: record.odometer,
      volume: record.volume,
      total_cost: record.total_cost,
      unit_price: record.unit_price || 0,
      full_tank: record.full_tank,
      gas_station: record.gas_station || '',
      notes: record.notes || '',
    }
    vehiclePickerValue.value = [record.vehicle_id]
    currentDateValue.value = record.date.split('-')
    dateDisplayValue.value = record.date
    unitPriceDisplay.value = (record.unit_price || 0).toFixed(2)
    updateVehicleDisplay()
  } finally {
    loading.value = false
  }
}

const onSubmit = async () => {
  if (!formData.value.vehicle_id) {
    showToast({ message: '请选择车辆' })
    return
  }

  if (formData.value.volume <= 0) {
    showToast({ message: '加油量必须大于0' })
    return
  }

  if (formData.value.total_cost <= 0) {
    showToast({ message: '总金额必须大于0' })
    return
  }

  submitting.value = true
  // 使用轻量 toast 提示而不是按钮 loading
  const toast = showToast({
    message: isEdit.value ? '保存中...' : '提交中...',
    duration: 0,
    forbidClick: true,
    loadingType: 'circular',
  })

  try {
    if (isEdit.value) {
      await recordsStore.updateRecord(recordId.value, formData.value as UpdateRecordRequest)
      toast({ message: '更新成功', type: 'success' })
    } else {
      await recordsStore.createRecord(formData.value as CreateRecordRequest)
      toast({ message: '添加成功', type: 'success' })
    }
    router.back()
  } catch (error) {
    toast.close()
    // 错误已由 API 拦截器自动显示
  } finally {
    submitting.value = false
  }
}

const vehicleColumns = computed(() => {
  return (vehiclesStore.vehicles || []).map(v => ({
    text: `${v.icon} ${v.name}`,
    value: v.id
  }))
})

const onSelectVehicle = ({ selectedValues }: any) => {
  formData.value.vehicle_id = selectedValues[0]
  vehiclePickerValue.value = selectedValues
  showVehiclePicker.value = false
  updateVehicleDisplay()
}
</script>

<template>
  <div class="form-page">
    <van-nav-bar
      :title="isEdit ? '编辑记录' : '添加记录'"
      left-arrow
      @click-left="router.back()"
    />

    <van-form @submit="onSubmit" class="form-content">
      <!-- 基本信息 -->
      <div class="form-section">
        <div class="section-header">基本信息</div>

        <div class="form-card">
          <van-field
            v-model="vehicleDisplayValue"
            label="车辆"
            placeholder="点击选择车辆"
            readonly
            is-link
            required
            @click="showVehiclePicker = true"
          />

          <van-field
            v-model="dateDisplayValue"
            label="日期"
            placeholder="请选择日期"
            readonly
            is-link
            required
            @click="showDatePicker = true"
          />

          <van-field
            v-model.number="formData.odometer"
            type="number"
            label="当前里程"
            placeholder="请输入里程"
            suffix="km"
            required
            :rules="[{ required: true, message: '请输入里程' }]"
          >
            <template #extra>
              <span v-if="!isEdit && lastOdometer > 0" class="hint">
                上次: {{ lastOdometer }} km
              </span>
            </template>
          </van-field>
        </div>
      </div>

      <!-- 加油信息 -->
      <div class="form-section">
        <div class="section-header">
          加油信息
          <span class="section-toggle" @click="showCalcInfo = !showCalcInfo">
            {{ showCalcInfo ? '收起' : '计算说明' }}
            <van-icon :name="showCalcInfo ? 'arrow-up' : 'arrow-down'" />
          </span>
        </div>

        <div class="form-card">
          <van-field
            v-model.number="formData.volume"
            type="number"
            label="加油量"
            placeholder="请输入加油量"
            suffix="L"
            required
            :rules="[{ required: true, message: '请输入加油量' }]"
          />

          <van-field
            v-model.number="formData.total_cost"
            type="number"
            label="总金额"
            placeholder="请输入总金额"
            suffix="元"
            required
            :rules="[{ required: true, message: '请输入总金额' }]"
          />

          <van-field
            v-model.number="unitPriceDisplay"
            type="number"
            label="单价"
            placeholder="自动计算"
            suffix="元/L"
          />

          <van-field name="full_tank" label="是否加满">
            <template #input>
              <van-switch v-model="formData.full_tank" size="20" />
            </template>
          </van-field>
        </div>

        <!-- 油耗计算说明 -->
        <div v-if="showCalcInfo" class="calc-card">
          <div class="calc-content">
            <div class="calc-formula">
              <span class="formula-label">公式：</span>
              <span class="formula-text">油耗 = 累积加油量 ÷ 累积里程 × 100</span>
            </div>
            <div class="calc-example">
              <p class="example-title">📝 举例说明：</p>
              <div class="example-item">
                <span class="example-label">第1次加满</span>
                <span class="example-value">1000km · 40L</span>
              </div>
              <div class="example-item">
                <span class="example-label">第2次(未满)</span>
                <span class="example-value">1200km · 30L</span>
              </div>
              <div class="example-item">
                <span class="example-label">第3次加满</span>
                <span class="example-value">1600km · 45L</span>
              </div>
              <div class="example-result">
                <span>累积加油量: 75L · 累积里程: 600km</span>
                <span class="result-value">油耗 = 75÷600×100 = <strong>12.5L/100km</strong></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 其他信息 -->
      <div class="form-section">
        <div class="section-header">其他信息（可选）</div>

        <div class="form-card">
          <van-field
            v-model="formData.gas_station"
            label="加油站"
            placeholder="如：中石化xxx站"
          />

          <van-field
            v-model="formData.notes"
            type="textarea"
            label="备注"
            placeholder="添加备注..."
            rows="2"
            maxlength="200"
            show-word-limit
          />
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :disabled="submitting"
          size="large"
        >
          {{ isEdit ? '保存修改' : '添加记录' }}
        </van-button>
      </div>
    </van-form>

    <!-- 车辆选择弹窗 -->
    <van-popup v-model:show="showVehiclePicker" position="bottom" round>
      <van-picker
        :columns="vehicleColumns"
        :model-value="vehiclePickerValue"
        @confirm="onSelectVehicle"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>

    <!-- 日期选择弹窗 -->
    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        :model-value="currentDateValue"
        :max-date="new Date()"
        :min-date="new Date(2020, 0, 1)"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.form-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 30px;
}

.form-content {
  padding: 12px;
}

/* 表单区块 */
.form-section {
  margin-bottom: 12px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px 4px;
  font-size: 13px;
  font-weight: 600;
  color: #323233;
}

.section-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #1989fa;
  cursor: pointer;
  font-size: 12px;
}

/* 表单卡片 */
.form-card {
  background: white;
  border-radius: 12px;
  padding: 4px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.form-card .van-field {
  padding: 12px 16px;
}

/* 油耗计算说明 */
.calc-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-top: 10px;
  overflow: hidden;
}

.calc-content {
  padding: 12px;
}

.calc-formula {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.formula-label {
  color: #1989fa;
  font-weight: 600;
  font-size: 12px;
}

.formula-text {
  color: #323233;
  font-size: 14px;
  font-weight: 500;
}

.calc-example {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.example-title {
  color: #323233;
  font-size: 12px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.example-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
  color: #646566;
}

.example-label {
  flex-shrink: 0;
}

.example-value {
  color: #323233;
}

.example-result {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 0 0;
  margin-top: 8px;
  border-top: 1px dashed #ebedf0;
}

.result-value {
  color: #1989fa;
  font-size: 13px;
}

/* 提交按钮 */
.form-actions {
  padding: 12px;
}
</style>
