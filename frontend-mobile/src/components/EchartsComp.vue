<template>
  <!-- #ifdef MP-WEIXIN -->
  <canvas
    type="2d"
    :id="canvasId"
    :canvas-id="canvasId"
    class="ec-canvas"
  ></canvas>
  <!-- #endif -->

  <!-- #ifndef MP-WEIXIN -->
  <view :id="canvasId" class="ec-canvas"></view>
  <!-- #endif -->
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, getCurrentInstance } from 'vue'

const props = defineProps<{
  canvasId: string
}>()

const emit = defineEmits<{
  (e: 'init', chart: any): void
}>()

let chartInstance: any = null
let canvasNode: any = null
let ctx: any = null
const instance = getCurrentInstance()

// #ifdef MP-WEIXIN
class MpChart {
  canvas: any
  ctx: any
  width: number
  height: number
  option: any = null
  
  constructor(canvas: any, ctx: any, width: number, height: number) {
    this.canvas = canvas
    this.ctx = ctx
    this.width = width
    this.height = height
  }
  
  setOption(option: any, notMerge?: boolean) {
    this.option = option
    this.render()
  }
  
  clear() {
    if (this.ctx) {
      this.ctx.clearRect(0, 0, this.width, this.height)
    }
  }
  
  dispose() {
    this.clear()
  }
  
  render() {
    if (!this.ctx || !this.option) return
    
    this.clear()
    
    const series = this.option.series
    if (!series || series.length === 0) return
    
    const s = series[0]
    if (s.type !== 'line') return
    
    const data = s.data || []
    const xAxis = this.option.xAxis || {}
    const title = this.option.title || {}
    
    const padding = 40
    const chartWidth = this.width - padding * 2
    const chartHeight = this.height - padding * 2
    
    if (title.text) {
      this.ctx.fillStyle = '#1e293b'
      this.ctx.font = 'bold 16px sans-serif'
      this.ctx.textAlign = 'center'
      this.ctx.fillText(title.text, this.width / 2, 25)
    }
    
    if (data.length < 2) return
    
    const minVal = Math.min(...data)
    const maxVal = Math.max(...data)
    const range = maxVal - minVal || 1
    
    this.ctx.strokeStyle = '#e2e8f0'
    this.ctx.lineWidth = 1
    this.ctx.beginPath()
    this.ctx.moveTo(padding, padding)
    this.ctx.lineTo(padding, this.height - padding)
    this.ctx.lineTo(this.width - padding, this.height - padding)
    this.ctx.stroke()
    
    this.ctx.fillStyle = '#64748b'
    this.ctx.font = '12px sans-serif'
    this.ctx.textAlign = 'right'
    for (let i = 0; i <= 4; i++) {
      const y = padding + (chartHeight * i / 4)
      const val = maxVal - (range * i / 4)
      this.ctx.fillText(val.toFixed(1), padding - 5, y + 4)
      
      this.ctx.strokeStyle = '#f1f5f9'
      this.ctx.beginPath()
      this.ctx.moveTo(padding, y)
      this.ctx.lineTo(this.width - padding, y)
      this.ctx.stroke()
    }
    
    const points: any[] = []
    data.forEach((val: number, i: number) => {
      const x = padding + (chartWidth * i / (data.length - 1))
      const y = padding + chartHeight - (chartHeight * (val - minVal) / range)
      points.push({ x, y, val })
    })
    
    this.ctx.beginPath()
    this.ctx.moveTo(points[0].x, this.height - padding)
    points.forEach(p => this.ctx.lineTo(p.x, p.y))
    this.ctx.lineTo(points[points.length - 1].x, this.height - padding)
    this.ctx.closePath()
    
    const gradient = this.ctx.createLinearGradient(0, padding, 0, this.height - padding)
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)')
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)')
    this.ctx.fillStyle = gradient
    this.ctx.fill()
    
    this.ctx.beginPath()
    this.ctx.strokeStyle = '#3b82f6'
    this.ctx.lineWidth = 3
    points.forEach((p, i) => {
      if (i === 0) this.ctx.moveTo(p.x, p.y)
      else this.ctx.lineTo(p.x, p.y)
    })
    this.ctx.stroke()
    
    points.forEach(p => {
      this.ctx.beginPath()
      this.ctx.arc(p.x, p.y, 4, 0, Math.PI * 2)
      this.ctx.fillStyle = '#3b82f6'
      this.ctx.fill()
      this.ctx.strokeStyle = '#ffffff'
      this.ctx.lineWidth = 2
      this.ctx.stroke()
    })
    
    const xData = xAxis.data || []
    this.ctx.fillStyle = '#64748b'
    this.ctx.font = '11px sans-serif'
    this.ctx.textAlign = 'center'
    points.forEach((p, i) => {
      const label = xData[i] || ''
      const displayLabel = label.length > 5 ? label.substring(5) : label
      this.ctx.fillText(displayLabel, p.x, this.height - padding + 20)
    })
  }
}

function initMpChart(retry = 0) {
  const query = uni.createSelectorQuery().in(instance?.proxy)
  ;(query as any)
    .select(`#${props.canvasId}`)
    .fields({ node: true, size: true })
    .exec((res: any) => {
      if (!res || !res[0] || !res[0].node) {
        if (retry < 8) {
          setTimeout(() => initMpChart(retry + 1), 150)
        }
        return
      }
      
      const canvas = res[0].node
      const width = res[0].width || 300
      const height = res[0].height || 300
      const dpr = uni.getSystemInfoSync().pixelRatio || 1

      canvas.width = width * dpr
      canvas.height = height * dpr
      
      const context = canvas.getContext('2d')
      context.scale(dpr, dpr)
      
      canvasNode = canvas
      ctx = context
      
      chartInstance = new MpChart(canvas, context, width, height)
      emit('init', chartInstance)
    })
}

onMounted(() => {
  setTimeout(() => initMpChart(), 200)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
// #endif

// #ifndef MP-WEIXIN
import * as echarts from 'echarts'

function initWebChart() {
  const el = document.getElementById(props.canvasId)
  if (!el) {
    setTimeout(() => initWebChart(), 100)
    return
  }
  
  chartInstance = echarts.init(el)
  emit('init', chartInstance)
}

onMounted(() => {
  setTimeout(() => initWebChart(), 100)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
// #endif
</script>

<style scoped>
.ec-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
