<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatMoney, formatConsumption } from '@/utils/format'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const recordsStore = useRecordsStore()
const vehiclesStore = useVehiclesStore()

const loading = ref(false)
const finished = ref(false)

const records = computed(() => recordsStore.records)

// 计算里程增量
const getOdometerDelta = (index: number) => {
  if (index >= records.value.length - 1) return 0
  const current = records.value[index]
  const previous = records.value[index + 1]
  return current.odometer - previous.odometer
}

// 获取油耗颜色等级
const getConsumptionLevel = (consumption: number) => {
  if (consumption < 7) return 'low'
  if (consumption < 10) return 'medium'
  return 'high'
}

onMounted(async () => {
  await onRefresh()
})

const onRefresh = async () => {
  loading.value = true
  finished.value = false
  try {
    await recordsStore.fetchRecords({
      vehicle_id: vehiclesStore.currentVehicleId ?? undefined,
    })
  } catch (error) {
    console.error('获取记录失败:', error)
    showToast({ message: '获取记录失败', type: 'fail' })
  } finally {
    loading.value = false
  }
}

const onDelete = async (id: number) => {
  await showConfirmDialog({
    title: '确认删除',
    message: '确定要删除这条记录吗？',
  })
  await recordsStore.deleteRecord(id)
  showToast('已删除')
}

const onAdd = () => {
  router.push('/records/new')
}

const onEdit = (id: number) => {
  router.push(`/records/${id}/edit`)
}
</script>

<template>
  <div class="records-page">
    <van-nav-bar title="加油记录" />

    <van-pull-refresh v-model="loading" @refresh="onRefresh">
      <!-- 空状态 -->
      <div v-if="records.length === 0" class="empty-state">
        <div class="empty-icon">⛽</div>
        <p class="empty-title">还没有加油记录</p>
        <p class="empty-desc">添加第一条记录开始追踪油耗吧</p>
        <van-button type="primary" round size="small" @click="onAdd">
          添加记录
        </van-button>
      </div>

      <!-- 记录列表 -->
      <div v-else class="records-list">
        <van-swipe-cell
          v-for="(record, index) in records"
          :key="record.id"
        >
          <div
            class="record-card"
            :class="`consumption-${record.fuel_consumption ? getConsumptionLevel(record.fuel_consumption) : 'medium'}`"
            @click="onEdit(record.id)"
          >
            <div class="record-header">
              <span class="record-date">{{ record.date }}</span>
              <span v-if="record.fuel_consumption" class="record-consumption" :class="`consumption-${getConsumptionLevel(record.fuel_consumption)}`">
                {{ formatConsumption(record.fuel_consumption) }}
              </span>
            </div>

            <div class="record-station">
              <span class="station-icon">⛽</span>
              <span class="station-name">{{ record.gas_station || '加油站' }}</span>
              <van-tag v-if="record.full_tank" type="success" round size="small">
                <van-icon name="passed" />
                已加满
              </van-tag>
            </div>

            <div class="record-details">
              <div class="detail-item">
                <span class="detail-icon">📍</span>
                <span class="detail-value">{{ record.odometer.toLocaleString() }} km</span>
                <span v-if="getOdometerDelta(index) > 0" class="detail-delta">
                  +{{ getOdometerDelta(index) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="detail-icon">⛽</span>
                <span class="detail-value">{{ record.volume }} L</span>
                <span v-if="record.unit_price" class="detail-price">
                  ¥{{ record.unit_price }}/L
                </span>
              </div>
            </div>

            <div class="record-footer">
              <div class="cost-section">
                <span class="cost-label">花费</span>
                <span class="cost-value">{{ formatMoney(record.total_cost) }}</span>
              </div>
              <van-icon name="arrow" class="arrow-icon" />
            </div>
          </div>

          <template #right>
            <van-button
              square
              type="danger"
              text="删除"
              class="delete-button"
              @click="onDelete(record.id)"
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
  </div>
</template>

<style scoped>
.records-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px;
}

/* 空状态 */
.empty-state {
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

/* 记录列表 */
.records-list {
  padding: 12px;
}

.record-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
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

.record-card.consumption-low::before {
  background: linear-gradient(180deg, #07c160 0%, #95de64 100%);
}

.record-card.consumption-medium::before {
  background: linear-gradient(180deg, #1989fa 0%, #40a9ff 100%);
}

.record-card.consumption-high::before {
  background: linear-gradient(180deg, #ee0a24 0%, #ff6060 100%);
}

.record-card:active {
  transform: scale(0.98);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

/* 记录头部 */
.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-date {
  font-size: 15px;
  font-weight: 600;
  color: #323233;
}

.record-consumption {
  font-size: 13px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.record-consumption.consumption-low {
  background: rgba(7, 193, 96, 0.1);
  color: #07c160;
}

.record-consumption.consumption-medium {
  background: rgba(25, 137, 250, 0.1);
  color: #1989fa;
}

.record-consumption.consumption-high {
  background: rgba(238, 10, 36, 0.1);
  color: #ee0a24;
}

/* 加油站信息 */
.record-station {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.station-icon {
  font-size: 16px;
}

.station-name {
  font-size: 14px;
  color: #323233;
  flex: 1;
}

/* 详细信息 */
.record-details {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #646566;
}

.detail-icon {
  font-size: 14px;
}

.detail-value {
  color: #323233;
  font-weight: 500;
}

.detail-delta {
  color: #07c160;
  font-size: 12px;
  font-weight: 500;
}

.detail-price {
  color: #969799;
  font-size: 12px;
}

/* 底部信息 */
.record-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #f5f6f7;
}

.cost-section {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.cost-label {
  font-size: 12px;
  color: #969799;
}

.cost-value {
  font-size: 18px;
  font-weight: 600;
  color: #ee0a24;
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
  box-shadow: 0 2px 10px rgba(25, 137, 250, 0.4);
}
</style>
