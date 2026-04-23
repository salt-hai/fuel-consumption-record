<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatMoney, formatConsumption, formatOdometer } from '@/utils/format'
import * as statsApi from '@/api/stats'
import StatsChart from '@/components/StatsChart.vue'

const vehiclesStore = useVehiclesStore()

const period = ref('6month')
const periods = [
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
})

const monthlyStats = ref<Array<{
  month: string
  cost: number
  volume: number
  distance: number
  consumption: number
}>>([])

const loading = ref(false)

onMounted(async () => {
  await vehiclesStore.fetchVehicles()
  await loadStats()
})

watch(() => vehiclesStore.currentVehicleId, () => {
  loadStats()
})

const loadStats = async () => {
  const vehicleId = vehiclesStore.currentVehicleId ?? undefined
  loading.value = true
  try {
    const [summaryData, monthlyData] = await Promise.all([
      statsApi.getStatsSummary({ vehicle_id: vehicleId }),
      statsApi.getMonthlyStats({ vehicle_id: vehicleId }),
    ])
    summary.value = summaryData
    monthlyStats.value = monthlyData
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="stats-container">
    <van-nav-bar title="统计分析">
      <template #right>
        <van-dropdown-menu>
          <van-dropdown-item v-model="period" :options="periods" @change="loadStats" />
        </van-dropdown-menu>
      </template>
    </van-nav-bar>

    <!-- 汇总卡片 -->
    <van-cell-group inset title="数据汇总">
      <van-cell title="总记录数" :value="`${summary.total_records} 条`" />
      <van-cell title="总花费" :value="formatMoney(summary.total_cost)" />
      <van-cell title="总里程" :value="formatOdometer(summary.total_distance)" />
      <van-cell title="平均油耗" :value="formatConsumption(summary.avg_consumption)" />
      <van-cell title="最新油耗" :value="formatConsumption(summary.latest_consumption)" />
    </van-cell-group>

    <!-- 月度花费图表 -->
    <van-cell-group inset title="月度花费">
      <div class="chart-container">
        <StatsChart
          v-if="monthlyStats.length > 0"
          type="bar"
          :data="monthlyStats"
          :loading="loading"
        />
        <van-empty v-else-if="!loading" description="暂无数据" image-size="80" />
      </div>
    </van-cell-group>

    <!-- 油耗趋势图表 -->
    <van-cell-group inset title="油耗趋势">
      <div class="chart-container">
        <StatsChart
          v-if="monthlyStats.length > 0"
          type="line"
          :data="monthlyStats.map(s => ({ date: s.month, consumption: s.consumption }))"
          :loading="loading"
        />
        <van-empty v-else-if="!loading" description="暂无数据" image-size="80" />
      </div>
    </van-cell-group>

    <!-- 月度统计表格 -->
    <van-cell-group inset title="月度详情">
      <div v-if="monthlyStats.length === 0" class="empty-state">
        <van-empty description="暂无数据" />
      </div>
      <div v-else class="table-container">
        <table class="stats-table">
          <thead>
            <tr>
              <th>月份</th>
              <th>花费</th>
              <th>油耗</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stat in monthlyStats" :key="stat.month">
              <td>{{ stat.month }}</td>
              <td>{{ formatMoney(stat.cost) }}</td>
              <td>{{ formatConsumption(stat.consumption) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </van-cell-group>
  </div>
</template>

<style scoped>
.stats-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.chart-container {
  height: 220px;
  padding: 16px;
}

.empty-state {
  padding: 32px 0;
}

.table-container {
  padding: 0 16px 16px 16px;
}

.stats-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.stats-table th,
.stats-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.stats-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.stats-table td {
  color: #6b7280;
  font-size: 14px;
}

.stats-table tr:last-child td {
  border-bottom: none;
}
</style>
