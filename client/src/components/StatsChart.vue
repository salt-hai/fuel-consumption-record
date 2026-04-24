<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  type: 'line' | 'bar'
  data: any[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  updateChart()

  // 响应式调整
  const resizeObserver = new ResizeObserver(() => {
    chartInstance?.resize()
  })
  resizeObserver.observe(chartRef.value)
}

const updateChart = () => {
  if (!chartInstance) return

  let option: EChartsOption

  if (props.type === 'line') {
    option = getLineOption()
  } else {
    option = getBarOption()
  }

  chartInstance.setOption(option, true)
}

const getLineOption = (): EChartsOption => {
  const dates = props.data.map((d: any) => d.date)
  const values = props.data.map((d: any) => d.consumption)

  return {
    grid: {
      left: '12%',
      right: '8%',
      bottom: '12%',
      top: '8%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      confine: true,
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>油耗: ${param.value} L/100km`
      },
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#e5e7eb' },
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 10,
        rotate: dates.some((d: string) => d.length > 7) ? 30 : 0,
        interval: dates.length > 6 ? 'auto' : 0,
        formatter: (value: string) => {
          // 简化日期显示：2026-04 -> 04月
          if (value.includes('-')) {
            const parts = value.split('-')
            return `${parts[1]}月`
          }
          return value
        },
      },
    },
    yAxis: {
      type: 'value',
      name: 'L/100km',
      nameTextStyle: { color: '#6b7280', fontSize: 10 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: {
        lineStyle: { color: '#f3f4f6', type: 'dashed' },
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 10,
        formatter: (value: number) => value.toFixed(1),
      },
    },
    series: [
      {
        type: 'line',
        data: values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: {
          color: '#4f46e5',
          width: 2,
        },
        itemStyle: {
          color: '#4f46e5',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(79, 70, 229, 0.2)' },
            { offset: 1, color: 'rgba(79, 70, 229, 0)' },
          ]),
        },
      },
    ],
  }
}

const getBarOption = (): EChartsOption => {
  const months = props.data.map((d: any) => d.month)
  const costs = props.data.map((d: any) => d.cost)

  return {
    grid: {
      left: '12%',
      right: '8%',
      bottom: '12%',
      top: '8%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      confine: true,
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>花费: ¥${param.value}`
      },
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: {
        lineStyle: { color: '#e5e7eb' },
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 10,
        interval: months.length > 6 ? 'auto' : 0,
        rotate: months.some((m: string) => m.length > 7) ? 30 : 0,
        formatter: (value: string) => {
          // 简化月份显示：2026-04 -> 04月
          if (value.includes('-')) {
            const parts = value.split('-')
            return `${parts[1]}月`
          }
          return value
        },
      },
    },
    yAxis: {
      type: 'value',
      name: '元',
      nameTextStyle: { color: '#6b7280', fontSize: 10 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: {
        lineStyle: { color: '#f3f4f6', type: 'dashed' },
      },
      axisLabel: {
        color: '#6b7280',
        fontSize: 10,
        formatter: (value: number) => {
          if (value >= 1000) return (value / 1000).toFixed(1) + 'k'
          return value.toString()
        },
      },
    },
    series: [
      {
        type: 'bar',
        data: costs,
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#6366f1' },
            { offset: 1, color: '#4f46e5' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  }
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  chartInstance?.dispose()
})
</script>

<template>
  <div ref="chartRef" class="stats-chart" />
</template>

<style scoped>
.stats-chart {
  width: 100%;
  height: 100%;
  min-height: 180px;
}
</style>
