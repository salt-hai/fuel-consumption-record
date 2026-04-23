<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatMoney, formatConsumption, formatOdometer } from '@/utils/format'
import * as statsApi from '@/api/stats'
import { showActionSheet, showToast } from 'vant'
import StatsChart from '@/components/StatsChart.vue'

const router = useRouter()
const vehiclesStore = useVehiclesStore()

const periodOptions = [
  { text: '近3月', value: '3month' },
  { text: '近6月', value: '6month' },
  { text: '近1年', value: 'year' },
  { text: '全部', value: 'all' },
]

const currentPeriod = ref('6month')

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
  try {
    await vehiclesStore.fetchVehicles()
    await loadStats()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

watch(() => vehiclesStore.currentVehicleId, () => {
  loadStats()
})

const loadStats = async () => {
  const vehicleId = vehiclesStore.currentVehicleId ?? undefined
  loading.value = true
  try {
    const [summaryData, monthlyData] = await Promise.all([
      statsApi.getStatsSummary({ vehicle_id: vehicleId }).catch(() => null),
      statsApi.getMonthlyStats({ vehicle_id: vehicleId }).catch(() => []),
    ])
    summary.value = summaryData || {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
    }
    monthlyStats.value = monthlyData || []
  } catch (error) {
    console.error('加载统计数据失败:', error)
    summary.value = {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
    }
    monthlyStats.value = []
  } finally {
    loading.value = false
  }
}

const onShowPeriodPicker = () => {
  showActionSheet({
    title: '选择时间范围',
    menu: [
      ...periodOptions.map(p => ({
        text: p.text,
        onClick: () => {
          currentPeriod.value = p.value
        }
      })),
      { text: '取消', theme: 'cancel' }
    ]
  })
}

const onShowVehiclePicker = () => {
  const vehicles = vehiclesStore.activeVehicles
  if (vehicles.length === 0) {
    showToast('暂无车辆，请先添加车辆')
    router.push('/vehicles')
    return
  }

  showActionSheet({
    title: '选择车辆',
    menu: [
      ...vehicles.map(v => ({
        text: v.name,
        onClick: () => {
          vehiclesStore.setCurrentVehicle(v.id)
          loadStats()
        }
      })),
      { text: '取消', theme: 'cancel' }
    ]
  })
}

const currentPeriodText = computed(() => {
  return periodOptions.find(p => p.value === currentPeriod.value)?.text || '选择时间'
})

const currentVehicleName = computed(() => {
  return vehiclesStore.currentVehicle?.name || '选择车辆'
})
</script>

<template>
  <div class="stats-container">
    <van-nav-bar title="统计分析">
      <template #right>
        <van-dropdown-menu>
          <van-dropdown-item :model-value="currentPeriodText" @click="onShowPeriodPicker" />
        </van-dropdown-menu>
      </template>
    </van-nav-bar>

    <!-- 车辆和时间选择 -->
    <van-cell-group inset>
      <van-cell :title="currentVehicleName" is-link @click="onShowVehiclePicker" />
      <van-cell :title="currentPeriodText" is-link @click="onShowPeriodPicker" />
    </van-cell-group>

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
