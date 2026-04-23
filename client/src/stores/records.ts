import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as recordsApi from '@/api/records'
import type { FuelRecord, CreateRecordRequest, UpdateRecordRequest, RecordListParams } from '@/api/records'

export const useRecordsStore = defineStore('records', () => {
  const records = ref<FuelRecord[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)

  // 获取记录列表
  const fetchRecords = async (params?: RecordListParams) => {
    loading.value = true
    try {
      const res = await recordsApi.getRecords({
        page: page.value,
        page_size: pageSize.value,
        ...params,
      })
      records.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  // 获取单条记录
  const fetchRecord = async (id: number) => {
    return await recordsApi.getRecord(id)
  }

  // 创建记录
  const createRecord = async (data: CreateRecordRequest) => {
    const record = await recordsApi.createRecord(data)
    records.value.unshift(record)
    total.value += 1
    return record
  }

  // 更新记录
  const updateRecord = async (id: number, data: UpdateRecordRequest) => {
    const record = await recordsApi.updateRecord(id, data)
    const index = records.value.findIndex((r) => r.id === id)
    if (index !== -1) {
      records.value[index] = record
    }
    return record
  }

  // 删除记录
  const deleteRecord = async (id: number) => {
    await recordsApi.deleteRecord(id)
    records.value = records.value.filter((r) => r.id !== id)
    total.value -= 1
  }

  // 分页参数变更
  const setPage = (newPage: number) => {
    page.value = newPage
  }

  const setPageSize = (newPageSize: number) => {
    pageSize.value = newPageSize
    page.value = 1
  }

  return {
    records,
    total,
    page,
    pageSize,
    loading,
    fetchRecords,
    fetchRecord,
    createRecord,
    updateRecord,
    deleteRecord,
    setPage,
    setPageSize,
  }
})
