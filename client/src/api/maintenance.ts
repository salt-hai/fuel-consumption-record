import api from './index'

export interface MaintenanceRecord {
  id: number
  vehicle_id: number
  maintenance_type: string
  type?: string  // 别名，用于显示
  date: string
  odometer: number
  cost: number
  notes?: string
  description?: string  // 别名，用于显示
  next_maintenance_odometer?: number
  next_maintenance_date?: string
  created_at: string
}

export interface CreateMaintenanceRequest {
  vehicle_id: number
  maintenance_type: string
  type?: string
  date: string
  odometer: number
  cost: number
  notes?: string
  description?: string
  next_maintenance_odometer?: number
  next_maintenance_date?: string
}

export interface UpdateMaintenanceRequest extends Partial<CreateMaintenanceRequest> {}

// 获取保养记录列表
export const getMaintenanceRecords = (vehicle_id?: number) => {
  return api.get<MaintenanceRecord[]>('/v1/maintenance/', { params: { vehicle_id } })
}

// 别名，兼容旧代码
export const getMaintenances = getMaintenanceRecords

// 获取即将到期的保养
export const getUpcomingMaintenance = (vehicle_id?: number) => {
  return api.get<MaintenanceRecord[]>('/v1/maintenance/upcoming', { params: { vehicle_id } })
}

// 别名，兼容旧代码
export const getUpcomingMaintenances = getUpcomingMaintenance

// 创建保养记录
export const createMaintenanceRecord = (data: CreateMaintenanceRequest) => {
  return api.post<MaintenanceRecord>('/v1/maintenance/', data)
}

// 别名，兼容旧代码
export const createMaintenance = createMaintenanceRecord

// 更新保养记录
export const updateMaintenanceRecord = (id: number, data: UpdateMaintenanceRequest) => {
  return api.put<MaintenanceRecord>(`/v1/maintenance/${id}`, data)
}

// 别名，兼容旧代码
export const updateMaintenance = updateMaintenanceRecord

// 删除保养记录
export const deleteMaintenanceRecord = (id: number) => {
  return api.delete(`/v1/maintenance/${id}`)
}

// 别名，兼容旧代码
export const deleteMaintenance = deleteMaintenanceRecord
