<template>
  <view class="md-page">
    <view v-if="!metricType || loading" class="state-wrap">
      <text class="state-text">{{ !metricType ? '请稍候…' : '加载中...' }}</text>
    </view>

    <scroll-view v-else scroll-y class="md-scroll" :enable-flex="true">
      <!-- 最新记录 -->
      <view class="card latest-card">
        <view class="latest-row">
          <view class="latest-icon-wrap" :style="{ background: meta.iconBg }">
            <text class="latest-icon">{{ meta.emoji }}</text>
          </view>
          <view class="latest-body">
            <text class="latest-label">最新记录</text>
            <view v-if="latest" class="latest-value-row">
              <text class="latest-value" :style="{ color: meta.accentColor }">{{ latestValueMain }}</text>
              <text class="latest-unit">{{ meta.unit }}</text>
            </view>
            <view v-else class="latest-empty">
              <text>暂无{{ meta.label }}记录</text>
            </view>
            <view v-if="latest" class="latest-meta">
              <view v-if="latestStatus.cls" class="tag-pill" :class="latestStatus.cls">
                <text class="tag-pill-text">{{ latestStatus.text }}</text>
              </view>
              <text v-if="latestScene" class="scene-text">{{ latestScene }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 趋势图 -->
      <view class="card chart-card">
        <text class="card-title">趋势变化</text>
        <view v-if="!chartHasEnough" class="chart-empty">
          <text class="chart-empty-title">数据不足</text>
          <text class="chart-empty-sub">{{ chartEmptyHint }}</text>
        </view>
        <view v-show="chartHasEnough" class="echarts-dom">
          <EchartsComp :canvas-id="chartCanvasId" @init="onChartInit" />
        </view>
      </view>

      <!-- 历史记录 -->
      <view class="card history-card">
        <text class="card-title">历史记录</text>
        <view class="history-divider" />
        <view v-if="historyRows.length === 0" class="history-empty">
          <text>暂无历史记录</text>
        </view>
        <view v-for="item in historyRows" :key="item.id" class="history-item">
          <view class="hi-left">
            <text class="hi-date">{{ formatMD(item.recorded_at) }}</text>
            <text class="hi-scene">{{ item.scene }}</text>
          </view>
          <view class="hi-right">
            <view class="hi-value-wrap">
              <text class="hi-value" :style="{ color: meta.accentColor }">{{ formatReadingValue(item) }}</text>
            </view>
            <view class="hi-row2">
              <view v-if="rowStatus(item).cls" class="hi-tag" :class="rowStatus(item).cls">
                <text class="hi-tag-text">{{ rowStatus(item).text }}</text>
              </view>
              <text class="hi-time">{{ formatHM(item.recorded_at) }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="md-bottom-space" />
    </scroll-view>

    <view v-if="metricType" class="md-fab-row">
      <view class="fab-remind" @click="openMeasurementReminders">
        <text class="fab-remind-icon">🔔</text>
        <text>提醒</text>
      </view>
      <view class="fab-add" @click="openForm">
        <text>+ 记录</text>
      </view>
    </view>

    <!-- 录入 -->
    <view v-if="formVisible" class="modal-mask" @click="closeForm">
      <view class="modal-card" @click.stop>
        <text class="modal-title">记录{{ meta.label }}</text>
        <template v-if="metricType === 'blood_pressure'">
          <view class="form-field">
            <text class="field-label">收缩压</text>
            <view class="field-input-row">
              <input class="field-input" type="number" v-model="formSys" placeholder="如 120" />
              <text class="field-unit">mmHg</text>
            </view>
          </view>
          <view class="form-field">
            <text class="field-label">舒张压</text>
            <view class="field-input-row">
              <input class="field-input" type="number" v-model="formDia" placeholder="如 80" />
              <text class="field-unit">mmHg</text>
            </view>
          </view>
        </template>
        <template v-else>
          <view class="form-field">
            <text class="field-label">数值</text>
            <view class="field-input-row">
              <input class="field-input" type="digit" v-model="formValue1" placeholder="请输入" />
              <text class="field-unit">{{ meta.unit }}</text>
            </view>
          </view>
        </template>
        <view class="form-field">
          <text class="field-label">测量场景（选填）</text>
          <view class="scene-chips">
            <view
              v-for="s in scenePresets"
              :key="s"
              class="scene-chip"
              :class="{ active: formScene === s }"
              @click="pickScene(s)"
            >
              <text>{{ s }}</text>
            </view>
          </view>
          <input
            class="field-input-inline"
            v-model="formSceneCustom"
            placeholder="或填写其他场景"
            @input="onSceneCustom"
          />
        </view>
        <view class="form-field">
          <text class="field-label">备注（选填）</text>
          <textarea class="field-textarea" v-model="formNotes" placeholder="其他说明" />
        </view>
        <view class="modal-btns">
          <view class="modal-btn ghost" @click="closeForm"><text>取消</text></view>
          <view class="modal-btn primary" :class="{ disabled: submitting }" @click="submitForm">
            <text>{{ submitting ? '保存中...' : '保存' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 提醒管理面板 -->
    <view v-if="reminderPanelVisible" class="drawer-mask" @click="closeReminderPanel">
      <view class="drawer" @click.stop>
        <view class="drawer-handle" />
        <view class="drawer-head">
          <view class="rp-title-wrap">
            <text class="drawer-title">{{ metricTypeLabel[reminderType] }}测量提醒</text>
            <text class="drawer-unit">管理测量提醒任务</text>
          </view>
          <view class="drawer-add-btn" @click="openReminderForm()">
            <text class="drawer-add-txt">+ 新增</text>
          </view>
        </view>
        <scroll-view scroll-y enable-flex class="drawer-history">
          <view v-if="reminderPanelReminders.length === 0" class="rp-empty">
            <text class="rp-empty-icon">🔔</text>
            <text class="rp-empty-text">还没有设置测量提醒</text>
            <text class="rp-empty-hint">点击右上角「+ 新增」开始设置</text>
          </view>
          <view v-for="item in reminderPanelReminders" :key="item.id" class="rp-item">
            <view class="rp-item-left">
              <view class="rp-dot" :class="item.is_active ? 'dot-active' : 'dot-off'" />
              <view class="rp-item-info">
                <text class="rp-item-title">{{ item.title }}</text>
                <text class="rp-item-schedule">{{ item.schedule_text || '未设置频率' }}</text>
              </view>
            </view>
            <view class="rp-item-actions">
              <view
                class="rp-switch"
                :class="item.is_active ? 'switch-on' : 'switch-off'"
                @click="toggleReminderActive(item)"
              >
                <view class="rp-switch-thumb" :class="item.is_active ? 'thumb-on' : 'thumb-off'" />
              </view>
              <view class="rp-action-btn edit-btn" @click="openReminderForm(item)"><text>✏️</text></view>
              <view class="rp-action-btn del-btn" @click="removeReminder(item)"><text>🗑️</text></view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 提醒表单 -->
    <view v-if="reminderFormVisible" class="modal-mask" @click="closeReminderForm">
      <view class="modal-card modal-card-reminder" @click.stop>
        <text class="modal-title">{{ reminderEditTarget ? '编辑提醒' : '新增提醒' }}</text>
        <view class="form-field">
          <text class="field-label">提醒频率</text>
          <view class="freq-options">
            <view
              v-for="f in freqOptions"
              :key="f"
              class="freq-chip"
              :class="{ 'freq-active': reminderFormFreq === f }"
              @click="reminderFormFreq = f"
            >
              <text>{{ f }}</text>
            </view>
          </view>
        </view>
        <view class="form-field">
          <text class="field-label">提醒时间</text>
          <picker mode="time" :value="reminderFormTime" @change="(e: any) => (reminderFormTime = e.detail.value)">
            <view class="field-input-row time-picker-row">
              <text class="time-value">{{ reminderFormTime }}</text>
              <text class="field-unit">点提醒</text>
            </view>
          </picker>
        </view>
        <view class="rp-preview">
          <text class="rp-preview-label">提醒预览</text>
          <text class="rp-preview-text">
            {{ metricTypeLabel[reminderType] }}测量提醒 · {{ reminderFormFreq }} {{ reminderFormTime }}
          </text>
        </view>
        <view class="modal-btns">
          <view class="modal-btn ghost" @click="closeReminderForm"><text>取消</text></view>
          <view class="modal-btn primary" :class="{ disabled: reminderFormSaving }" @click="saveReminder">
            <text>{{ reminderFormSaving ? '保存中...' : '保存提醒' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

import { computed, ref, watch, nextTick } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import * as echarts from 'echarts'
import EchartsComp from '@/components/EchartsComp.vue'
import { getHealthReadings, addHealthReading, type HealthReadingData } from '@/api/patient'
import {
  useMeasurementReminders,
  isMonitoringMetricType,
  type MonitoringMetricType
} from '@/composables/useMeasurementReminders'

type MetricType = MonitoringMetricType

type Reading = {
  id: string | number
  patient_id: string
  type: string
  value_1: number
  value_2?: number | null
  unit?: string | null
  notes?: string | null
  recorded_at: string
}

const METRICS = {
  blood_sugar: {
    label: '血糖',
    unit: 'mmol/L',
    emoji: '💧',
    iconBg: 'linear-gradient(135deg,#fb923c,#f97316)',
    accentColor: '#ea580c',
    chartLine2: '#fdba74',
    dualLine: false as const
  },
  blood_pressure: {
    label: '血压',
    unit: 'mmHg',
    emoji: '❤️',
    iconBg: 'linear-gradient(135deg,#60a5fa,#3b82f6)',
    accentColor: '#3b82f6',
    chartLine2: '#94a3b8',
    dualLine: true as const
  },
  heart_rate: {
    label: '心率',
    unit: '次/分',
    emoji: '📈',
    iconBg: 'linear-gradient(135deg,#4ade80,#22c55e)',
    accentColor: '#16a34a',
    chartLine2: '#86efac',
    dualLine: false as const
  },
  weight: {
    label: '体重',
    unit: 'kg',
    emoji: '⚖️',
    iconBg: 'linear-gradient(135deg,#c084fc,#a855f7)',
    accentColor: '#9333ea',
    chartLine2: '#d8b4fe',
    dualLine: false as const
  },
  blood_lipids: {
    label: '血脂',
    unit: 'mmol/L',
    emoji: '🩸',
    iconBg: 'linear-gradient(135deg,#fbbf24,#f59e0b)',
    accentColor: '#d97706',
    chartLine2: '#fde68a',
    dualLine: false as const
  },
  uric_acid: {
    label: '尿酸',
    unit: 'μmol/L',
    emoji: '🧪',
    iconBg: 'linear-gradient(135deg,#818cf8,#6366f1)',
    accentColor: '#6366f1',
    chartLine2: '#a5b4fc',
    dualLine: false as const
  }
} as const

const {
  metricTypeLabel,
  loadReminders,
  reminderPanelVisible,
  reminderType,
  reminderPanelReminders,
  reminderFormVisible,
  reminderEditTarget,
  reminderFormTime,
  reminderFormFreq,
  reminderFormSaving,
  freqOptions,
  openReminderPanel,
  closeReminderPanel,
  openReminderForm,
  closeReminderForm,
  saveReminder,
  toggleReminderActive,
  removeReminder
} = useMeasurementReminders()

const metricType = ref<MetricType | ''>('')
const meta = computed(() => METRICS[(metricType.value || 'blood_sugar') as MetricType])

const loading = ref(true)
const readings = ref<Reading[]>([])
const chartInstance = ref<any>(null)
const submitting = ref(false)

const chartCanvasId = 'metric-trend-canvas'

const formVisible = ref(false)
const formSys = ref('')
const formDia = ref('')
const formValue1 = ref('')
const formNotes = ref('')
const formScene = ref('')
const formSceneCustom = ref('')
const scenePresets = ['晨起', '上午', '下午', '晚上', '睡前', '静息']

const sortedAsc = computed(() =>
  [...readings.value].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  )
)

const validBp = computed(() =>
  sortedAsc.value.filter((r) => r.value_2 != null && Number.isFinite(Number(r.value_2)))
)

const chartSource = computed(() => {
  if (meta.value.dualLine) return validBp.value
  return sortedAsc.value.filter((r) => Number.isFinite(Number(r.value_1)))
})

const chartHasEnough = computed(() => chartSource.value.length >= 2)

const chartEmptyHint = computed(() =>
  meta.value.dualLine
    ? '至少需要 2 条含舒张压的记录以展示趋势'
    : `至少需要 2 条${meta.value.label}记录以展示趋势`
)

const latest = computed(() => {
  const arr = sortedAsc.value
  return arr.length ? arr[arr.length - 1] : null
})

const latestValueMain = computed(() => {
  if (!latest.value) return ''
  if (metricType.value === 'blood_pressure') {
    return latest.value.value_2 != null
      ? `${latest.value.value_1}/${latest.value.value_2}`
      : `${latest.value.value_1}`
  }
  return `${latest.value.value_1}`
})

const latestStatus = computed(() => (latest.value ? statusOf(latest.value) : { text: '', cls: '' }))

const latestScene = computed(() =>
  latest.value ? measurementScene(latest.value.notes, latest.value.recorded_at) : ''
)

const historyRows = computed(() => {
  const rows = [...sortedAsc.value].reverse()
  return rows.map((r) => ({
    ...r,
    scene: measurementScene(r.notes, r.recorded_at)
  }))
})

function formatReadingValue(r: Reading) {
  if (metricType.value === 'blood_pressure') {
    return r.value_2 != null ? `${r.value_1}/${r.value_2}` : `${r.value_1}`
  }
  return `${r.value_1}`
}

function formatMD(iso: string) {
  const d = new Date(iso)
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${m}-${day}`
}

function formatHM(iso: string) {
  const d = new Date(iso)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function statusOf(r: Reading) {
  if (!metricType.value) return { text: '', cls: '' }
  const t = metricType.value
  if (t === 'blood_pressure') {
    if (r.value_2 == null || !Number.isFinite(Number(r.value_2))) {
      return { text: '待补全', cls: 'tag-muted' }
    }
    const sys = Number(r.value_1),
      dia = Number(r.value_2)
    if (sys < 90 || dia < 60) return { text: '偏低', cls: 'tag-low' }
    if (sys >= 140 || dia >= 90) return { text: '偏高', cls: 'tag-high' }
    return { text: '正常', cls: 'tag-normal' }
  }
  if (t === 'blood_sugar') {
    const v = Number(r.value_1)
    if (v < 3.9) return { text: '偏低', cls: 'tag-low' }
    if (v >= 7) return { text: '偏高', cls: 'tag-high' }
    return { text: '正常', cls: 'tag-normal' }
  }
  if (t === 'heart_rate') {
    const v = Number(r.value_1)
    if (v < 60) return { text: '偏低', cls: 'tag-low' }
    if (v > 100) return { text: '偏高', cls: 'tag-high' }
    return { text: '正常', cls: 'tag-normal' }
  }
  if (t === 'blood_lipids') {
    return Number(r.value_1) >= 5.2 ? { text: '偏高', cls: 'tag-high' } : { text: '正常', cls: 'tag-normal' }
  }
  if (t === 'uric_acid') {
    return Number(r.value_1) > 420 ? { text: '偏高', cls: 'tag-high' } : { text: '正常', cls: 'tag-normal' }
  }
  return { text: '', cls: '' }
}

function rowStatus(r: Reading) {
  const s = statusOf(r)
  if (s.cls === 'tag-muted') return s
  if (!s.cls && !s.text) return { text: '', cls: '' }
  return s
}

function measurementScene(notes: string | null | undefined, recordedAt: string) {
  const t = (notes || '').trim()
  const keys = ['晨起', '上午', '下午', '晚上', '睡前', '静息', '运动后', '餐后', '夜间']
  for (const k of keys) {
    if (t.includes(k)) return k
  }
  if (t && t.length <= 10) return t
  const d = new Date(recordedAt)
  const h = d.getHours()
  if (h >= 5 && h < 10) return '晨起'
  if (h >= 10 && h < 12) return '上午'
  if (h >= 12 && h < 18) return '下午'
  if (h >= 18 && h < 22) return '晚上'
  return '夜间'
}

function setNavTitle() {
  uni.setNavigationBarTitle({ title: `${meta.value.label}监测` })
}

onLoad((query) => {
  const t = (query?.type as string) || ''
  if (!isMonitoringMetricType(t)) {
    uni.showToast({ title: '无效的指标类型', icon: 'none' })
    setTimeout(() => uni.navigateBack(), 1200)
    return
  }
  metricType.value = t
  setNavTitle()
})

async function loadData() {
  if (!metricType.value) return
  loading.value = true
  try {
    const res: any = await getHealthReadings(metricType.value)
    readings.value = Array.isArray(res) ? res : []
  } catch {
    readings.value = []
    uni.showToast({ title: '获取数据失败', icon: 'none' })
  } finally {
    loading.value = false
    nextTick(() => tryRenderChart())
  }
}

onShow(() => {
  if (!metricType.value || !isMonitoringMetricType(metricType.value)) return
  loadData()
  loadReminders()
})

function onChartInit(chart: any) {
  chartInstance.value = chart
  tryRenderChart()
}

function tryRenderChart() {
  const chart = chartInstance.value
  if (!chart || !chartHasEnough.value) return

  const pts = chartSource.value
  const times = pts.map((r) => new Date(r.recorded_at).getTime())

  if (meta.value.dualLine) {
    const sys = pts.map((r) => r.value_1)
    const dia = pts.map((r) => Number(r.value_2))
    const minV = Math.min(...dia, ...sys)
    const maxV = Math.max(...dia, ...sys)
    const pad = Math.max(8, Math.round((maxV - minV) * 0.15))
    const yMin = Math.max(40, Math.floor(minV - pad))
    const yMax = Math.min(200, Math.ceil(maxV + pad))
    const sysData = times.map((t, i) => [t, sys[i]] as [number, number])
    const diaData = times.map((t, i) => [t, dia[i]] as [number, number])

    chart.setOption(
      {
        color: [meta.value.accentColor, meta.value.chartLine2],
        tooltip: {
          trigger: 'axis',
          confine: true,
          formatter(params: any) {
            if (!Array.isArray(params) || !params.length) return ''
            const ts = params[0].value[0]
            const date = new Date(ts)
            const head = `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
            const lines = params.map(
              (p: any) => `${p.marker}${p.seriesName}：${p.value[1]} mmHg`
            )
            return `${head}\n${lines.join('\n')}`
          }
        },
        legend: {
          data: ['收缩压', '舒张压'],
          bottom: 0,
          textStyle: { fontSize: 11, color: '#64748b' }
        },
        grid: { left: 12, right: 12, top: 28, bottom: 36, containLabel: true },
        xAxis: {
          type: 'time',
          axisLine: { lineStyle: { color: '#e2e8f0' } },
          axisLabel: {
            color: '#94a3b8',
            fontSize: 10,
            formatter(value: number) {
              const d = new Date(value)
              return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
            }
          },
          splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f1f5f9' } }
        },
        yAxis: {
          type: 'value',
          min: yMin,
          max: yMax,
          name: 'mmHg',
          nameTextStyle: { color: '#94a3b8', fontSize: 10 },
          axisLine: { show: false },
          axisLabel: { color: '#94a3b8', fontSize: 10 },
          splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
        },
        series: [
          {
            name: '收缩压',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            data: sysData,
            lineStyle: { width: 2.5, color: meta.value.accentColor },
            itemStyle: { color: meta.value.accentColor }
          },
          {
            name: '舒张压',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            data: diaData,
            lineStyle: { width: 2.5, color: meta.value.chartLine2 },
            itemStyle: { color: meta.value.chartLine2 }
          }
        ]
      },
      true
    )
    return
  }

  const vals = pts.map((r) => r.value_1)
  const minV = Math.min(...vals)
  const maxV = Math.max(...vals)
  const pad = Math.max(1, Math.round((maxV - minV) * 0.12) || maxV * 0.05)
  const yMin = Math.floor(minV - pad)
  const yMax = Math.ceil(maxV + pad)
  const lineData = times.map((t, i) => [t, vals[i]] as [number, number])
  const lineColor = meta.value.accentColor

  chart.setOption(
    {
      color: [lineColor],
      tooltip: {
        trigger: 'axis',
        confine: true,
        formatter(params: any) {
          const p = params[0]
          if (!p) return ''
          const ts = p.value[0]
          const date = new Date(ts)
          const head = `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
          return `${head}\n${meta.value.label}：${p.value[1]} ${meta.value.unit}`
        }
      },
      grid: { left: 12, right: 12, top: 20, bottom: 24, containLabel: true },
      xAxis: {
        type: 'time',
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 10,
          formatter(value: number) {
            const d = new Date(value)
            return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
          }
        },
        splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f1f5f9' } }
      },
      yAxis: {
        type: 'value',
        min: yMin,
        max: yMax,
        name: meta.value.unit,
        nameTextStyle: { color: '#94a3b8', fontSize: 10 },
        axisLine: { show: false },
        axisLabel: { color: '#94a3b8', fontSize: 10 },
        splitLine: { lineStyle: { type: 'dashed', color: '#f1f5f9' } }
      },
      series: [
        {
          name: meta.value.label,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          data: lineData,
          lineStyle: { width: 2.5, color: lineColor },
          itemStyle: { color: lineColor },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: `${lineColor}33` },
              { offset: 1, color: `${lineColor}08` }
            ])
          }
        }
      ]
    },
    true
  )
}

watch(
  () => [metricType.value, chartSource.value.length, chartHasEnough.value],
  () => nextTick(() => tryRenderChart())
)

function openForm() {
  formSys.value = ''
  formDia.value = ''
  formValue1.value = ''
  formNotes.value = ''
  formScene.value = ''
  formSceneCustom.value = ''
  formVisible.value = true
}

function onSceneCustom() {
  if (formSceneCustom.value.trim()) formScene.value = ''
}

function pickScene(s: string) {
  formScene.value = s
  formSceneCustom.value = ''
}

function closeForm() {
  if (submitting.value) return
  formVisible.value = false
}

function buildNotesForSave() {
  const scene = formSceneCustom.value.trim() || formScene.value.trim()
  const extra = formNotes.value.trim()
  if (scene && extra) return `${scene}；${extra}`
  return scene || extra || undefined
}

async function submitForm() {
  if (submitting.value) return
  if (!metricType.value) return
  const unit = meta.value.unit
  let payload: HealthReadingData

  if (metricType.value === 'blood_pressure') {
    const sys = Number(formSys.value)
    const dia = Number(formDia.value)
    if (!Number.isFinite(sys) || sys <= 0) {
      uni.showToast({ title: '请输入有效收缩压', icon: 'none' })
      return
    }
    if (!Number.isFinite(dia) || dia <= 0) {
      uni.showToast({ title: '请输入有效舒张压', icon: 'none' })
      return
    }
    payload = {
      type: 'blood_pressure',
      value_1: sys,
      value_2: dia,
      unit,
      notes: buildNotesForSave()
    }
  } else {
    const v1 = Number(formValue1.value)
    if (!Number.isFinite(v1) || v1 <= 0) {
      uni.showToast({ title: '请输入有效数值', icon: 'none' })
      return
    }
    payload = {
      type: metricType.value,
      value_1: v1,
      unit,
      notes: buildNotesForSave()
    }
  }

  submitting.value = true
  try {
    await addHealthReading(payload)
    formVisible.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
    await loadData()
  } catch {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

function openMeasurementReminders() {
  if (metricType.value && isMonitoringMetricType(metricType.value)) {
    openReminderPanel(metricType.value)
  }
}
</script>

<style scoped>
.md-page {
  min-height: 100vh;
  background: #f5f7fa;
  box-sizing: border-box;
}

.md-scroll {
  height: 100vh;
  box-sizing: border-box;
  padding: 16px;
  padding-bottom: calc(96px + env(safe-area-inset-bottom, 0px));
}

.state-wrap {
  padding: 48px 0;
  display: flex;
  justify-content: center;
}
.state-text {
  font-size: 14px;
  color: #94a3b8;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.06);
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
}

.card-title {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.latest-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}
.latest-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.latest-icon {
  font-size: 26px;
}
.latest-body {
  flex: 1;
  min-width: 0;
}
.latest-label {
  font-size: 12px;
  color: #64748b;
  display: block;
  margin-bottom: 6px;
}
.latest-value-row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}
.latest-value {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.1;
}
.latest-unit {
  font-size: 14px;
  color: #94a3b8;
}
.latest-empty text {
  font-size: 14px;
  color: #94a3b8;
}
.latest-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.tag-pill-text {
  font-size: 12px;
  font-weight: 600;
}
.tag-normal {
  background: #f0fdf4;
}
.tag-normal .tag-pill-text {
  color: #16a34a;
}
.tag-high {
  background: #fff7ed;
}
.tag-high .tag-pill-text {
  color: #ea580c;
}
.tag-low {
  background: #eff6ff;
}
.tag-low .tag-pill-text {
  color: #2563eb;
}
.tag-muted {
  background: #f1f5f9;
}
.tag-muted .tag-pill-text {
  color: #64748b;
}
.scene-text {
  font-size: 13px;
  color: #94a3b8;
}

.chart-card {
  min-height: 320px;
}
.chart-empty {
  padding: 40px 12px;
  text-align: center;
}
.chart-empty-title {
  display: block;
  font-size: 15px;
  color: #64748b;
  margin-bottom: 6px;
}
.chart-empty-sub {
  font-size: 12px;
  color: #94a3b8;
}
.echarts-dom {
  width: 100%;
  height: 280px;
  margin-top: 8px;
}

.history-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 10px 0 4px;
}
.history-empty {
  padding: 24px 0;
  text-align: center;
}
.history-empty text {
  font-size: 14px;
  color: #94a3b8;
}
.history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid #f8fafc;
  width: 100%;
  box-sizing: border-box;
}
.history-item:last-child {
  border-bottom: none;
}
.hi-left {
  flex: 0 1 auto;
  max-width: 42%;
  min-width: 0;
}
.hi-date {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}
.hi-scene {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}
.hi-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}
.hi-value-wrap {
  width: 100%;
  text-align: right;
}
.hi-value {
  font-size: 17px;
  font-weight: 800;
  word-break: break-all;
}
.hi-row2 {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}
.hi-tag {
  display: inline-flex;
  padding: 3px 10px;
  border-radius: 20px;
}
.hi-tag-text {
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.hi-tag.tag-normal {
  background: #f0fdf4;
}
.hi-tag.tag-normal .hi-tag-text {
  color: #16a34a;
}
.hi-tag.tag-high {
  background: #fff7ed;
}
.hi-tag.tag-high .hi-tag-text {
  color: #ea580c;
}
.hi-tag.tag-low {
  background: #eff6ff;
}
.hi-tag.tag-low .hi-tag-text {
  color: #2563eb;
}
.hi-tag.tag-muted {
  background: #f1f5f9;
}
.hi-tag.tag-muted .hi-tag-text {
  color: #64748b;
}
.hi-time {
  font-size: 12px;
  color: #94a3b8;
}

.md-bottom-space {
  height: 8px;
}

.md-fab-row {
  position: fixed;
  left: 16px;
  right: 16px;
  bottom: calc(20px + env(safe-area-inset-bottom, 0px));
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  z-index: 100;
}
.fab-remind {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  color: #6366f1;
  font-size: 14px;
  font-weight: 600;
  padding: 12px 16px;
  border-radius: 24px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.1);
  border: 1px solid #e8eeff;
}
.fab-remind-icon {
  font-size: 14px;
}
.fab-add {
  background: #6366f1;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  padding: 12px 22px;
  border-radius: 24px;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 500;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.modal-card {
  width: 100%;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  padding: 20px 20px calc(20px + env(safe-area-inset-bottom, 0px));
  box-sizing: border-box;
  max-height: 85vh;
  overflow-y: auto;
}
.modal-card-reminder {
  z-index: 550;
}
.modal-title {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 16px;
  display: block;
}
.form-field {
  margin-bottom: 14px;
}
.field-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}
.field-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 0 14px;
}
.field-input {
  flex: 1;
  height: 46px;
  font-size: 16px;
  color: #1e293b;
  background: transparent;
}
.field-unit {
  font-size: 13px;
  color: #94a3b8;
}
.scene-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.scene-chip {
  padding: 6px 12px;
  border-radius: 20px;
  background: #f1f5f9;
  border: 1.5px solid transparent;
}
.scene-chip text {
  font-size: 12px;
  color: #475569;
}
.scene-chip.active {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
}
.scene-chip.active text {
  color: #6366f1;
  font-weight: 600;
}
.field-input-inline {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  font-size: 14px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-sizing: border-box;
}
.field-textarea {
  width: 100%;
  min-height: 72px;
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 14px;
  color: #1e293b;
  box-sizing: border-box;
}
.modal-btns {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}
.modal-btn {
  flex: 1;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-btn text {
  font-size: 15px;
  font-weight: 700;
}
.modal-btn.ghost {
  background: #f1f5f9;
}
.modal-btn.ghost text {
  color: #475569;
}
.modal-btn.primary {
  background: #6366f1;
}
.modal-btn.primary text {
  color: #ffffff;
}
.modal-btn.disabled {
  opacity: 0.6;
}

.time-picker-row {
  cursor: pointer;
}
.time-value {
  flex: 1;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  padding: 10px 0;
}

.freq-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.freq-chip {
  padding: 7px 14px;
  border-radius: 20px;
  background: #f1f5f9;
  border: 1.5px solid transparent;
}
.freq-chip text {
  font-size: 13px;
  color: #475569;
}
.freq-active {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
}
.freq-active text {
  color: #6366f1;
  font-weight: 600;
}
.rp-preview {
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
}
.rp-preview-label {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}
.rp-preview-text {
  font-size: 14px;
  color: #6366f1;
  font-weight: 600;
  word-break: break-word;
}

.drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: 520;
  display: flex;
  align-items: flex-end;
}
.drawer {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  padding: 0 0 env(safe-area-inset-bottom, 0px);
  max-height: 75vh;
  display: flex;
  flex-direction: column;
}
.drawer-handle {
  width: 40px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin: 12px auto 8px;
}
.drawer-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  row-gap: 10px;
  padding: 8px 20px 16px;
  gap: 14px;
  border-bottom: 1px solid #f1f5f9;
}
.rp-title-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.drawer-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}
.drawer-unit {
  font-size: 12px;
  color: #94a3b8;
}
.drawer-add-btn {
  background: #6366f1;
  border-radius: 20px;
  padding: 8px 18px;
}
.drawer-add-txt {
  font-size: 14px;
  color: #ffffff;
  font-weight: 600;
}
.drawer-history {
  flex: 1;
  overflow-y: auto;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 0 calc(20px + env(safe-area-inset-right, 0px)) 16px 20px;
}
.rp-empty {
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.rp-empty-icon {
  font-size: 36px;
}
.rp-empty-text {
  font-size: 15px;
  color: #334155;
  font-weight: 600;
}
.rp-empty-hint {
  font-size: 13px;
  color: #94a3b8;
}
.rp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
  padding: 14px 0;
  border-bottom: 1px solid #f8fafc;
}
.rp-item:last-child {
  border-bottom: none;
}
.rp-item-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}
.rp-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-active {
  background: #6366f1;
}
.dot-off {
  background: #e2e8f0;
}
.rp-item-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.rp-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  word-break: break-word;
}
.rp-item-schedule {
  font-size: 12px;
  color: #64748b;
  word-break: break-word;
}
.rp-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.rp-switch {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  position: relative;
}
.switch-on {
  background: #6366f1;
}
.switch-off {
  background: #e2e8f0;
}
.rp-switch-thumb {
  position: absolute;
  top: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}
.thumb-on {
  left: 23px;
}
.thumb-off {
  left: 3px;
}
.rp-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.edit-btn {
  background: #f0f4ff;
}
.del-btn {
  background: #fff0f0;
}
</style>
