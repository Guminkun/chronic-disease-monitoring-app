<template>
  <view class="container">
    <view class="header-card">
      <view class="header-content">
        <text class="title">复诊计划</text>
        <text class="subtitle">科学管理复诊周期，守护长期健康</text>
      </view>
      <view class="add-btn" @click="showAddModal">
        <text class="btn-text">+ 新增计划</text>
      </view>
    </view>

    <!-- Tabs -->
    <view class="tab-bar">
      <view class="tab-item" :class="{ active: activeTab === 0 }" @click="activeTab = 0">
        <text>进行中</text>
        <view class="tab-line" v-if="activeTab === 0"></view>
      </view>
      <view class="tab-item" :class="{ active: activeTab === 1 }" @click="loadHistory">
        <text>历史记录</text>
        <view class="tab-line" v-if="activeTab === 1"></view>
      </view>
    </view>

    <!-- Active Plans -->
    <view class="plan-list" v-if="activeTab === 0">
      <view class="plan-card" v-for="plan in plans" :key="plan.id" @click="editPlan(plan)">
        <view class="card-left">
          <view class="disease-tag-wrapper">
            <view class="disease-badge" :class="getDiseaseClass(plan.patient_disease?.name)">
              <view class="badge-dot"></view>
              <text class="badge-text">{{ plan.patient_disease?.name || '通用' }}</text>
            </view>
          </view>
          <view class="cycle-info">
            <text class="cycle-label">复诊周期：</text>
            <text class="cycle-value">{{ formatCycle(plan) }}</text>
          </view>
          <view class="next-date">
            <text class="label">下次复诊：</text>
            <text class="value highlight">{{ plan.next_date }}</text>
            <text class="days-left" :class="getDaysLeftClass(plan.next_date)">
              {{ getDaysLeft(plan.next_date) }}
            </text>
          </view>
        </view>
        <view class="card-action" @click.stop="checkIn(plan)">
          <text class="check-btn">打卡</text>
        </view>
      </view>
      
      <view class="empty-state" v-if="plans.length === 0">
        <text class="empty-text">暂无复诊计划，点击上方按钮添加</text>
      </view>
    </view>

    <!-- History Records -->
    <view class="history-list" v-if="activeTab === 1">
      <view class="history-card" v-for="rec in records" :key="rec.id">
        <view class="history-left">
          <text class="history-date">{{ rec.actual_date }}</text>
          <text class="history-plan" v-if="rec.plan">
            {{ rec.plan.patient_disease?.name || '通用' }} · {{ formatCycle(rec.plan) }}
          </text>
          <text class="history-notes" v-if="rec.notes">备注：{{ rec.notes }}</text>
        </view>
        <view class="history-right">
          <text class="status-text">已完成</text>
        </view>
      </view>
      
      <view class="empty-state" v-if="records.length === 0">
        <text class="empty-text">暂无历史记录</text>
      </view>
    </view>

    <!-- Add/Edit Modal -->
    <view class="modal-mask" v-if="showModal" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ isEditing ? '编辑计划' : '新增复诊计划' }}</text>
          <text class="close-icon" @click="closeModal">×</text>
        </view>
        
        <view class="form-item">
          <text class="label">关联疾病</text>
          <picker :range="diseaseList" range-key="name" @change="onDiseaseChange">
            <view class="picker-box">
              <text v-if="form.patient_disease_id">
                {{ getDiseaseName(form.patient_disease_id) }}
              </text>
              <text v-else class="placeholder">请选择关联疾病（可选）</text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">复诊周期</text>
          <view class="cycle-options">
            <view 
              class="cycle-opt" 
              :class="{ active: form.cycle_type === 'week' }"
              @click="setCycle('week')"
            >1周</view>
            <view 
              class="cycle-opt" 
              :class="{ active: form.cycle_type === 'month' }"
              @click="setCycle('month')"
            >1个月</view>
            <view 
              class="cycle-opt" 
              :class="{ active: form.cycle_type === 'quarter' }"
              @click="setCycle('quarter')"
            >1季度</view>
            <view 
              class="cycle-opt" 
              :class="{ active: form.cycle_type === 'year' }"
              @click="setCycle('year')"
            >1年</view>
             <view 
              class="cycle-opt" 
              :class="{ active: form.cycle_type === 'custom' }"
              @click="setCycle('custom')"
            >自定义</view>
          </view>
        </view>

        <view class="form-item" v-if="form.cycle_type === 'custom'">
           <text class="label">自定义天数</text>
           <input type="number" class="input" v-model="form.custom_days" placeholder="请输入间隔天数" />
        </view>

        <view class="form-item">
          <text class="label">下次复诊日期</text>
          <picker mode="date" :value="form.next_date" @change="onDateChange">
            <view class="picker-box">
              <text>{{ form.next_date || '请选择日期' }}</text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">备注</text>
          <textarea class="textarea" v-model="form.notes" placeholder="例如：需空腹抽血..." />
        </view>

        <view class="modal-footer">
          <button class="btn-cancel" @click="isEditing ? handleDelete() : closeModal()">
             {{ isEditing ? '删除计划' : '取消' }}
          </button>
          <button class="btn-save" @click="handleSave">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { 
  getDiseases, 
  getRevisitPlans, 
  addRevisitPlan, 
  updateRevisitPlan, 
  deleteRevisitPlan,
  getRevisitRecords,
  addRevisitRecord
} from '@/api/patient'

const activeTab = ref(0)
const plans = ref<any[]>([])
const records = ref<any[]>([])
const diseaseList = ref<any[]>([])
const showModal = ref(false)
const isEditing = ref(false)

const form = ref({
  id: 0,
  patient_disease_id: 0,
  cycle_type: 'month',
  cycle_value: 1,
  custom_days: '',
  next_date: '',
  notes: ''
})

const getDiseaseClass = (name: string) => {
  if (!name) return 'bg-gray'
  if (name.includes('高血压')) return 'bg-blue'
  if (name.includes('糖尿病')) return 'bg-orange'
  return 'bg-green'
}

const getDiseaseName = (id: number) => {
  const d = diseaseList.value.find(item => item.id === id)
  return d ? d.name : ''
}

const formatCycle = (plan: any) => {
  const map: any = {
    week: '每 1 周',
    month: '每 1 个月',
    quarter: '每 1 季度',
    year: '每 1 年',
    custom: `每 ${plan.cycle_value} 天`
  }
  if (plan.cycle_type === 'custom') return `每 ${plan.cycle_value} 天`
  return map[plan.cycle_type] || plan.cycle_type
}

const getDaysLeft = (dateStr: string) => {
  const target = new Date(dateStr).getTime()
  const now = new Date().setHours(0,0,0,0)
  const diff = Math.ceil((target - now) / (1000 * 3600 * 24))
  if (diff < 0) return '已逾期'
  if (diff === 0) return '今天'
  return `还有 ${diff} 天`
}

const getDaysLeftClass = (dateStr: string) => {
  const target = new Date(dateStr).getTime()
  const now = new Date().setHours(0,0,0,0)
  const diff = Math.ceil((target - now) / (1000 * 3600 * 24))
  if (diff < 0) return 'text-red'
  if (diff <= 3) return 'text-orange'
  return 'text-gray'
}

const loadData = async () => {
  try {
    const [dRes, pRes]: any = await Promise.all([getDiseases(), getRevisitPlans()])
    diseaseList.value = Array.isArray(dRes) ? dRes : (dRes?.data || [])
    plans.value = Array.isArray(pRes) ? pRes : (pRes?.data || [])
  } catch (e) {
    console.error(e)
  }
}

const loadHistory = async () => {
  activeTab.value = 1
  try {
    const res: any = await getRevisitRecords()
    records.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error(e)
  }
}

const showAddModal = () => {
  isEditing.value = false
  const today = new Date()
  const nextMonth = new Date(today.setMonth(today.getMonth() + 1))
  
  form.value = {
    id: 0,
    patient_disease_id: 0,
    cycle_type: 'month',
    cycle_value: 1,
    custom_days: '',
    next_date: nextMonth.toISOString().split('T')[0],
    notes: ''
  }
  showModal.value = true
}

const editPlan = (plan: any) => {
  isEditing.value = true
  form.value = {
    id: plan.id,
    patient_disease_id: plan.patient_disease_id || 0,
    cycle_type: plan.cycle_type,
    cycle_value: plan.cycle_value,
    custom_days: plan.cycle_type === 'custom' ? String(plan.cycle_value) : '',
    next_date: plan.next_date,
    notes: plan.notes || ''
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const onDiseaseChange = (e: any) => {
  const index = e.detail.value
  if (index >= 0 && diseaseList.value[index]) {
    form.value.patient_disease_id = diseaseList.value[index].id
  }
}

const setCycle = (type: string) => {
  form.value.cycle_type = type
  
  // Auto calculate next date based on cycle
  const today = new Date()
  let target = new Date(today)
  
  if (type === 'week') {
    form.value.cycle_value = 1
    target.setDate(target.getDate() + 7)
  } else if (type === 'month') {
    form.value.cycle_value = 1
    target.setMonth(target.getMonth() + 1)
  } else if (type === 'quarter') {
    form.value.cycle_value = 1
    target.setMonth(target.getMonth() + 3)
  } else if (type === 'year') {
    form.value.cycle_value = 1
    target.setFullYear(target.getFullYear() + 1)
  } else {
    // Custom: keep date or default to +30 days if empty
     form.value.cycle_value = 30
     form.value.custom_days = '30'
     target.setDate(target.getDate() + 30)
  }
  
  form.value.next_date = target.toISOString().split('T')[0]
}

const onDateChange = (e: any) => {
  form.value.next_date = e.detail.value
}

const handleSave = async () => {
  if (!form.value.next_date) {
    uni.showToast({ title: '请选择复诊日期', icon: 'none' })
    return
  }
  
  if (form.value.cycle_type === 'custom' && form.value.custom_days) {
      form.value.cycle_value = parseInt(form.value.custom_days)
  }

  const payload = {
    patient_disease_id: form.value.patient_disease_id || null,
    cycle_type: form.value.cycle_type,
    cycle_value: form.value.cycle_value,
    next_date: form.value.next_date,
    reminder_days: 3, // Default reminder
    notes: form.value.notes
  }

  try {
    uni.showLoading({ title: '保存中' })
    if (isEditing.value) {
      await updateRevisitPlan(form.value.id, payload as any)
    } else {
      await addRevisitPlan(payload as any)
    }
    uni.showToast({ title: '保存成功' })
    closeModal()
    loadData()
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

const handleDelete = async () => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该复诊计划吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          uni.showLoading({ title: '删除中' })
          await deleteRevisitPlan(form.value.id)
          uni.showToast({ title: '已删除' })
          closeModal()
          loadData()
        } catch (e) {
           uni.showToast({ title: '删除失败', icon: 'none' })
        } finally {
          uni.hideLoading()
        }
      }
    }
  })
}

const checkIn = (plan: any) => {
  uni.showModal({
    title: '确认打卡',
    content: `确认已完成本次复诊吗？\n系统将自动把下次复诊日期更新为：${calculateNextDate(plan)}`,
    success: async (res) => {
      if (res.confirm) {
        try {
          uni.showLoading({ title: '打卡中' })
          const today = new Date().toISOString().split('T')[0]
          await addRevisitRecord({
            plan_id: plan.id,
            actual_date: today,
            status: 'completed',
            notes: ''
          })
          uni.showToast({ title: '打卡成功' })
          loadData() // Refresh plans to see updated date
        } catch (e) {
          uni.showToast({ title: '打卡失败', icon: 'none' })
        } finally {
          uni.hideLoading()
        }
      }
    }
  })
}

const calculateNextDate = (plan: any) => {
  // Simple preview calculation for UI
  const today = new Date()
  if (plan.cycle_type === 'week') today.setDate(today.getDate() + 7 * plan.cycle_value)
  if (plan.cycle_type === 'month') today.setMonth(today.getMonth() + plan.cycle_value)
  if (plan.cycle_type === 'quarter') today.setMonth(today.getMonth() + 3 * plan.cycle_value)
  if (plan.cycle_type === 'year') today.setFullYear(today.getFullYear() + plan.cycle_value)
  if (plan.cycle_type === 'custom') today.setDate(today.getDate() + plan.cycle_value)
  return today.toISOString().split('T')[0]
}

onShow(() => {
  if (activeTab.value === 0) {
    loadData()
  } else {
    loadHistory()
  }
})
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 16px;
}

.header-card {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.header-content {
  flex: 1;
}
.title {
  font-size: 20px;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 4px;
}
.subtitle {
  font-size: 12px;
  color: #dbeafe;
}

.add-btn {
  background-color: rgba(255,255,255,0.2);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}
.btn-text {
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
}

/* Tabs */
.tab-bar {
  display: flex;
  margin-bottom: 16px;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 4px;
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 14px;
  color: #64748b;
  position: relative;
}
.tab-item.active {
  color: #3b82f6;
  font-weight: 600;
}
.tab-line {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background-color: #3b82f6;
  border-radius: 2px;
}

.plan-list, .history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.card-left {
  flex: 1;
}

.disease-tag-wrapper {
  display: flex;
  margin-bottom: 8px;
}
.disease-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  position: relative;
  overflow: hidden;
}
.disease-badge::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(120deg, rgba(255,255,255,0) 30%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 70%);
  transform: skewX(-20deg);
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 6px;
  background-color: currentColor;
  opacity: 0.8;
}
.badge-text {
  position: relative;
  z-index: 1;
}

/* Badge Colors */
.bg-blue { 
  background-color: #e0f2fe; 
  color: #0284c7; 
  border: 1px solid #bae6fd;
}
.bg-orange { 
  background-color: #ffedd5; 
  color: #c2410c; 
  border: 1px solid #fed7aa;
}
.bg-green { 
  background-color: #dcfce7; 
  color: #15803d; 
  border: 1px solid #bbf7d0;
}
.bg-gray { 
  background-color: #f1f5f9; 
  color: #475569; 
  border: 1px solid #e2e8f0;
}

.cycle-info {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}
.cycle-value {
  color: #334155;
  font-weight: 500;
}

.next-date {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.label { color: #64748b; }
.value.highlight { color: #0f172a; font-weight: bold; }
.days-left { font-size: 12px; margin-left: auto; }
.text-red { color: #ef4444; }
.text-orange { color: #f59e0b; }
.text-gray { color: #94a3b8; }

.card-action {
  padding-left: 12px;
  display: flex;
  align-items: center;
}
.check-btn {
  background-color: #eff6ff;
  color: #3b82f6;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: 14px;
  font-weight: 600;
}

/* History Card */
.history-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.history-date {
  font-size: 16px;
  font-weight: bold;
  color: #1e293b;
  display: block;
}
.history-plan {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}
.history-notes {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
  display: block;
}
.status-text {
  font-size: 12px;
  color: #10b981;
  background-color: #ecfdf5;
  padding: 4px 8px;
  border-radius: 4px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}
.empty-text {
  color: #94a3b8;
  font-size: 14px;
}

/* Modal Styles */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: flex-end; /* Bottom sheet style */
  z-index: 100;
}

.modal-content {
  width: 100%;
  background-color: #ffffff;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 20px;
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.modal-title { font-size: 18px; font-weight: bold; color: #1e293b; }
.close-icon { font-size: 24px; color: #94a3b8; padding: 4px; }

.form-item {
  margin-bottom: 16px;
}
.label {
  display: block;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.picker-box {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  color: #334155;
}
.placeholder { color: #94a3b8; }

.cycle-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.cycle-opt {
  padding: 6px 12px;
  border-radius: 16px;
  background-color: #f1f5f9;
  color: #64748b;
  font-size: 13px;
  border: 1px solid transparent;
}
.cycle-opt.active {
  background-color: #eff6ff;
  color: #3b82f6;
  border-color: #3b82f6;
}

.input {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

.textarea {
  width: 100%;
  height: 80px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.btn-cancel {
  flex: 1;
  background-color: #f1f5f9;
  color: #64748b;
  border-radius: 8px;
  font-size: 14px;
}
.btn-save {
  flex: 2;
  background-color: #3b82f6;
  color: #ffffff;
  border-radius: 8px;
  font-size: 14px;
}
</style>