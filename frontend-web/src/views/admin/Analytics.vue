<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">数据统计</h2>
        <p class="text-gray-500 mt-1">系统数据分析和使用统计</p>
      </div>
      <el-button type="primary" class="!bg-primary" icon="Download">导出数据</el-button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Card 1 -->
      <div class="bg-blue-50 p-6 rounded-xl border border-blue-100 relative overflow-hidden group transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <span class="text-gray-600 font-medium">总用户数</span>
          <div class="p-2 bg-white/60 rounded-lg text-blue-500">
            <el-icon><User /></el-icon>
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-2">3,600</div>
        <div class="text-xs text-gray-500">较上周增加 12%</div>
      </div>

      <!-- Card 2 -->
      <div class="bg-green-50 p-6 rounded-xl border border-green-100 relative overflow-hidden group transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <span class="text-gray-600 font-medium">待审核医生</span>
          <div class="p-2 bg-white/60 rounded-lg text-green-500">
            <el-icon><CircleCheck /></el-icon>
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-2">12</div>
        <div class="text-xs text-gray-500">需要立即处理</div>
      </div>

      <!-- Card 3 -->
      <div class="bg-purple-50 p-6 rounded-xl border border-purple-100 relative overflow-hidden group transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <span class="text-gray-600 font-medium">已验证医生</span>
          <div class="p-2 bg-white/60 rounded-lg text-purple-500">
            <el-icon><Postcard /></el-icon>
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-2">248</div>
        <div class="text-xs text-gray-500">本周已验证</div>
      </div>

      <!-- Card 4 -->
      <div class="bg-orange-50 p-6 rounded-xl border border-orange-100 relative overflow-hidden group transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <span class="text-gray-600 font-medium">每日活跃</span>
          <div class="p-2 bg-white/60 rounded-lg text-orange-500">
            <el-icon><TrendCharts /></el-icon>
          </div>
        </div>
        <div class="text-3xl font-bold text-gray-900 mb-2">1,850</div>
        <div class="text-xs text-gray-500">今日活跃</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Line Chart -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <h3 class="font-bold text-gray-900 mb-6">用户增长趋势</h3>
        <div ref="lineChartRef" class="h-64 w-full"></div>
      </div>

      <!-- Bar Chart -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <h3 class="font-bold text-gray-900 mb-6">日活跃用户时间分布</h3>
        <div ref="barChartRef" class="h-64 w-full"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { User, CircleCheck, Postcard, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const lineChartRef = ref<HTMLElement | null>(null)
const barChartRef = ref<HTMLElement | null>(null)

let lineChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

onMounted(() => {
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value)
    lineChart.setOption({
      grid: { top: 10, right: 10, bottom: 20, left: 40, containLabel: true },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['1月20', '1月21', '1月22', '1月23', '1月24', '1月25', '1月26'],
        axisLine: { lineStyle: { color: '#E2E8F0' } },
        axisLabel: { color: '#94A3B8' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: '#F1F5F9', type: 'dashed' } },
        axisLabel: { color: '#94A3B8' }
      },
      series: [
        {
          data: [1200, 1500, 1800, 2200, 2600, 3100, 3600],
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { color: '#3B82F6', width: 3 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(59, 130, 246, 0.2)' },
              { offset: 1, color: 'rgba(59, 130, 246, 0)' }
            ])
          }
        },
        {
          data: [800, 950, 1100, 1400, 1700, 2000, 2300],
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { color: '#10B981', width: 3 }
        },
        {
          data: [400, 450, 500, 600, 700, 800, 900],
          type: 'line',
          smooth: true,
          showSymbol: false,
          lineStyle: { color: '#A855F7', width: 3 }
        }
      ]
    })
  }

  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    barChart.setOption({
      grid: { top: 10, right: 10, bottom: 20, left: 30, containLabel: true },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: ['6:00', '9:00', '12:00', '15:00', '18:00', '21:00'],
        axisLine: { lineStyle: { color: '#E2E8F0' } },
        axisLabel: { color: '#94A3B8' }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: '#F1F5F9', type: 'dashed' } },
        axisLabel: { color: '#94A3B8' }
      },
      series: [
        {
          data: [120, 250, 450, 380, 320, 150],
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            color: '#3B82F6',
            borderRadius: [4, 4, 0, 0]
          }
        }
      ]
    })
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  lineChart?.dispose()
  barChart?.dispose()
})

const handleResize = () => {
  lineChart?.resize()
  barChart?.resize()
}
</script>
