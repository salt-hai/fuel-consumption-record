<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useVehiclesStore } from '@/stores/vehicles'
import { useRecordsStore } from '@/stores/records'
import * as statsApi from '@/api/stats'
import { formatMoney, formatConsumption, formatOdometer } from '@/utils/format'
import StatsChart from '@/components/StatsChart.vue'

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
const showVehiclePicker = ref(false)

const loadStats = async () => {
  if (!currentVehicle.value) return

  loading.value = true
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

    // 同时获取最近记录
    await recordsStore.fetchRecords({
      vehicle_id: currentVehicle.value.id,
      page_size: 3,
    })
  } catch (error) {
    console.error('加载统计数据失败:', error)
    stats.value = {
      total_records: 0,
      total_cost: 0,
      total_distance: 0,
      avg_consumption: 0,
      latest_consumption: 0,
    }
    trendData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    await vehiclesStore.fetchVehicles()
    if (currentVehicle.value) {
      await loadStats()
    }
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

watch(() => currentVehicle.value?.id, () => {
  loadStats()
})

const onVehicleChange = async (val: any) => {
  vehiclesStore.setCurrentVehicle(val.value)
  showVehiclePicker.value = false
}
</script>

<template>
  <div class="home-container">
    <!-- 头部车辆选择 -->
    <van-sticky>
      <van-nav-bar
        :title="currentVehicle?.name || '选择车辆'"
        @click-right="showVehiclePicker = true"
      >
        <template #right>
          <van-icon name="arrow-down" />
        </template>
      </van-nav-bar>
    </van-sticky>

    <!-- 无车辆时显示提示 -->
    <div v-if="!currentVehicle && !loading" class="empty-vehicle">
      <van-empty description="还没有添加车辆">
        <van-button type="primary" size="small" @click="router.push('/vehicles')">
          添加车辆
        </van-button>
      </van-empty>
    </div>

    <!-- 有车辆时显示内容 -->
    <template v-else>
    <div class="stats-cards">
      <van-grid :column-num="2" :border="false">
        <van-grid-item>
          <div class="stat-card">
            <div class="stat-value">{{ formatConsumption(stats.latest_consumption) }}</div>
            <div class="stat-label">本次油耗</div>
          </div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-card">
            <div class="stat-value">{{ formatConsumption(stats.avg_consumption) }}</div>
            <div class="stat-label">平均油耗</div>
          </div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-card">
            <div class="stat-value">{{ formatMoney(stats.total_cost) }}</div>
            <div class="stat-label">总花费</div>
          </div>
        </van-grid-item>
        <van-grid-item>
          <div class="stat-card">
            <div class="stat-value">{{ formatOdometer(stats.total_distance) }}</div>
            <div class="stat-label">总里程</div>
          </div>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- 油耗趋势图 -->
    <van-cell-group title="油耗趋势" inset>
      <div class="chart-container">
        <StatsChart
          v-if="trendData.length > 0"
          type="line"
          :data="trendData"
          :loading="loading"
        />
        <van-empty v-else-if="!loading" description="暂无数据" image-size="80" />
      </div>
    </van-cell-group>

    <!-- 最近记录 -->
    <van-cell-group title="最近记录" inset>
      <div v-if="recentRecords.length === 0" class="empty-state">
        <van-empty description="暂无记录" />
      </div>
      <van-cell
        v-for="record in recentRecords"
        :key="record.id"
        :title="record.gas_station || '加油站'"
        :label="record.date"
        is-link
        :to="`/records/${record.id}/edit`"
      >
        <template #value>
          <div class="record-value">
            <div>{{ formatMoney(record.total_cost) }}</div>
            <div v-if="record.fuel_consumption" class="consumption">
              {{ formatConsumption(record.fuel_consumption) }}
            </div>
          </div>
        </template>
      </van-cell>
    </van-cell-group>

    <!-- 车辆选择弹窗 -->
    <van-popup v-model:show="showVehiclePicker" position="bottom">
      <van-picker
        :columns="vehiclesStore.activeVehicles.map(v => ({ text: v.name, value: v.id }))"
        @confirm="onVehicleChange"
        @cancel="showVehiclePicker = false"
      />
    </van-popup>
    </template>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.stats-cards {
  padding: 16px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #4f46e5;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.chart-container {
  height: 200px;
  padding: 16px;
}

.record-value {
  text-align: right;
}

.consumption {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.empty-state {
  padding: 32px 0;
}

.empty-vehicle {
  padding: 60px 20px;
}
</style>
