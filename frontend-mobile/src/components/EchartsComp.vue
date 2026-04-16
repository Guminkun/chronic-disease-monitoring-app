<template>
  <!-- #ifdef MP-WEIXIN -->
  <canvas
    type="2d"
    :id="canvasId"
    :canvas-id="canvasId"
    class="ec-canvas"
    @touchstart="touchStart"
    @touchmove="touchMove"
    @touchend="touchEnd"
  ></canvas>
  <!-- #endif -->

  <!-- #ifndef MP-WEIXIN -->
  <div :id="canvasId" class="ec-canvas"></div>
  <!-- #endif -->
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, getCurrentInstance } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  canvasId: string
}>()

const emit = defineEmits<{
  (e: 'init', chart: any): void
}>()

let chartInstance: any = null
const instance = getCurrentInstance()

function initMpChart(retry = 0) {
  const query = uni.createSelectorQuery().in(instance?.proxy)
  ;(query as any)
    .select(`#${props.canvasId}`)
    .fields({ node: true, size: true })
    .exec((res: any) => {
      if (!res || !res[0] || !res[0].node) {
        if (retry < 8) setTimeout(() => initMpChart(retry + 1), 150)
        return
      }
      const canvas = res[0].node
      const width = res[0].width || 300
      const height = res[0].height || 300
      const dpr = uni.getSystemInfoSync().pixelRatio || 1

      canvas.width = width * dpr
      canvas.height = height * dpr

      chartInstance = echarts.init(canvas, null, {
        width,
        height,
        devicePixelRatio: dpr
      })

      emit('init', chartInstance)
    })
}

function initWebChart() {
  // 运行时判断，避免小程序环境访问 document
  if (typeof document === 'undefined') {
    // 小程序环境降级到 MP 初始化
    initMpChart()
    return
  }
  const el = document.getElementById(props.canvasId)
  if (!el) return
  chartInstance = echarts.init(el)
  emit('init', chartInstance)
}

function touchStart(e: any) {
  chartInstance?.dispatchAction?.({ type: 'showTip', ...e })
}
function touchMove(e: any) {
  chartInstance?.dispatchAction?.({ type: 'showTip', ...e })
}
function touchEnd(e: any) {
  chartInstance?.dispatchAction?.({ type: 'hideTip' })
}

onMounted(() => {
  // #ifdef MP-WEIXIN
  setTimeout(() => initMpChart(), 200)
  // #endif

  // #ifndef MP-WEIXIN
  setTimeout(() => initWebChart(), 50)
  // #endif
})

onUnmounted(() => {
  chartInstance?.dispose?.()
  chartInstance = null
})
</script>

<style scoped>
.ec-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
