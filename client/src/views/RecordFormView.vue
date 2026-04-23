<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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

const onDateConfirm = (val: any) => {
  formData.value.date = val.selectedValues.join('-')
  showDatePicker.value = false
}

onMounted(async () => {
  await vehiclesStore.fetchVehicles()

  if (vehiclesStore.currentVehicle) {
    formData.value.vehicle_id = vehiclesStore.currentVehicle.id
  }

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
  } finally {
    loading.value = false
  }
}

// 自动计算单价
const onCostChange = () => {
  if (formData.value.volume > 0) {
    formData.value.unit_price = formData.value.total_cost / formData.value.volume
  }
}

// 自动计算总金额
const onVolumeOrPriceChange = () => {
  formData.value.total_cost = formData.value.volume * formData.value.unit_price
}

const onSubmit = async () => {
  if (!formData.value.vehicle_id) {
    showToast({ message: '请选择车辆' })
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

const vehicleName = computed(() => {
  const vehicle = vehiclesStore.vehicles.find(v => v.id === formData.value.vehicle_id)
  return vehicle?.name || '选择车辆'
})
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
          :value="vehicleName"
          label="车辆"
          placeholder="请选择车辆"
          readonly
          is-link
          @click="showVehiclePicker = true"
        />

        <van-field
          :value="formData.date"
          label="日期"
          placeholder="请选择日期"
          readonly
          is-link
          @click="showDatePicker = true"
        />

        <van-field
          v-model.number="formData.odometer"
          type="number"
          label="当前里程"
          placeholder="请输入里程"
          :rules="[{ required: true, message: '请输入里程' }]"
        >
          <template #extra>
            <span v-if="!isEdit && lastOdometer > 0" class="hint">
              上次: {{ lastOdometer }}
            </span>
          </template>
        </van-field>

        <van-field
          v-model.number="formData.volume"
          type="number"
          label="加油量"
          placeholder="请输入加油量"
          suffix="L"
          :rules="[{ required: true, message: '请输入加油量' }]"
          @blur="onVolumeOrPriceChange"
        />

        <van-field
          v-model.number="formData.total_cost"
          type="number"
          label="总金额"
          placeholder="请输入总金额"
          suffix="元"
          :rules="[{ required: true, message: '请输入总金额' }]"
          @blur="onCostChange"
        />

        <van-field
          v-model.number="formData.unit_price"
          type="number"
          label="单价"
          placeholder="自动计算"
          suffix="元/L"
          @blur="onVolumeOrPriceChange"
        />

        <van-field name="full_tank" label="是否加满">
          <template #input>
            <van-switch v-model="formData.full_tank" />
          </template>
        </van-field>

        <van-field
          v-model="formData.gas_station"
          label="加油站"
          placeholder="请输入加油站名称"
        />

        <van-field
          v-model="formData.notes"
          type="textarea"
          label="备注"
          placeholder="请输入备注"
          rows="2"
          maxlength="200"
          show-word-limit
        />
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

    <van-popup v-model:show="showVehiclePicker" position="bottom">
      <van-picker
        :columns="vehiclesStore.activeVehicles.map(v => ({ text: v.name, value: v.id }))"
        @confirm="(val: any) => { formData.vehicle_id = val.value; showVehiclePicker = false }"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="currentDateValue"
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
</style>
