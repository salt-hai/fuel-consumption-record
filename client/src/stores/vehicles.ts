import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as vehiclesApi from '@/api/vehicles'
import type { Vehicle, CreateVehicleRequest, UpdateVehicleRequest } from '@/api/vehicles'

export const useVehiclesStore = defineStore('vehicles', () => {
  const vehicles = ref<Vehicle[]>([])
  const currentVehicleId = ref<number | null>(
    parseInt(localStorage.getItem('current_vehicle_id') || '0') || null
  )
  const loading = ref(false)

  const currentVehicle = computed(() => {
    const vehiclesList = vehicles.value || []
    if (!currentVehicleId.value) return vehiclesList[0] || null

    // 如果当前选中的车辆不存在于列表中，返回第一个车辆
    const vehicle = vehiclesList.find((v) => v.id === currentVehicleId.value)
    if (!vehicle && vehiclesList.length > 0) {
      return vehiclesList[0]
    }
    return vehicle || null
  })

  const activeVehicles = computed(() =>
    (vehicles.value || []).filter((v) => v.is_active)
  )

  // 获取车辆列表
  const fetchVehicles = async () => {
    loading.value = true
    try {
      const result = await vehiclesApi.getVehicles()
      // 确保 result 是数组
      vehicles.value = Array.isArray(result) ? result : []
    } catch (error) {
      console.error('获取车辆列表失败:', error)
      vehicles.value = []
    } finally {
      loading.value = false
      // 确保 vehicles.value 是数组
      if (!Array.isArray(vehicles.value)) {
        vehicles.value = []
      }

      // 验证当前选中车辆是否有效
      const isValidVehicle = currentVehicleId.value && vehicles.value.some(v => v.id === currentVehicleId.value)

      // 如果没有选中车辆，或选中的车辆不存在，选中第一个活跃车辆
      if (!isValidVehicle && activeVehicles.value.length > 0) {
        currentVehicleId.value = activeVehicles.value[0].id
        saveCurrentVehicleId()
      }
    }
  }

  // 创建车辆
  const createVehicle = async (data: CreateVehicleRequest) => {
    const vehicle = await vehiclesApi.createVehicle(data)
    vehicles.value.push(vehicle)
    return vehicle
  }

  // 更新车辆
  const updateVehicle = async (id: number, data: UpdateVehicleRequest) => {
    const vehicle = await vehiclesApi.updateVehicle(id, data)
    const index = vehicles.value.findIndex((v) => v.id === id)
    if (index !== -1) {
      vehicles.value[index] = vehicle
    }
    return vehicle
  }

  // 删除车辆
  const deleteVehicle = async (id: number) => {
    await vehiclesApi.deleteVehicle(id)
    vehicles.value = vehicles.value.filter((v) => v.id !== id)

    // 如果删除的是当前车辆，切换到其他车辆
    if (currentVehicleId.value === id) {
      currentVehicleId.value = activeVehicles.value[0]?.id || null
      saveCurrentVehicleId()
    }
  }

  // 设置当前车辆
  const setCurrentVehicle = (vehicleId: number) => {
    currentVehicleId.value = vehicleId
    saveCurrentVehicleId()
  }

  const saveCurrentVehicleId = () => {
    if (currentVehicleId.value) {
      localStorage.setItem('current_vehicle_id', currentVehicleId.value.toString())
    } else {
      localStorage.removeItem('current_vehicle_id')
    }
  }

  return {
    vehicles,
    currentVehicleId,
    currentVehicle,
    activeVehicles,
    loading,
    fetchVehicles,
    createVehicle,
    updateVehicle,
    deleteVehicle,
    setCurrentVehicle,
  }
})
