<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useVehiclesStore } from '@/stores/vehicles'
import { formatMoney, formatConsumption, formatDate } from '@/utils/format'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const recordsStore = useRecordsStore()
const vehiclesStore = useVehiclesStore()

const loading = ref(false)
const finished = ref(false)

const records = computed(() => recordsStore.records)

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
  <div class="record-list-container">
    <van-nav-bar title="加油记录" />

    <van-pull-refresh v-model="loading" @refresh="onRefresh">
      <div v-if="records.length === 0" class="empty-state">
        <van-empty description="暂无记录">
          <van-button type="primary" size="small" @click="onAdd">
            添加第一条记录
          </van-button>
        </van-empty>
      </div>

      <div v-else>
        <van-swipe-cell
          v-for="record in records"
          :key="record.id"
        >
          <van-cell
            :title="record.gas_station || '加油站'"
            :label="`${record.date} · ${record.volume}L`"
            is-link
            @click="onEdit(record.id)"
          >
            <template #value>
              <div class="record-info">
                <div class="cost">{{ formatMoney(record.total_cost) }}</div>
                <div v-if="record.fuel_consumption" class="consumption">
                  {{ formatConsumption(record.fuel_consumption) }}
                </div>
              </div>
            </template>
          </van-cell>
          <template #right>
            <van-button
              square
              type="danger"
              text="删除"
              style="height: 100%"
              @click="onDelete(record.id)"
            />
          </template>
        </van-swipe-cell>
      </div>
    </van-pull-refresh>

    <van-floating-bubble
      axis="xy"
      icon="plus"
      magnetic="x"
      @click="onAdd"
    />
  </div>
</template>

<style scoped>
.record-list-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.empty-state {
  padding: 60px 20px;
}

.record-info {
  text-align: right;
}

.cost {
  font-weight: bold;
  color: #1f2937;
}

.consumption {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}
</style>
