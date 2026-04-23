import api from './index'

export interface Vehicle {
  id: number
  name: string
  brand?: string
  model?: string
  plate_number?: string
  initial_odometer: number
  fuel_type: string
  is_active: boolean
  created_at: string
}

export interface CreateVehicleRequest {
  name: string
  brand?: string
  model?: string
  plate_number?: string
  initial_odometer?: number
  fuel_type?: string
}

export interface UpdateVehicleRequest extends Partial<CreateVehicleRequest> {
  is_active?: boolean
}

// 获取车辆列表
export const getVehicles = () => {
  return api.get<Vehicle[]>('/v1/vehicles/')
}

// 创建车辆
export const createVehicle = (data: CreateVehicleRequest) => {
  return api.post<Vehicle>('/v1/vehicles/', data)
}

// 更新车辆
export const updateVehicle = (id: number, data: UpdateVehicleRequest) => {
  return api.put<Vehicle>(`/v1/vehicles/${id}/`, data)
}

// 删除车辆
export const deleteVehicle = (id: number) => {
  return api.delete(`/v1/vehicles/${id}/`)
}
