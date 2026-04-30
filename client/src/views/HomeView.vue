<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { useRecordsStore } from '@/stores/records'
import * as statsApi from '@/api/stats'
import { formatMoney, formatConsumption, formatOdometer } from '@/utils/format'
import StatsChart from '@/components/StatsChart.vue'
import { showToast } from 'vant'

const router = useRouter()
const vehiclesStore = useVehiclesStore()
const recordsStore = useRecordsStore()

const currentVehicle = computed(() => vehiclesStore.currentVehicle)
const recentRecords = computed(() => recordsStore.records.slice(0, 3))

const stats = ref({
  total_records: 0,
  total_cost: 0,
  total_distance: 0,
  avg_consumption: 0,
  latest_consumption: 0,
})

const trendData = ref<Array<{ date: string; consumption: number }>>([])
const loading = ref(false)
const isInitialized = ref(false)
const showVehiclePicker = ref(false)
const vehiclePickerValue = ref<number[]>([])

const vehicleColumns = computed(() => {
  return (vehiclesStore.vehicles || []).map(v => ({
    text: `${v.icon} ${v.name}`,
    value: v.id
  }))
})

// 静默刷新（不显示 loading）
const loadStatsSilent = async () => {
  if (!currentVehicle.value) return

  try {
    const [summary, trend] = await Promise.all([
      statsApi.getStatsSummary({ vehicle_id: currentVehicle.value.id }).catch(() => null),
      statsApi.getConsumptionTrend({ vehicle_id: currentVehicle.value.id, months: 6 }).catch(() => []),
    ])
    stats.value = summary || {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
    }
    trendData.value = trend || []

    await recordsStore.fetchRecords({
      vehicle_id: currentVehicle.value.id,
      page_size: 3,
    })
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadStats = async () => {
  if (!currentVehicle.value) return

  loading.value = true
  await loadStatsSilent()
  loading.value = false
}

onMounted(async () => {
  try {
    await vehiclesStore.fetchVehicles()
    if (currentVehicle.value) {
      vehiclePickerValue.value = [currentVehicle.value.id]
      await loadStats()
      isInitialized.value = true
    }
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

watch(() => currentVehicle.value?.id, (newId) => {
  if (newId && isInitialized.value) {
    vehiclePickerValue.value = [newId]
    loadStatsSilent() // 车辆切换时静默刷新
  }
})

const onSelectVehicle = ({ selectedValues }: any) => {
  vehiclesStore.setCurrentVehicle(selectedValues[0])
  vehiclePickerValue.value = selectedValues
  showVehiclePicker.value = false
}

const goToRecord = (id: number) => {
  router.push(`/records/${id}/edit`)
}

const addRecord = () => {
  router.push('/records/new')
}
</script>

<template>
  <div class="home-page">
    <!-- 头部车辆选择 -->
    <van-sticky>
      <van-nav-bar
        :title="`${currentVehicle?.icon || ''} ${currentVehicle?.name || '选择车辆'}`"
        @click-right="showVehiclePicker = true"
      >
        <template #right>
          <van-icon
            name="arrow-down"
            color="#1989fa"
          />
        </template>
      </van-nav-bar>
    </van-sticky>

    <!-- 无车辆时显示提示 -->
    <div
      v-if="!currentVehicle && !loading"
      class="empty-vehicle"
    >
      <div class="empty-icon">
        🚗
      </div>
      <p class="empty-title">
        还没有添加车辆
      </p>
      <p class="empty-desc">
        添加第一辆车开始记录油耗吧
      </p>
      <van-button
        type="primary"
        round
        size="small"
        @click="router.push('/vehicles')"
      >
        添加车辆
      </van-button>
    </div>

    <!-- 有车辆时显示内容 -->
    <template v-else>
      <!-- 统计卡片 -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              ⛽
            </div>
            <div class="stat-content">
              <div class="stat-value">
                {{ formatConsumption(stats.latest_consumption) }}
              </div>
              <div class="stat-label">
                本次油耗
              </div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              📊
            </div>
            <div class="stat-content">
              <div class="stat-value">
                {{ formatConsumption(stats.avg_consumption) }}
              </div>
              <div class="stat-label">
                平均油耗
              </div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              💰
            </div>
            <div class="stat-content">
              <div class="stat-value">
                {{ formatMoney(stats.total_cost) }}
              </div>
              <div class="stat-label">
                总花费
              </div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              📍
            </div>
            <div class="stat-content">
              <div class="stat-value">
                {{ formatOdometer(stats.total_distance) }}
              </div>
              <div class="stat-label">
                总里程
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 油耗趋势图 -->
      <div class="section-title">
        📈 油耗趋势
      </div>
      <div class="chart-card">
        <StatsChart
          v-if="trendData.length > 0"
          type="line"
          :data="trendData"
          :loading="loading"
        />
        <div
          v-else-if="!loading"
          class="chart-empty"
        >
          <van-empty
            description="暂无数据"
            image-size="60"
          />
        </div>
      </div>

      <!-- 最近记录 -->
      <div class="section-title">
        📝 最近记录
      </div>
      <div class="records-list">
        <div
          v-if="recentRecords.length === 0"
          class="empty-records"
        >
          <van-empty
            description="暂无记录"
            image-size="60"
          >
            <van-button
              round
              type="primary"
              size="small"
              @click="addRecord"
            >
              添加记录
            </van-button>
          </van-empty>
        </div>
        <div
          v-for="record in recentRecords"
          :key="record.id"
          class="record-card"
          @click="goToRecord(record.id)"
        >
          <div class="record-header">
            <span class="record-date">{{ record.date }}</span>
            <span
              v-if="record.fuel_consumption"
              class="record-consumption"
            >
              {{ formatConsumption(record.fuel_consumption) }}
            </span>
          </div>
          <div class="record-body">
            <div class="record-info">
              <div class="record-icon">
                ⛽
              </div>
              <div class="record-details">
                <div class="record-station">
                  {{ record.gas_station || '加油站' }}
                </div>
                <div class="record-odometer">
                  {{ record.odometer }} km
                </div>
              </div>
            </div>
            <div class="record-cost">
              <div class="cost-value">
                {{ formatMoney(record.total_cost) }}
              </div>
              <div class="cost-label">
                花费
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- FAB 添加按钮 -->
    <van-button
      v-if="currentVehicle"
      round
      icon="plus"
      class="fab-button"
      @click="addRecord"
    />

    <!-- 车辆选择弹窗 -->
    <van-popup
      v-model:show="showVehiclePicker"
      position="bottom"
      round
    >
      <van-picker
        :columns="vehicleColumns"
        :model-value="vehiclePickerValue"
        @confirm="onSelectVehicle"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 空状态 */
.empty-vehicle {
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

/* 统计区域 */
.stats-section {
  padding: 12px 12px 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1989fa;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-top: 2px;
}

/* 章节标题 */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
  padding: 4px 16px 8px;
}

/* 图表卡片 */
.chart-card {
  margin: 0 12px 16px;
  background: white;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-empty {
  padding: 20px 0;
}

/* 记录列表 */
.records-list {
  padding: 0 12px 16px;
}

.empty-records {
  background: white;
  border-radius: 12px;
  padding: 30px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.record-card {
  background: white;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.record-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-date {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.record-consumption {
  font-size: 13px;
  color: #1989fa;
  background: rgba(25, 137, 250, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.record-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.record-icon {
  font-size: 20px;
}

.record-details {
  min-width: 0;
}

.record-station {
  font-size: 13px;
  color: #323233;
}

.record-odometer {
  font-size: 12px;
  color: #969799;
  margin-top: 2px;
}

.record-cost {
  text-align: right;
}

.cost-value {
  font-size: 16px;
  font-weight: 600;
  color: #ee0a24;
}

.cost-label {
  font-size: 11px;
  color: #969799;
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
</style>
