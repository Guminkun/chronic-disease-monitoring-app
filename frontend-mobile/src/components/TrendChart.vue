<template>
  <view class="trend-chart-container">
    <view class="chart-header" v-if="title">
      <text class="chart-title">{{ title }}</text>
      <text class="chart-unit" v-if="unit">单位: {{ unit }}</text>
    </view>
    <view class="canvas-wrapper">
      <canvas
        type="2d"
        id="trendCanvas"
        canvas-id="trendCanvas"
        class="trend-canvas"
        :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      ></canvas>
      <view v-if="tooltip.show" class="tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <text class="tooltip-date">{{ tooltip.date }}</text>
        <text class="tooltip-value">{{ tooltip.value }} {{ unit || '' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, getCurrentInstance, watch, ref, reactive } from 'vue'

const props = defineProps<{
  title?: string
  data: { date: string; value: number }[]
  unit?: string
}>()

const instance = getCurrentInstance()
const canvasWidth = 320
const canvasHeight = 200
let canvas: any = null
let ctx: any = null
let pointsInfo: { x: number; y: number; value: number; date: string }[] = []

const tooltip = reactive({
  show: false,
  x: 0,
  y: 0,
  date: '',
  value: 0
})

function drawChart() {
  if (!ctx || !props.data || props.data.length < 2) return

  const dpr = uni.getSystemInfoSync().pixelRatio || 1
  ctx.clearRect(0, 0, canvasWidth * dpr, canvasHeight * dpr)

  const padding = { top: 25, right: 10, bottom: 35, left: 40 }
  const chartWidth = canvasWidth - padding.left - padding.right
  const chartHeight = canvasHeight - padding.top - padding.bottom

  const values = props.data.map(d => d.value)
  const maxVal = Math.max(...values)
  const range = maxVal || 1

  ctx.save()
  ctx.scale(dpr, dpr)

  // 绘制网格背景
  ctx.fillStyle = '#fafbfc'
  ctx.fillRect(padding.left, padding.top, chartWidth, chartHeight)

  // 绘制网格线
  ctx.strokeStyle = '#e8ecf0'
  ctx.lineWidth = 0.5
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartHeight * i / 4)
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(canvasWidth - padding.right, y)
    ctx.stroke()
  }

  // 绘制Y轴刻度（从0开始）
  ctx.fillStyle = '#7c8591'
  ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartHeight * i / 4)
    const val = maxVal - (range * i / 4)
    ctx.fillText(val.toFixed(1), padding.left - 8, y + 3)
  }

  // 计算数据点
  pointsInfo = []
  props.data.forEach((d, i) => {
    const x = padding.left + (chartWidth * i / (props.data.length - 1))
    const y = padding.top + chartHeight - (chartHeight * d.value / range)
    pointsInfo.push({ x, y, value: d.value, date: d.date })
  })

  // 绘制渐变区域
  ctx.beginPath()
  ctx.moveTo(pointsInfo[0].x, canvasHeight - padding.bottom)
  pointsInfo.forEach(p => ctx.lineTo(p.x, p.y))
  ctx.lineTo(pointsInfo[pointsInfo.length - 1].x, canvasHeight - padding.bottom)
  ctx.closePath()

  const gradient = ctx.createLinearGradient(0, padding.top, 0, canvasHeight - padding.bottom)
  gradient.addColorStop(0, 'rgba(99, 102, 241, 0.25)')
  gradient.addColorStop(0.5, 'rgba(99, 102, 241, 0.12)')
  gradient.addColorStop(1, 'rgba(99, 102, 241, 0.02)')
  ctx.fillStyle = gradient
  ctx.fill()

  // 绘制曲线
  ctx.beginPath()
  ctx.strokeStyle = '#6366f1'
  ctx.lineWidth = 2.5
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  pointsInfo.forEach((p, i) => {
    if (i === 0) ctx.moveTo(p.x, p.y)
    else ctx.lineTo(p.x, p.y)
  })
  ctx.stroke()

  // 绘制数据点
  pointsInfo.forEach((p, i) => {
    // 外圈光晕
    ctx.beginPath()
    ctx.arc(p.x, p.y, 8, 0, Math.PI * 2)
    ctx.fillStyle = 'rgba(99, 102, 241, 0.15)'
    ctx.fill()

    // 白色背景
    ctx.beginPath()
    ctx.arc(p.x, p.y, 5, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()

    // 内圈
    ctx.beginPath()
    ctx.arc(p.x, p.y, 4, 0, Math.PI * 2)
    ctx.fillStyle = '#6366f1'
    ctx.fill()

    // 高亮点
    ctx.beginPath()
    ctx.arc(p.x, p.y, 2, 0, Math.PI * 2)
    ctx.fillStyle = '#ffffff'
    ctx.fill()
  })

  // 绘制X轴标签
  ctx.fillStyle = '#7c8591'
  ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif'
  ctx.textAlign = 'center'
  props.data.forEach((d, i) => {
    const x = padding.left + (chartWidth * i / (props.data.length - 1))
    const label = d.date && d.date.length > 5 ? d.date.substring(5) : d.date || ''
    ctx.fillText(label, x, canvasHeight - padding.bottom + 18)
  })

  ctx.restore()
}

function onTouchStart(e: any) {
  showTooltip(e)
}

function onTouchMove(e: any) {
  showTooltip(e)
}

function onTouchEnd() {
  tooltip.show = false
}

function showTooltip(e: any) {
  if (!e.touches || e.touches.length === 0 || pointsInfo.length === 0) return
  
  const touch = e.touches[0]
  const x = touch.x
  const y = touch.y
  
  // 找到最近的数据点
  let nearestPoint = pointsInfo[0]
  let minDistance = Infinity
  
  pointsInfo.forEach(p => {
    const distance = Math.sqrt((p.x - x) ** 2 + (p.y - y) ** 2)
    if (distance < minDistance) {
      minDistance = distance
      nearestPoint = p
    }
  })
  
  // 如果距离足够近，显示tooltip
  if (minDistance < 50) {
    tooltip.show = true
    tooltip.x = nearestPoint.x - 40
    tooltip.y = nearestPoint.y - 50
    tooltip.date = nearestPoint.date
    tooltip.value = nearestPoint.value
  } else {
    tooltip.show = false
  }
}

function initCanvas() {
  const query = uni.createSelectorQuery().in(instance?.proxy)
  ;(query as any)
    .select('#trendCanvas')
    .fields({ node: true, size: true })
    .exec((res: any) => {
      if (!res || !res[0] || !res[0].node) {
        setTimeout(() => initCanvas(), 150)
        return
      }

      const dpr = uni.getSystemInfoSync().pixelRatio || 1
      canvas = res[0].node
      canvas.width = canvasWidth * dpr
      canvas.height = canvasHeight * dpr
      ctx = canvas.getContext('2d')

      drawChart()
    })
}

watch(() => props.data, () => {
  if (ctx) drawChart()
}, { deep: true })

onMounted(() => {
  setTimeout(() => initCanvas(), 200)
})
</script>

<style scoped>
.trend-chart-container {
  width: 100%;
  max-width: 100%;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 0 2px;
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  letter-spacing: -0.2px;
}

.chart-unit {
  font-size: 10px;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 8px;
}

.canvas-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
}

.trend-canvas {
  display: block;
}

.tooltip {
  position: absolute;
  background: rgba(30, 41, 59, 0.95);
  border-radius: 8px;
  padding: 8px 12px;
  pointer-events: none;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 80px;
  text-align: center;
}

.tooltip-date {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.tooltip-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}
</style>
