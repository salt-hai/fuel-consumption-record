import api from './index'

export interface StatsSummary {
  total_records: number
  total_cost: number
  total_distance: number
  avg_consumption: number
  latest_consumption: number
}

export interface MonthlyStats {
  month: string
  cost: number
  volume: number
  distance: number
  consumption: number
}

export interface ConsumptionTrend {
  date: string
  consumption: number
}

export interface StatsParams {
  vehicle_id?: number
  period?: 'month' | 'year'
  months?: number
}

// 获取统计数据汇总
export const getStatsSummary = (params?: StatsParams) => {
  return api.get<StatsSummary>('/v1/stats/summary', { params })
}

// 获取月度统计
export const getMonthlyStats = (params?: StatsParams) => {
  return api.get<MonthlyStats[]>('/v1/stats', { params })
}

// 获取油耗趋势
export const getConsumptionTrend = (params?: StatsParams) => {
  return api.get<ConsumptionTrend[]>('/v1/stats/trend', { params })
}
