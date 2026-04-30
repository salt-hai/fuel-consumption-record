<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatMoney, formatConsumption, formatOdometer } from '@/utils/format'
import * as statsApi from '@/api/stats'
import { showToast } from 'vant'
import StatsChart from '@/components/StatsChart.vue'

const router = useRouter()
const vehiclesStore = useVehiclesStore()

const periodValue = ref('6month')
const periodOptions = [
  { text: '近3月', value: '3month' },
  { text: '近6月', value: '6month' },
  { text: '近1年', value: 'year' },
  { text: '全部', value: 'all' },
]

const summary = ref({
  total_records: 0,
  total_cost: 0,
  total_distance: 0,
  avg_consumption: 0,
  latest_consumption: 0,
  avg_cost_per_km: 0,
})

const monthlyStats = ref<Array<{
  month: string
  cost: number
  volume: number
  distance: number
  consumption: number
}>>([])

const trendStats = ref<Array<{
  date: string
  consumption: number
}>>([])

const loading = ref(false)
const isInitialized = ref(false)
const showVehiclePicker = ref(false)
const showPeriodPicker = ref(false)
const vehiclePickerValue = ref<number[]>([])

const currentPeriodText = computed(() => {
  return periodOptions.find(p => p.value === periodValue.value)?.text || '选择时间'
})

const currentVehicleName = computed(() => {
  const vehicle = vehiclesStore.currentVehicle
  return vehicle ? `${vehicle.icon} ${vehicle.name}` : '选择车辆'
})

const vehicleColumns = computed(() => {
  return (vehiclesStore.vehicles || []).map(v => ({
    text: `${v.icon} ${v.name}`,
    value: v.id
  }))
})

// 根据时间范围筛选月数
const getMonthsCount = (period: string): number | undefined => {
  switch (period) {
    case '3month': return 3
    case '6month': return 6
    case 'year': return 12
    case 'all': return undefined
    default: return undefined
  }
}

// 根据时间范围筛选月度数据
const filterMonthlyData = (data: typeof monthlyStats.value, period: string): typeof monthlyStats.value => {
  if (period === 'all') return data
  const months = getMonthsCount(period)
  if (months === undefined) return data
  return data.slice(0, months)
}

// 静默刷新（不显示 loading）
const loadStatsSilent = async () => {
  const vehicleId = vehiclesStore.currentVehicleId ?? undefined
  try {
    const [summaryData, monthlyData, trendData] = await Promise.all([
      statsApi.getStatsSummary({ vehicle_id: vehicleId }).catch(() => null),
      statsApi.getMonthlyStats({ vehicle_id: vehicleId }).catch(() => []),
      statsApi.getConsumptionTrend({ vehicle_id: vehicleId, months: getMonthsCount(periodValue.value) }).catch(() => []),
    ])
    summary.value = summaryData || {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
      avg_cost_per_km: 0,
    }
    monthlyStats.value = filterMonthlyData(monthlyData || [], periodValue.value)
    trendStats.value = trendData || []
  } catch (error) {
    console.error('加载统计数据失败:', error)
    summary.value = {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
      avg_cost_per_km: 0,
    }
    monthlyStats.value = []
    trendStats.value = []
  }
}

const loadStats = async () => {
  loading.value = true
  await loadStatsSilent()
  loading.value = false
}

onMounted(async () => {
  try {
    await vehiclesStore.fetchVehicles()
    if (vehiclesStore.currentVehicle) {
      vehiclePickerValue.value = [vehiclesStore.currentVehicle.id]
    }
    await loadStats()
    isInitialized.value = true
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

watch(() => vehiclesStore.currentVehicleId, (newId) => {
  if (newId && isInitialized.value) {
    vehiclePickerValue.value = [newId]
    loadStatsSilent() // 车辆切换时静默刷新
  }
})

const onSelectVehicle = ({ selectedValues }: any) => {
  vehiclesStore.setCurrentVehicle(selectedValues[0])
  vehiclePickerValue.value = selectedValues
  showVehiclePicker.value = false
  loadStats()
}

const onSelectPeriod = ({ selectedValues }: any) => {
  periodValue.value = selectedValues[0]
  showPeriodPicker.value = false
  loadStats()
}
</script>

<template>
  <div class="stats-page">
    <van-nav-bar title="统计分析" />

    <!-- 车辆和时间选择 -->
    <div class="filter-section">
      <div class="filter-card">
        <div
          class="filter-item"
          @click="showVehiclePicker = true"
        >
          <span class="filter-label">车辆</span>
          <span class="filter-value">{{ currentVehicleName }}</span>
          <van-icon name="arrow-down" />
        </div>
        <div class="filter-divider" />
        <div
          class="filter-item"
          @click="showPeriodPicker = true"
        >
          <span class="filter-label">时间范围</span>
          <span class="filter-value">{{ currentPeriodText }}</span>
          <van-icon name="arrow-down" />
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="section-title">
      📊 数据汇总
    </div>
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">
            📝
          </div>
          <div class="stat-content">
            <div class="stat-value">
              {{ summary.total_records }}
            </div>
            <div class="stat-label">
              总记录数
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            💰
          </div>
          <div class="stat-content">
            <div class="stat-value">
              {{ formatMoney(summary.total_cost) }}
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
              {{ formatOdometer(summary.total_distance) }}
            </div>
            <div class="stat-label">
              总里程
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            ⛽
          </div>
          <div class="stat-content">
            <div class="stat-value">
              {{ formatConsumption(summary.avg_consumption) }}
            </div>
            <div class="stat-label">
              平均油耗
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            📈
          </div>
          <div class="stat-content">
            <div class="stat-value">
              {{ formatConsumption(summary.latest_consumption) }}
            </div>
            <div class="stat-label">
              最新油耗
            </div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            💵
          </div>
          <div class="stat-content">
            <div class="stat-value">
              ¥{{ summary.avg_cost_per_km }}
            </div>
            <div class="stat-label">
              平均油费
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 月度花费图表 -->
    <div class="section-title">
      💵 月度花费
    </div>
    <div class="chart-card">
      <StatsChart
        v-if="monthlyStats.length > 0"
        type="bar"
        :data="monthlyStats"
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

    <!-- 油耗趋势图表 -->
    <div class="section-title">
      📈 油耗趋势
    </div>
    <div class="chart-card">
      <StatsChart
        v-if="trendStats.length > 0"
        type="line"
        :data="trendStats"
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

    <!-- 月度统计表格 -->
    <div class="section-title">
      📅 月度详情
    </div>
    <div class="table-card">
      <div
        v-if="monthlyStats.length === 0"
        class="table-empty"
      >
        <van-empty
          description="暂无数据"
          image-size="60"
        />
      </div>
      <table
        v-else
        class="stats-table"
      >
        <thead>
          <tr>
            <th>月份</th>
            <th>花费</th>
            <th>油耗</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="stat in monthlyStats"
            :key="stat.month"
          >
            <td>{{ stat.month }}</td>
            <td>{{ formatMoney(stat.cost) }}</td>
            <td>{{ formatConsumption(stat.consumption) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

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

    <!-- 时间选择弹窗 -->
    <van-popup
      v-model:show="showPeriodPicker"
      position="bottom"
      round
    >
      <van-picker
        :columns="periodOptions"
        @confirm="onSelectPeriod"
        @cancel="showPeriodPicker = false"
      />
    </van-popup>
  </div>
</template>

<style scoped>
.stats-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 筛选区域 */
.filter-section {
  padding: 12px;
}

.filter-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  overflow: hidden;
}

.filter-item {
  flex: 1;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.filter-item:active {
  background: #f5f6f7;
}

.filter-label {
  font-size: 11px;
  color: #969799;
}

.filter-value {
  font-size: 14px;
  color: #323233;
  font-weight: 500;
}

.filter-divider {
  width: 1px;
  background: #ebedf0;
  margin: 12px 0;
}

/* 章节标题 */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
  padding: 4px 16px 8px;
}

/* 统计卡片 */
.stats-section {
  padding: 0 12px 16px;
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
  word-break: break-all;
}

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-top: 2px;
}

/* 图表卡片 */
.chart-card {
  margin: 0 12px 16px;
  background: white;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  min-height: 220px;
}

.chart-empty {
  padding: 40px 0;
}

/* 表格卡片 */
.table-card {
  margin: 0 12px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.table-empty {
  padding: 40px 0;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
}

.stats-table th,
.stats-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #f5f6f7;
}

.stats-table th {
  background: #fafafa;
  font-weight: 600;
  color: #323233;
  font-size: 13px;
}

.stats-table td {
  color: #646566;
  font-size: 14px;
}

.stats-table tr:last-child td {
  border-bottom: none;
}

.stats-table tr:active {
  background: #f5f6f7;
}
</style>
