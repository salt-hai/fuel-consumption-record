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

// 计算单价（当用户修改加油量或总金额时自动计算）
watch(() => [formData.value.volume, formData.value.total_cost], ([newVolume, newCost]) => {
  if (newVolume > 0 && newCost > 0) {
    unitPriceDisplay.value = (newCost / newVolume).toFixed(2)
    formData.value.unit_price = parseFloat(unitPriceDisplay.value)
  } else {
    unitPriceDisplay.value = '0.00'
    formData.value.unit_price = 0
  }
}, { immediate: true })

// 监听单价手动输入，更新 formData
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

// 更新车辆显示名称
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
    // 获取上次里程作为参考
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
  try {
    if (isEdit.value) {
      await recordsStore.updateRecord(recordId.value, formData.value as UpdateRecordRequest)
      showToast({ message: '更新成功', type: 'success' })
    } else {
      await recordsStore.createRecord(formData.value as CreateRecordRequest)
      showToast({ message: '添加成功', type: 'success' })
    }
    router.back()
  } catch (error: any) {
    showToast({ message: error || '操作失败', type: 'fail' })
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

const onSelectVehicle = ({ selectedValues, selectedOptions }: any) => {
  formData.value.vehicle_id = selectedValues[0]
  vehiclePickerValue.value = selectedValues
  showVehiclePicker.value = false
  updateVehicleDisplay()
}
</script>

<template>
  <div class="record-form-container">
    <van-nav-bar
      :title="isEdit ? '编辑记录' : '添加记录'"
      left-arrow
      @click-left="router.back()"
    />

    <van-form @submit="onSubmit">
      <van-cell-group inset>
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
          placeholder="自动计算或手动输入"
          suffix="元/L"
        />

        <van-field name="full_tank" label="是否加满">
          <template #input>
            <van-switch v-model="formData.full_tank" />
          </template>
        </van-field>

        <van-field
          v-model="formData.gas_station"
          label="加油站"
          placeholder="请输入加油站名称（可选）"
        />

        <van-field
          v-model="formData.notes"
          type="textarea"
          label="备注"
          placeholder="请输入备注（可选）"
          rows="2"
          maxlength="200"
          show-word-limit
        />
      </van-cell-group>

      <!-- 油耗计算说明 -->
      <van-cell-group inset class="info-section">
        <van-cell title="油耗计算说明" :border="false">
          <template #icon>
            <van-icon name="info-o" class="info-icon" />
          </template>
        </van-cell>
        <van-cell :border="false">
          <template #title>
            <div class="calc-info">
              <p><strong>计算公式：</strong></p>
              <p class="formula">油耗(L/100km) = 累积加油量 ÷ 累积里程 × 100</p>
              <p><strong>计算方式：</strong></p>
              <ul class="example">
                <li>从<strong>上次加满</strong>到<strong>本次加满</strong>作为一个完整周期</li>
                <li><strong>累积加油量</strong> = 中间所有加油量 + 本次加油量</li>
                <li><strong>累积里程</strong> = 本次里程 - 上次加满时里程</li>
              </ul>
              <p><strong>举例：</strong></p>
              <div class="example-box">
                <p>📝 第1次加满：里程 1000km，加油 40L</p>
                <p>📝 第2次（未满）：里程 1200km，加油 30L</p>
                <p>📝 第3次加满：里程 1600km，加油 45L</p>
                <p class="result">📊 计算：</p>
                <p class="result">• 累积加油量 = 30L + 45L = 75L</p>
                <p class="result">• 累积里程 = 1600km - 1000km = 600km</p>
                <p class="result highlight">• 油耗 = 75 ÷ 600 × 100 = <strong>12.5L/100km</strong></p>
              </div>
            </div>
          </template>
        </van-cell>
      </van-cell-group>

      <div class="submit-section">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="submitting"
        >
          {{ isEdit ? '保存' : '添加' }}
        </van-button>
      </div>
    </van-form>

    <!-- 车辆选择弹窗 -->
    <van-popup v-model:show="showVehiclePicker" position="bottom">
      <van-picker
        :model-value="vehiclePickerValue"
        :columns="vehicleColumns"
        @confirm="onSelectVehicle"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        :model-value="currentDateValue"
        :min-date="new Date(2020, 0, 1)"
        :max-date="new Date()"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.record-form-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 80px;
}

.submit-section {
  padding: 16px;
}

.hint {
  font-size: 12px;
  color: #9ca3af;
}

.info-section {
  margin: 16px;
}

.info-icon {
  margin-right: 8px;
  color: #1989fa;
  font-size: 18px;
}

.calc-info {
  font-size: 13px;
  line-height: 1.6;
  color: #323233;
}

.calc-info p {
  margin: 8px 0;
}

.formula {
  background: #f0f9ff;
  padding: 8px 12px;
  border-radius: 6px;
  color: #1989fa;
  font-family: monospace;
  text-align: center;
  margin: 8px 0;
}

.example {
  margin: 8px 0;
  padding-left: 20px;
}

.example li {
  margin: 4px 0;
}

.example-box {
  background: #fafafa;
  padding: 12px;
  border-radius: 8px;
  margin-top: 8px;
}

.example-box p {
  margin: 6px 0;
  font-size: 12px;
}

.result {
  padding-left: 16px;
  color: #646566;
}

.result.highlight {
  color: #1989fa;
  font-weight: bold;
  font-size: 14px;
  margin-top: 8px;
}
</style>
