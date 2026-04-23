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
    if (!currentVehicleId.value) return vehicles.value[0] || null
    return vehicles.value.find((v) => v.id === currentVehicleId.value) || null
  })

  const activeVehicles = computed(() =>
    vehicles.value.filter((v) => v.is_active)
  )

  // 获取车辆列表
  const fetchVehicles = async () => {
    loading.value = true
    try {
      vehicles.value = await vehiclesApi.getVehicles()

      // 如果没有当前选中的车辆，默认选中第一个
      if (!currentVehicleId.value && activeVehicles.value.length > 0) {
        currentVehicleId.value = activeVehicles.value[0].id
        saveCurrentVehicleId()
      }
    } finally {
      loading.value = false
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
