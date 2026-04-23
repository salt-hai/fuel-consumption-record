// 金额格式化
export const formatMoney = (amount: number): string => {
  return `¥${amount.toFixed(2)}`
}

// 油耗格式化
export const formatConsumption = (consumption: number): string => {
  return `${consumption.toFixed(1)} L/100km`
}

// 日期格式化
export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 日期时间格式化
export const formatDateTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  const dateStr = formatDate(d)
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${dateStr} ${hours}:${minutes}`
}

// 里程格式化
export const formatOdometer = (odometer: number): string => {
  return `${odometer.toLocaleString()} km`
}

// 油量格式化
export const formatVolume = (volume: number): string => {
  return `${volume.toFixed(2)} L`
}

// 计算油耗
export const calculateConsumption = (
  currentOdometer: number,
  previousOdometer: number,
  volume: number
): number => {
  if (volume <= 0) return 0
  const distance = currentOdometer - previousOdometer
  if (distance <= 0) return 0
  return (volume / distance) * 100
}
