<template>
  <view class="container">
    <view class="header">
      <text class="title">今日待办</text>
      <text class="subtitle">让健康管理成为习惯</text>
    </view>

    <view class="date-bar">
      <text class="date-text">{{ today }}</text>
      <text class="week-text">{{ weekDay }}</text>
    </view>

    <!-- 今日用药模块 -->
    <view class="med-card" @click="goToMedication">
      <view class="mc-header">
        <view class="mc-icon">
          <text style="font-size: 22px;">💊</text>
        </view>
        <view class="mc-info">
          <text class="mc-title">今日用药</text>
          <text class="mc-subtitle">已完成 {{ todayStats.completed }}/{{ todayStats.total }}</text>
        </view>
        <view class="mc-action">
          <text class="mc-action-text">查看</text>
          <text class="arrow-right">›</text>
        </view>
      </view>

      <view class="mc-progress-bg">
        <view class="mc-progress-bar" :style="{ width: `${todayStats.percent}%` }"></view>
      </view>

      <view class="mc-chips">
        <view
          v-for="(task, idx) in dailyTasks"
          :key="'med-' + task.plan_id + '-' + (task.scheduled_time || idx)"
          class="mc-chip"
        >
          <view class="mc-chip-main">
            <text class="mc-time">{{ formatTime(task.scheduled_time) }}</text>
            <text class="mc-name">{{ task.plan_name }}</text>
            <text class="mc-status" :class="medStatusClass(task.status)">{{ medStatusText(task.status) }}</text>
          </view>
          <text v-if="medTaskSubline(task)" class="mc-chip-sub">{{ medTaskSubline(task) }}</text>
        </view>
        <view v-if="dailyTasks.length === 0" class="mc-empty">
          <text>今日暂无用药计划</text>
        </view>
      </view>
    </view>

    <!-- 监测任务 -->
    <view class="task-section">
      <view class="section-head">
        <view class="title-left">
          <text class="icon">🩺</text>
          <text class="section-label">监测任务</text>
        </view>
        <view class="section-action" @click="goToMonitor">
          <text class="section-action-text">管理提醒</text>
          <text class="arrow-right">›</text>
        </view>
      </view>

      <view class="task-list">
        <!-- 动态提醒列表 -->
        <view
          v-for="item in activeMonitorReminders"
          :key="item.id"
          class="task-card"
          @click="goToMonitor"
        >
          <view class="check-circle" :class="{ 'circle-active': item.is_active }">
            <text v-if="item.is_active" class="check-mark">✓</text>
          </view>
          <view class="task-info">
            <text class="task-name">{{ item.title }}</text>
            <text class="task-time">{{ item.schedule_text || '定时提醒' }}</text>
          </view>
          <view class="task-badge" :class="item.is_active ? 'badge-on' : 'badge-off'">
            <text>{{ item.is_active ? '已开启' : '已关闭' }}</text>
          </view>
        </view>

        <!-- 空态 -->
        <view v-if="activeMonitorReminders.length === 0" class="monitor-empty-card">
          <text class="monitor-empty-icon">🔔</text>
          <view class="monitor-empty-info">
            <text class="monitor-empty-text">暂无监测提醒</text>
            <text class="monitor-empty-hint">前往"监测"页面设置提醒</text>
          </view>
          <view class="monitor-set-btn" @click="goToMonitor">
            <text>去设置</text>
          </view>
        </view>
      </view>
    </view>

    <view class="empty-tip">
      <text>暂无更多待办任务</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { getDailyTasks } from '@/api/medication'
import { getPatientReminders } from '@/api/patient'

const userStore = useUserStore()
const dailyTasks = ref<any[]>([])
const monitorReminders = ref<any[]>([])

const now = new Date()
const today = computed(() => `${now.getMonth() + 1}月${now.getDate()}日`)
const weekDay = computed(() => {
  const weeks = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weeks[now.getDay()]
})

const todayStats = computed(() => {
  const total = dailyTasks.value.length
  const completed = dailyTasks.value.filter(t => t.status === 'taken').length
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0
  return { total, completed, percent }
})

const medStatusText = (status: string) => {
  if (status === 'taken') return '已服'
  if (status === 'skipped') return '已跳过'
  return '待服'
}
const medStatusClass = (status: string) => {
  if (status === 'taken') return 'mc-status-done'
  if (status === 'skipped') return 'mc-status-skip'
  return 'mc-status-pending'
}

const medTaskSubline = (task: Record<string, any>) => {
  const parts: string[] = []
  if (task.dosage) parts.push(String(task.dosage))
  if (task.timing) parts.push(String(task.timing))
  if (task.status === 'taken' && task.taken_time) {
    parts.push(`实际服用 ${formatTime(task.taken_time)}`)
  }
  return parts.length ? parts.join(' · ') : ''
}

// 只显示 type=recheck 的监测提醒
const activeMonitorReminders = computed(() =>
  monitorReminders.value.filter(r => r.type === 'recheck')
)

const formatTime = (isoStr: string) => {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const goToMedication = () => {
  if (!userStore.token) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }
  uni.navigateTo({ url: '/pages/medication/index' })
}

const goToMonitor = () => {
  if (!userStore.token) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }
  uni.switchTab({ url: '/pages/monitor/index' })
}

const loadMedication = async () => {
  if (!userStore.token) { dailyTasks.value = []; return }
  try {
    const todayStr = new Date().toISOString().split('T')[0]
    const res = await getDailyTasks(todayStr)
    dailyTasks.value = res as any
  } catch {
    dailyTasks.value = []
  }
}

const loadMonitorReminders = async () => {
  if (!userStore.token) { monitorReminders.value = []; return }
  try {
    const res: any = await getPatientReminders()
    monitorReminders.value = Array.isArray(res) ? res : []
  } catch {
    monitorReminders.value = []
  }
}

onShow(() => {
  loadMedication()
  loadMonitorReminders()
})
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 16px;
  padding-bottom: 80px;
}

.header {
  margin: 16px 4px 24px;
}
.title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
  display: block;
}
.subtitle {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

.date-bar {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 20px;
  padding: 0 4px;
}
.date-text {
  font-size: 28px;
  font-weight: bold;
  color: #3b82f6;
}
.week-text {
  font-size: 16px;
  color: #64748b;
}

/* 今日用药卡片 */
.med-card {
  background: white;
  margin-bottom: 20px;
  padding: 16px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.mc-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.mc-icon {
  width: 40px;
  height: 40px;
  background: #3b82f6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}
.mc-info { flex: 1; min-width: 0; }
.mc-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  display: block;
}
.mc-subtitle {
  font-size: 12px;
  color: #64748b;
}
.mc-action {
  display: flex;
  align-items: center;
  gap: 4px;
}
.mc-action-text {
  color: #3b82f6;
  font-size: 13px;
}
.arrow-right { font-size: 12px; color: #3b82f6; }
.mc-progress-bg {
  height: 6px;
  background: #eff6ff;
  border-radius: 3px;
  margin-bottom: 16px;
  overflow: hidden;
}
.mc-progress-bar {
  height: 100%;
  background: #3b82f6;
  border-radius: 3px;
  transition: width 0.3s;
}
.mc-chips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mc-chip {
  background: #f1f5f9;
  padding: 8px 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 4px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.mc-chip-main {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 10px;
  width: 100%;
  min-width: 0;
}
.mc-chip-sub {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: break-word;
}
.mc-time {
  color: #3b82f6;
  font-weight: 600;
  font-size: 12px;
  flex-shrink: 0;
}
.mc-name {
  color: #64748b;
  font-size: 12px;
  flex: 1;
  min-width: 0;
  word-break: break-word;
  overflow-wrap: break-word;
}
.mc-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}
.mc-status-pending { background: #dbeafe; color: #1d4ed8; }
.mc-status-done { background: #dcfce7; color: #15803d; }
.mc-status-skip { background: #f1f5f9; color: #64748b; }
.mc-empty { font-size: 12px; color: #94a3b8; padding: 8px 0; }

/* 监测任务 */
.task-section { margin-bottom: 24px; }
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 4px;
}
.title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.icon { font-size: 18px; }
.section-label {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}
.section-action {
  display: flex;
  align-items: center;
  gap: 2px;
}
.section-action-text {
  font-size: 13px;
  color: #6366f1;
}
.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.task-card {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-width: 0;
}
.check-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.circle-active {
  background: #6366f1;
  border-color: #6366f1;
}
.check-mark {
  font-size: 13px;
  color: #ffffff;
  font-weight: 700;
}
.task-info { flex: 1; min-width: 0; }
.task-name {
  font-size: 15px;
  color: #334155;
  font-weight: 500;
  display: block;
  word-break: break-word;
  overflow-wrap: break-word;
}
.task-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 3px;
  display: block;
  word-break: break-word;
  overflow-wrap: break-word;
}
.task-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  flex-shrink: 0;
}
.task-badge text { font-size: 11px; font-weight: 500; }
.badge-on { background: rgba(99,102,241,0.1); }
.badge-on text { color: #6366f1; }
.badge-off { background: #f1f5f9; }
.badge-off text { color: #94a3b8; }

/* 监测空态卡片 */
.monitor-empty-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.monitor-empty-icon { font-size: 28px; }
.monitor-empty-info { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.monitor-empty-text { font-size: 14px; color: #475569; font-weight: 500; }
.monitor-empty-hint { font-size: 12px; color: #94a3b8; }
.monitor-set-btn {
  background: #6366f1;
  border-radius: 16px;
  padding: 7px 14px;
}
.monitor-set-btn text { font-size: 12px; color: #ffffff; font-weight: 600; }

.empty-tip {
  text-align: center;
  color: #cbd5e1;
  font-size: 14px;
  margin-top: 40px;
}
</style>