<template>
  <view class="page">
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="title">漏服补卡</text>
      <view class="placeholder"></view>
    </view>

    <scroll-view scroll-y class="scroll">
      <view class="date-section">
        <text class="section-title">选择补卡日期</text>
        <view class="date-list">
          <view 
            v-for="item in availableDates" 
            :key="item.value" 
            class="date-item"
            :class="{ active: selectedDate === item.value, disabled: item.disabled }"
            @click="!item.disabled && selectDate(item.value)"
          >
            <text class="date-label">{{ item.label }}</text>
            <text class="date-value">{{ item.dateStr }}</text>
          </view>
        </view>
      </view>

      <view v-if="selectedDate" class="tasks-section">
        <view class="section-head">
          <text class="section-title">漏服药物</text>
          <text class="section-sub">{{ selectedDate }} 的漏服记录</text>
        </view>

        <view v-if="loading" class="loading">
          <text>加载中...</text>
        </view>

        <view v-else-if="tasks.length === 0" class="empty">
          <text class="empty-icon">📋</text>
          <text class="empty-text">该日期无漏服记录</text>
        </view>

        <view v-else>
          <view 
            v-for="task in tasks" 
            :key="taskKey(task)" 
            class="task-card"
            :class="{ selected: selectedTask?.plan_id === task.plan_id && selectedTask?.scheduled_time === task.scheduled_time, makeup_done: task.is_makeup_done }"
            @click="!task.is_makeup_done && selectTask(task)"
          >
            <view class="task-icon">
              <text class="task-emoji">💊</text>
            </view>
            <view class="task-main">
              <text class="task-name">{{ task.plan_name }}</text>
              <text class="task-sub">{{ task.dosage }} · {{ formatTime(task.scheduled_time) }}</text>
            </view>
            <view v-if="task.is_makeup_done" class="makeup-badge done">
              <text>已补卡</text>
            </view>
            <view v-else class="check-icon" :class="{ checked: selectedTask?.plan_id === task.plan_id }">
              <text>{{ selectedTask?.plan_id === task.plan_id ? '✓' : '' }}</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="selectedTask" class="reason-section">
        <text class="section-title">补卡原因</text>
        <text class="required-hint">（必选）</text>
        
        <view class="reason-list">
          <view 
            v-for="reason in reasons" 
            :key="reason.value" 
            class="reason-item"
            :class="{ active: selectedReason === reason.value }"
            @click="selectReason(reason.value)"
          >
            <view class="radio-circle">
              <view v-if="selectedReason === reason.value" class="radio-dot"></view>
            </view>
            <text class="reason-label">{{ reason.label }}</text>
          </view>
        </view>

        <view v-if="selectedReason === 'other'" class="note-input">
          <text class="input-label">补充说明</text>
          <textarea 
            v-model="makeupNote" 
            class="note-textarea"
            placeholder="请输入漏服原因说明..."
            maxlength="200"
          />
        </view>
      </view>

      <view style="height: 120px;"></view>
    </scroll-view>

    <view class="bottom-bar">
      <view 
        class="submit-btn" 
        :class="{ disabled: !canSubmit }"
        @click="canSubmit && handleSubmit()"
      >
        <text class="submit-text">{{ submitting ? '提交中...' : '确认补卡' }}</text>
      </view>
    </view>

    <view v-if="successVisible" class="success-overlay">
      <view class="success-card">
        <text class="success-icon">✅</text>
        <text class="success-title">补卡成功</text>
        <text class="success-desc">您的漏服记录已补录，请按时服药保持健康</text>
        <view class="success-btn" @click="closeSuccess">
          <text>好的</text>
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

import { ref, computed, onMounted } from 'vue'
import * as medApi from '@/api/medication'

interface Task {
  plan_id: number
  plan_name: string
  dosage: string
  scheduled_time: string
  date_str: string
  is_makeup_done: boolean
}

const availableDates = ref<any[]>([])
const selectedDate = ref('')
const tasks = ref<Task[]>([])
const selectedTask = ref<Task | null>(null)
const reasons = ref<any[]>([])
const selectedReason = ref('')
const makeupNote = ref('')
const loading = ref(false)
const submitting = ref(false)
const successVisible = ref(false)

onMounted(() => {
  loadReasons()
  initAvailableDates()
})

const loadReasons = async () => {
  try {
    const res: any = await medApi.getMakeupReasons()
    reasons.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    reasons.value = [
      { value: 'forgot', label: '忘记服药' },
      { value: 'discomfort', label: '身体不适' },
      { value: 'shortage', label: '药品不足' },
      { value: 'other', label: '其他原因' }
    ]
  }
}

const initAvailableDates = () => {
  const today = new Date()
  const dates = []
  for (let i = 1; i <= 3; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][d.getDay()]
    dates.push({
      value: dateStr,
      label: i === 1 ? '昨天' : i === 2 ? '前天' : '3天前',
      dateStr: `${d.getMonth() + 1}月${d.getDate()}日 ${weekDay}`,
      disabled: false
    })
  }
  availableDates.value = dates
}

const selectDate = async (date: string) => {
  selectedDate.value = date
  selectedTask.value = null
  selectedReason.value = ''
  makeupNote.value = ''
  await loadTasks()
}

const loadTasks = async () => {
  if (!selectedDate.value) return
  
  loading.value = true
  try {
    const res: any = await medApi.getAvailableMakeupTasks(selectedDate.value)
    tasks.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const selectTask = (task: Task) => {
  if (task.is_makeup_done) return
  selectedTask.value = task
}

const selectReason = (reason: string) => {
  selectedReason.value = reason
  if (reason !== 'other') {
    makeupNote.value = ''
  }
}

const taskKey = (task: Task) => `${task.plan_id}-${task.scheduled_time}`

const formatTime = (isoStr: string) => {
  if (!isoStr) return '--:--'
  try {
    return new Date(isoStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '--:--'
  }
}

const canSubmit = computed(() => {
  return selectedTask.value && selectedReason.value && !submitting.value
})

const handleSubmit = async () => {
  if (!canSubmit.value) return
  
  submitting.value = true
  try {
    await medApi.createMakeup({
      plan_id: selectedTask.value!.plan_id,
      scheduled_time: selectedTask.value!.scheduled_time,
      makeup_reason: selectedReason.value,
      makeup_note: selectedReason.value === 'other' ? makeupNote.value : undefined
    })
    successVisible.value = true
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || '补卡失败'
    uni.showToast({ title: msg, icon: 'none' })
  } finally {
    submitting.value = false
  }
}

const closeSuccess = () => {
  successVisible.value = false
  loadTasks()
}

</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #eef2f7;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.back-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 28px;
  color: #0f172a;
  font-weight: 300;
}

.title {
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
}

.placeholder {
  width: 36px;
}

.scroll {
  flex: 1;
  padding: 20px;
  box-sizing: border-box;
}

.date-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 900;
  color: #0f172a;
}

.section-sub {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
  margin-left: 8px;
}

.section-head {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.date-list {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.date-item {
  flex: 1;
  background: #ffffff;
  border-radius: 14px;
  padding: 14px 10px;
  text-align: center;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.date-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.date-item.disabled {
  opacity: 0.5;
}

.date-label {
  display: block;
  font-size: 14px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 4px;
}

.date-value {
  display: block;
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.tasks-section {
  margin-bottom: 24px;
}

.loading, .empty {
  padding: 40px 0;
  text-align: center;
}

.empty-icon {
  display: block;
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 600;
}

.task-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  border: 2px solid transparent;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.task-card.selected {
  border-color: #2563eb;
  background: #eff6ff;
}

.task-card.makeup_done {
  opacity: 0.6;
}

.task-icon {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 44px;
}

.task-emoji {
  font-size: 22px;
  line-height: 1;
}

.task-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  font-size: 15px;
  font-weight: 900;
  color: #0f172a;
}

.task-sub {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.makeup-badge {
  height: 26px;
  padding: 0 12px;
  border-radius: 13px;
  background: rgba(22, 163, 74, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
}

.makeup-badge done {
  background: rgba(22, 163, 74, 0.14);
}

.makeup-badge text {
  font-size: 12px;
  font-weight: 900;
  color: #16a34a;
}

.check-icon {
  width: 24px;
  height: 24px;
  border-radius: 12px;
  border: 2px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon.checked {
  background: #2563eb;
  border-color: #2563eb;
}

.check-icon text {
  font-size: 14px;
  color: #ffffff;
  font-weight: 900;
}

.reason-section {
  background: #ffffff;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}

.required-hint {
  font-size: 13px;
  color: #ef4444;
  font-weight: 600;
}

.reason-list {
  margin-top: 16px;
}

.reason-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

.reason-item:last-child {
  border-bottom: none;
}

.radio-circle {
  width: 22px;
  height: 22px;
  border-radius: 11px;
  border: 2px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 22px;
}

.reason-item.active .radio-circle {
  border-color: #2563eb;
}

.radio-dot {
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background: #2563eb;
}

.reason-label {
  font-size: 15px;
  color: #0f172a;
  font-weight: 700;
}

.note-input {
  margin-top: 16px;
}

.input-label {
  display: block;
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 10px;
}

.note-textarea {
  width: 100%;
  height: 100px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
  color: #0f172a;
  box-sizing: border-box;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  background: #ffffff;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
  padding-bottom: calc(16px + constant(safe-area-inset-bottom));
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.submit-btn {
  height: 52px;
  border-radius: 26px;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.submit-btn.disabled {
  background: #cbd5e1;
}

.submit-text {
  font-size: 16px;
  font-weight: 900;
  color: #ffffff;
}

.success-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 24px;
  box-sizing: border-box;
}

.success-card {
  width: 100%;
  max-width: 340px;
  background: #ffffff;
  border-radius: 24px;
  padding: 32px 24px;
  text-align: center;
  box-sizing: border-box;
}

.success-icon {
  display: block;
  font-size: 56px;
  margin-bottom: 16px;
}

.success-title {
  display: block;
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 10px;
}

.success-desc {
  display: block;
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  line-height: 1.5;
  margin-bottom: 24px;
}

.success-btn {
  height: 48px;
  border-radius: 24px;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-btn text {
  font-size: 16px;
  font-weight: 900;
  color: #ffffff;
}
</style>
