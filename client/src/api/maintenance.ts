import api from './index'

export interface MaintenanceRecord {
  id: number
  vehicle_id: number
  type: string
  date: string
  odometer: number
  cost?: number
  description?: string
  next_maintenance_odometer?: number
  next_maintenance_date?: string
  is_completed: boolean
  created_at: string
}

export interface CreateMaintenanceRequest {
  vehicle_id: number
  type: string
  date: string
  odometer: number
  cost?: number
  description?: string
  next_maintenance_odometer?: number
  next_maintenance_date?: string
}

export interface UpdateMaintenanceRequest extends Partial<CreateMaintenanceRequest> {
  is_completed?: boolean
}

// 获取保养记录列表
export const getMaintenances = (vehicle_id?: number) => {
  return api.get<any, MaintenanceRecord[]>('/v1/maintenance', { params: { vehicle_id } })
}

// 获取即将到期的保养
export const getUpcomingMaintenances = (vehicle_id?: number) => {
  return api.get<any, MaintenanceRecord[]>('/v1/maintenance/upcoming', { params: { vehicle_id } })
}

// 创建保养记录
export const createMaintenance = (data: CreateMaintenanceRequest) => {
  return api.post<any, MaintenanceRecord>('/v1/maintenance', data)
}

// 更新保养记录
export const updateMaintenance = (id: number, data: UpdateMaintenanceRequest) => {
  return api.put<any, MaintenanceRecord>(`/v1/maintenance/${id}`, data)
}

// 删除保养记录
export const deleteMaintenance = (id: number) => {
  return api.delete(`/v1/maintenance/${id}`)
}
