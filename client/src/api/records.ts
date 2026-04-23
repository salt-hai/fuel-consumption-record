import api from './index'

export interface FuelRecord {
  id: number
  vehicle_id: number
  date: string
  odometer: number
  volume: number
  total_cost: number
  unit_price?: number
  full_tank: boolean
  gas_station?: string
  notes?: string
  fuel_consumption?: number  // L/100km
  created_at: string
}

export interface CreateRecordRequest {
  vehicle_id: number
  date: string
  odometer: number
  volume: number
  total_cost: number
  full_tank?: boolean
  gas_station?: string
  notes?: string
}

export interface UpdateRecordRequest extends Partial<CreateRecordRequest> {}

export interface RecordListResponse {
  items: FuelRecord[]
  total: number
  page: number
  page_size: number
}

export interface RecordListParams {
  vehicle_id?: number
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
}

// 获取加油记录列表
export const getRecords = (params: RecordListParams) => {
  return api.get<RecordListResponse>('/v1/records/', { params })
}

// 获取单条记录详情
export const getRecord = (id: number) => {
  return api.get<FuelRecord>(`/v1/records/${id}/`)
}

// 创建加油记录
export const createRecord = (data: CreateRecordRequest) => {
  return api.post<FuelRecord>('/v1/records/', data)
}

// 更新加油记录
export const updateRecord = (id: number, data: UpdateRecordRequest) => {
  return api.put<FuelRecord>(`/v1/records/${id}/`, data)
}

// 删除加油记录
export const deleteRecord = (id: number) => {
  return api.delete(`/v1/records/${id}/`)
}
