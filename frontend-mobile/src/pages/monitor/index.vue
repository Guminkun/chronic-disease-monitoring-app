<template>
  <view class="page">
    <!-- 顶部标题 -->
    <view class="page-header">
      <text class="page-title">健康监测</text>
      <text class="page-sub">记录并追踪您的健康指标</text>
    </view>

    <!-- 未登录提示 -->
    <AuthPrompt 
      v-if="!isLoggedIn()"
      title="登录以记录健康数据"
      description="登录后可记录血糖、血压等健康指标"
      icon="❤️"
      theme="warning"
      size="medium"
    />

    <!-- 指标卡片列表 -->
    <view class="metric-list">
      <view
        v-for="m in metrics"
        :key="m.type"
        class="metric-card"
        @click="openDetail(m.type)"
      >
        <!-- 卡片主体 -->
        <view class="mc-main">
          <view class="mc-icon-wrap" :style="{ background: m.iconBg }">
            <text class="mc-emoji">{{ m.emoji }}</text>
          </view>
          <view class="mc-info">
            <text class="mc-name">{{ m.label }}</text>
            <text class="mc-latest">
              {{ latestText(m.type) !== '--' ? '最近：' + latestText(m.type) + ' ' + m.unit : '暂无记录' }}
            </text>
          </view>
          <view class="mc-right">
            <text class="mc-trend" :class="getTrendClass(m.type)">{{ getTrendArrow(m.type) }}</text>
            <text class="mc-arrow">›</text>
          </view>
        </view>

        <!-- 分隔线 -->
        <view class="mc-divider"></view>

        <!-- 底部提醒行 -->
        <view class="mc-reminder" @click.stop="openReminderPanel(m.type)">
          <text class="reminder-bell">🔔</text>
          <view class="reminder-text-wrap">
            <text class="reminder-text">测量提醒</text>
            <text v-if="getReminderSummary(m.type)" class="reminder-summary">{{ getReminderSummary(m.type) }}</text>
            <text v-else class="reminder-text-muted">未设置</text>
          </view>
          <view v-if="hasActiveReminder(m.type)" class="reminder-on-badge"><text>已开启</text></view>
          <text class="reminder-arrow">›</text>
        </view>
      </view>
    </view>

    <!-- ── 提醒管理面板 ── -->
    <view v-if="reminderPanelVisible" class="drawer-mask" @click="closeReminderPanel">
      <view class="drawer" @click.stop>
        <view class="drawer-handle"></view>
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
          <!-- 提醒列表空态 -->
          <view v-if="reminderPanelReminders.length === 0" class="rp-empty">
            <text class="rp-empty-icon">🔔</text>
            <text class="rp-empty-text">还没有设置测量提醒</text>
            <text class="rp-empty-hint">点击右上角"+ 新增"开始设置</text>
          </view>

          <!-- 提醒条目 -->
          <view v-for="item in reminderPanelReminders" :key="item.id" class="rp-item">
            <view class="rp-item-left">
              <view class="rp-dot" :class="item.is_active ? 'dot-active' : 'dot-off'"></view>
              <view class="rp-item-info">
                <text class="rp-item-title">{{ item.title }}</text>
                <text class="rp-item-schedule">{{ item.schedule_text || '未设置频率' }}</text>
              </view>
            </view>
            <view class="rp-item-actions">
              <!-- 开/关切换 -->
              <view
                class="rp-switch"
                :class="item.is_active ? 'switch-on' : 'switch-off'"
                @click="toggleReminderActive(item)"
              >
                <view class="rp-switch-thumb" :class="item.is_active ? 'thumb-on' : 'thumb-off'"></view>
              </view>
              <!-- 编辑 -->
              <view class="rp-action-btn edit-btn" @click="openReminderForm(item)">
                <text>✏️</text>
              </view>
              <!-- 删除 -->
              <view class="rp-action-btn del-btn" @click="removeReminder(item)">
                <text>🗑️</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- ── 提醒设置表单 ── -->
    <view v-if="reminderFormVisible" class="modal-mask" @click="closeReminderForm">
      <view class="modal-card" @click.stop>
        <view class="modal-title">{{ reminderEditTarget ? '编辑提醒' : '新增提醒' }}</view>

        <!-- 频率选择 -->
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

        <!-- 时间选择 -->
        <view class="form-field">
          <text class="field-label">提醒时间</text>
          <picker mode="time" :value="reminderFormTime" @change="(e: any) => reminderFormTime = e.detail.value">
            <view class="field-input-row time-picker-row">
              <text class="time-value">{{ reminderFormTime }}</text>
              <text class="field-unit">点提醒</text>
            </view>
          </picker>
        </view>

        <view class="rp-preview">
          <text class="rp-preview-label">提醒预览</text>
          <text class="rp-preview-text">{{ metricTypeLabel[reminderType] }}测量提醒 · {{ reminderFormFreq }} {{ reminderFormTime }}</text>
        </view>

        <view class="modal-btns">
          <view class="modal-btn ghost" @click="closeReminderForm"><text>取消</text></view>
          <view class="modal-btn primary" :class="{ disabled: reminderFormSaving }" @click="saveReminder">
            <text>{{ reminderFormSaving ? '保存中...' : '保存提醒' }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="2" />
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getHealthReadings } from '@/api/patient'
import { useMeasurementReminders, type MonitoringMetricType } from '@/composables/useMeasurementReminders'
import { isLoggedIn, checkLoginWithRedirect } from '@/utils/auth'
import AuthPrompt from '@/components/AuthPrompt.vue'
import CustomTabBar from '@/components/tabbar/CustomTabBar.vue'

type MetricType = MonitoringMetricType

type ReadingLite = {
  value_1: number
  value_2?: number | null
  recorded_at: string
}

const metrics = [
  { type: 'blood_sugar'    as const, label: '血糖', unit: 'mmol/L', emoji: '💧', iconBg: 'linear-gradient(135deg,#fb923c,#f97316)' },
  { type: 'blood_pressure' as const, label: '血压', unit: 'mmHg',   emoji: '❤️', iconBg: 'linear-gradient(135deg,#60a5fa,#3b82f6)' },
  { type: 'heart_rate'     as const, label: '心率', unit: '次/分',  emoji: '📈', iconBg: 'linear-gradient(135deg,#4ade80,#22c55e)' },
  { type: 'weight'         as const, label: '体重', unit: 'kg',     emoji: '⚖️', iconBg: 'linear-gradient(135deg,#c084fc,#a855f7)' },
  { type: 'blood_lipids'   as const, label: '血脂', unit: 'mmol/L', emoji: '🩸', iconBg: 'linear-gradient(135deg,#fbbf24,#f59e0b)' },
  { type: 'uric_acid'      as const, label: '尿酸', unit: 'μmol/L', emoji: '🧪', iconBg: 'linear-gradient(135deg,#818cf8,#6366f1)' },
]

const readingsMap = ref<Record<MetricType, ReadingLite[]>>({
  blood_pressure: [], blood_sugar: [], heart_rate: [],
  weight: [], blood_lipids: [], uric_acid: []
})

const loading = ref(false)

const fetchType = async (type: MetricType) => {
  if (!isLoggedIn()) {
    readingsMap.value[type] = []
    return
  }
  try {
    const res: any = await getHealthReadings(type)
    readingsMap.value[type] = Array.isArray(res) ? res : []
  } catch {
    readingsMap.value[type] = []
  }
}

const reloadAll = async () => {
  if (!isLoggedIn()) return
  loading.value = true
  await Promise.all(metrics.map(m => fetchType(m.type)))
  loading.value = false
}

const latestText = (type: MetricType) => {
  const arr = readingsMap.value[type]
  const last = arr?.[arr.length - 1]
  if (!last) return '--'
  if (type === 'blood_pressure') {
    return last.value_2 != null ? `${last.value_1}/${last.value_2}` : `${last.value_1}`
  }
  return `${last.value_1}`
}

const getTrendClass = (type: MetricType) => {
  const arr = readingsMap.value[type]
  if (arr.length < 2) return 'trend-flat'
  const delta = Number(arr[arr.length - 1].value_1) - Number(arr[arr.length - 2].value_1)
  if (delta > 0) return 'trend-up'
  if (delta < 0) return 'trend-down'
  return 'trend-flat'
}

const getTrendArrow = (type: MetricType) => {
  const arr = readingsMap.value[type]
  if (arr.length < 2) return ''
  const delta = Number(arr[arr.length - 1].value_1) - Number(arr[arr.length - 2].value_1)
  if (delta > 0) return '↗'
  if (delta < 0) return '↘'
  return '→'
}

const openDetail = (type: MetricType) => {
  if (!checkLoginWithRedirect('/pages/monitor/index')) return
  uni.navigateTo({ url: `/pages/monitor/metric-detail?type=${type}` })
}

const {
  metricTypeLabel,
  loadReminders,
  hasActiveReminder,
  getReminderSummary,
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

onShow(async () => { await Promise.all([reloadAll(), loadReminders()]) })
</script>

<style>
/* ── 页面基础 ── */
.page {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  padding-bottom: 120rpx;
}

/* ── 顶部标题 ── */
.page-header {
  padding: 56rpx 32rpx 24rpx;
  background-color: var(--color-bg-elevated);
  border-bottom: 1rpx solid var(--color-bg-muted);
}
.page-title {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 2px;
}
.page-sub {
  display: block;
  font-size: 13px;
  color: #94a3b8;
}

/* ── 登录引导卡片 ── */

/* ── 指标列表 ── */
.metric-list {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── 指标卡片 ── */
.metric-card {
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  position: relative;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.6));
}

.mc-main {
  display: flex;
  align-items: center;
  padding: 16px 16px 14px;
  gap: 14px;
}

.mc-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.mc-emoji { font-size: 24px; }

.mc-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.mc-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}
.mc-latest {
  font-size: 13px;
  color: #64748b;
}

.mc-right {
  display: flex;
  align-items: center;
  gap: 6px;
}
.mc-trend {
  font-size: 18px;
  font-weight: 700;
}
.trend-up   { color: #ef4444; }
.trend-down { color: #22c55e; }
.trend-flat { color: #94a3b8; }
.mc-arrow {
  font-size: 20px;
  color: #cbd5e1;
}

.mc-divider {
  height: 1px;
  background: #f1f5f9;
  margin: 0 16px;
}

.mc-reminder {
  display: flex;
  align-items: center;
  padding: 11px 16px;
  gap: 8px;
}
.reminder-bell { font-size: 14px; }
.reminder-text-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.reminder-text {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}
.reminder-summary {
  font-size: 11px;
  color: #6366f1;
  word-break: break-word;
  overflow-wrap: anywhere;
}
.reminder-text-muted {
  font-size: 11px;
  color: #94a3b8;
}
.reminder-on-badge {
  background: rgba(99,102,241,0.1);
  border-radius: 10px;
  padding: 2px 8px;
}
.reminder-on-badge text {
  font-size: 11px;
  color: #6366f1;
  font-weight: 600;
}
.reminder-arrow {
  font-size: 16px;
  color: #cbd5e1;
}

/* ── 提醒管理面板 ── */
.rp-title-wrap { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }

.rp-empty {
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.rp-empty-icon { font-size: 36px; }
.rp-empty-text { font-size: 15px; color: #334155; font-weight: 600; }
.rp-empty-hint { font-size: 13px; color: #94a3b8; }

.rp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-width: 0;
  padding: 14px 0;
  border-bottom: 1px solid #f8fafc;
}
.rp-item:last-child { border-bottom: none; }
.rp-item-left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.rp-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-active { background: #6366f1; }
.dot-off { background: #e2e8f0; }
.rp-item-info { display: flex; flex-direction: column; gap: 3px; }
.rp-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  word-break: break-word;
  overflow-wrap: anywhere;
}
.rp-item-schedule {
  font-size: 12px;
  color: #64748b;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.rp-item-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }

/* toggle switch */
.rp-switch {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  position: relative;
  transition: background 0.2s;
}
.switch-on { background: #6366f1; }
.switch-off { background: #e2e8f0; }
.rp-switch-thumb {
  position: absolute;
  top: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  transition: left 0.2s;
}
.thumb-on { left: 23px; }
.thumb-off { left: 3px; }

.rp-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.edit-btn { background: #f0f4ff; }
.del-btn { background: #fff0f0; }

/* ── 提醒表单 ── */
.freq-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 2px;
}
.freq-chip {
  padding: 7px 14px;
  border-radius: 20px;
  background: #f1f5f9;
  border: 1.5px solid transparent;
}
.freq-chip text { font-size: 13px; color: #475569; }
.freq-active { background: rgba(99,102,241,0.1); border-color: #6366f1; }
.freq-active text { color: #6366f1; font-weight: 600; }

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

.rp-preview {
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
}
.rp-preview-label { display: block; font-size: 11px; color: #94a3b8; margin-bottom: 4px; }
.rp-preview-text {
  font-size: 14px;
  color: #6366f1;
  font-weight: 600;
  word-break: break-word;
  overflow-wrap: anywhere;
}

/* ── 详情抽屉 ── */
.drawer-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15,23,42,0.4);
  z-index: 500;
  display: flex;
  align-items: flex-end;
}
.drawer {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  padding: 0 0 env(safe-area-inset-bottom);
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
.drawer-title { font-size: 18px; font-weight: 700; color: #1e293b; }
.drawer-unit { font-size: 12px; color: #94a3b8; }
.drawer-add-btn {
  background: #6366f1;
  border-radius: 20px;
  padding: 8px 18px;
}
.drawer-add-txt { font-size: 14px; color: #ffffff; font-weight: 600; }

.drawer-history {
  flex: 1;
  overflow-y: auto;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  /* 右侧略增内边距，避免贴边裁切（含安全区） */
  padding: 0 calc(20px + env(safe-area-inset-right, 0px)) 16px 20px;
}

/* ── 记录表单弹层 ── */
.modal-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15,23,42,0.45);
  z-index: 600;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.modal-card {
  width: 100%;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  padding: 20px 20px calc(20px + env(safe-area-inset-bottom));
}
.modal-title {
  font-size: 18px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 18px;
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
.field-unit { font-size: 13px; color: #94a3b8; }
.field-textarea {
  width: 100%;
  min-height: 80px;
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
  margin-top: 20px;
}
.modal-btn {
  flex: 1;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-btn text { font-size: 15px; font-weight: 700; }
.modal-btn.ghost { background: #f1f5f9; }
.modal-btn.ghost text { color: #475569; }
.modal-btn.primary { background: #6366f1; }
.modal-btn.primary text { color: #ffffff; }
.modal-btn.disabled { opacity: 0.6; }
</style>
