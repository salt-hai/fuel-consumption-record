import api from './index'

export interface MaintenanceRecord {
  id: number
  vehicle_id: number
  maintenance_type: string
  date: string
  odometer: number
  cost: number
  notes?: string
  created_at: string
}

export interface CreateMaintenanceRequest {
  vehicle_id: number
  maintenance_type: string
  date: string
  odometer: number
  cost: number
  notes?: string
}

export interface UpdateMaintenanceRequest extends Partial<CreateMaintenanceRequest> {}

// 获取保养记录列表
export const getMaintenanceRecords = (vehicle_id: number) => {
  return api.get<MaintenanceRecord[]>('/v1/maintenance/', { params: { vehicle_id } })
}

// 获取即将到期的保养
export const getUpcomingMaintenance = (vehicle_id: number) => {
  return api.get<MaintenanceRecord[]>('/v1/maintenance/upcoming', { params: { vehicle_id } })
}

// 创建保养记录
export const createMaintenanceRecord = (data: CreateMaintenanceRequest) => {
  return api.post<MaintenanceRecord>('/v1/maintenance/', data)
}

// 更新保养记录
export const updateMaintenanceRecord = (id: number, data: UpdateMaintenanceRequest) => {
  return api.put<MaintenanceRecord>(`/v1/maintenance/${id}`, data)
}

// 删除保养记录
export const deleteMaintenanceRecord = (id: number) => {
  return api.delete(`/v1/maintenance/${id}`)
}
