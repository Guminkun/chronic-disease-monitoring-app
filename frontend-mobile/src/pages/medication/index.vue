<template>
  <view class="page">
    <view class="header">
      <text class="title">用药</text>
    </view>

    <view class="segmented">
      <view class="seg-item" :class="{ active: currentTab === 0 }" @click="switchTab(0)">
        <text>今日用药</text>
      </view>
      <view class="seg-item" :class="{ active: currentTab === 1 }" @click="switchTab(1)">
        <text>药品列表</text>
      </view>
    </view>

    <!-- 未登录提示 -->
    <AuthPrompt 
      v-if="!isLoggedIn()"
      title="登录以管理用药计划"
      description="登录后可添加药品、记录服药情况"
      icon="💊"
      theme="success"
      size="medium"
    />

    <!-- 即将到期的临时用药提醒 -->
    <view v-if="expiringTempPlans.length > 0" class="expiring-section">
      <view class="expiring-header">
        <text class="expiring-title">即将结束</text>
        <text class="expiring-hint">临时用药即将到期</text>
      </view>
      <view v-for="plan in expiringTempPlans" :key="plan.id" class="expiring-card">
        <view class="expiring-main">
          <text class="expiring-name">{{ plan.name }}</text>
          <text class="expiring-days">剩余 {{ getRemainingDays(plan) }} 天</text>
        </view>
        <view class="expiring-actions">
          <view class="ep-btn extend" @click="handleExtend(plan)">
            <text>延期</text>
          </view>
          <view class="ep-btn end" @click="handleEnd(plan)">
            <text>结束</text>
          </view>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="scroll">
      <view v-if="currentTab === 0" class="today">
        <view class="section-head">
          <view class="sh-left">
            <text class="sh-title">待服用</text>
            <view class="count-badge blue" v-if="pendingTasks.length > 0">
              <text>{{ pendingTasks.length }}</text>
            </view>
          </view>
        </view>

        <view v-for="task in pendingTasks" :key="taskKey(task)" class="task-card">
           <view class="task-icon" :class="{ temporary: task.is_temporary }">
             <text class="task-emoji">{{ task.is_temporary ? '⏰' : '💊' }}</text>
           </view>
           <view class="task-main">
             <view class="task-name-row">
               <text class="task-name">{{ task.plan_name }}</text>
               <view v-if="task.is_temporary" class="temp-badge">
                 <text>临时</text>
               </view>
             </view>
             <view class="task-info-row">
               <text class="task-dosage">{{ formatTaskDosage(task) }}</text>
               <text class="task-time">计划时间 {{ formatHHmm(task.scheduled_time) }}</text>
             </view>
           </view>
           <view class="task-action" @click.stop="handleTake(task)">
             <view class="take-btn">
               <text class="btn-check">✓</text>
               <text class="take-text">服用</text>
             </view>
           </view>
         </view>

        <view v-if="pendingTasks.length === 0" class="empty">
          <text>暂无待服用任务</text>
        </view>

        <view class="section-head done">
          <view class="sh-left">
            <text class="sh-title">已完成</text>
            <view class="count-badge green" v-if="doneTasks.length > 0">
              <text>{{ doneTasks.length }}</text>
            </view>
          </view>
        </view>

        <view v-for="task in doneTasks" :key="taskKey(task)" class="task-card done-card">
           <view class="task-icon done-icon">
             <text class="task-emoji">✅</text>
           </view>
           <view class="task-main">
             <text class="task-name">{{ task.plan_name }}</text>
             <view class="task-info-row">
               <text class="task-dosage done">{{ formatTaskDosage(task) }}</text>
               <text class="task-time">已于 {{ formatTakenText(task) }}</text>
             </view>
           </view>
           <view class="task-action">
             <view class="pill" :class="{ gray: task.status !== 'taken' }">
               <text class="pill-text">{{ task.status === 'taken' ? '已服用' : '已跳过' }}</text>
             </view>
           </view>
         </view>

        <view v-if="doneTasks.length === 0" class="empty">
          <text>暂无已完成记录</text>
        </view>
      </view>

      <view v-else class="plans">
        <view class="search-box">
          <text class="search-icon">🔍</text>
          <input class="search-input" v-model="searchText" placeholder="搜索药品名称或生产单位" />
        </view>

        <view class="plans-head">
          <text class="plans-count">共 {{ filteredPlanList.length }} 种药品</text>
          <view class="add-btn" @click="openAdd">
            <text class="add-plus">＋</text>
            <text class="add-text">添加药品</text>
          </view>
        </view>

        <view v-for="plan in filteredPlanList" :key="plan.id" class="plan-card" @click="openPlan(plan)">
           <!-- 左侧：药品基本信息 -->
           <view class="plan-left">
             <text class="plan-name">{{ plan.name }}</text>
             <text v-if="plan.manufacturer" class="plan-manufacturer">{{ plan.manufacturer }}</text>
             <text class="plan-sub">{{ formatDosageDisplay(plan) }} · {{ formatFrequencyDisplay(plan) }}</text>
             <view class="time-chips">
               <view v-for="t in (plan.taken_times || [])" :key="t" class="time-chip">
                 <text>{{ t }}</text>
               </view>
             </view>
           </view>
          
           <!-- 右侧：状态标签 + 操作区 -->
           <view class="plan-right">
             <!-- 状态标签区 -->
             <view class="status-section">
               <view v-if="plan.is_temporary" class="temp-pill">
                 <text>临时用药</text>
               </view>
               <!-- 临时用药：剩余≤3天显示红色警告 -->
               <view v-if="plan.is_temporary && remainingDays(plan) !== null && remainingDays(plan)! <= 3" class="remain-pill danger animate-pulse">
                 <text>剩 {{ remainingDays(plan)! }}天</text>
               </view>
                <!-- 长期用药：显示剩余天数 -->
                <view v-if="!plan.is_temporary && remainingDays(plan) !== null && remainingDays(plan)! > 0" class="remain-pill" :class="remainingDays(plan)! <= 3 ? 'danger' : (remainingDays(plan)! <= 7 ? 'warning' : '')">
                  <text>剩{{ remainingDays(plan) }}天</text>
                </view>
             </view>
             
              <!-- 操作按钮区 -->
             <view class="action-section">
              <view class="action-btn edit" @click.stop="handleEdit(plan)">
                <text class="action-icon">✏️</text>
              </view>
              <view class="action-btn delete" @click.stop="handleDelete(plan)">
                <text class="action-icon">🗑️</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="planList.length === 0" class="empty">
          <text>暂无药品医嘱</text>
        </view>
      </view>

      <view style="height: 24px;"></view>
    </scroll-view>

    <view v-if="detailVisible" class="detail-overlay" @click="closePlan">
      <view class="detail-sheet" @click.stop>
        <view class="detail-top">
          <view class="detail-left">
            <view class="detail-icon">
              <text class="task-emoji">💊</text>
            </view>
            <text class="detail-name">{{ selectedPlan?.name }}</text>
          </view>
          <view class="detail-close" @click="closePlan">
            <text class="close-text">✕</text>
          </view>
        </view>

        <view class="detail-grid">
           <view class="detail-box">
             <text class="box-label">剂量</text>
             <text class="box-value">{{ formatDosageDisplay(selectedPlan || {}) }}</text>
           </view>
           <view class="detail-box">
             <text class="box-label">频率</text>
             <text class="box-value">{{ formatFrequencyDisplay(selectedPlan || {}) }}</text>
           </view>
          <view class="detail-box full">
            <text class="box-label">服用时间</text>
            <text class="box-value">{{ (selectedPlan?.taken_times || []).join(' / ') || '-' }}</text>
          </view>
          <view class="detail-box full">
            <text class="box-label">服用说明</text>
            <text class="box-value">{{ selectedPlan?.timing_condition || selectedPlan?.notes || '-' }}</text>
          </view>
        </view>

        <view class="start-row">
          <text class="start-text">开始服用于 {{ selectedPlan?.start_date || '-' }}</text>
          <text v-if="selectedPlan?.end_date" class="end-text">至 {{ selectedPlan.end_date }}</text>
        </view>

        <view v-if="selectedPlan?.is_temporary && remainingDays(selectedPlan) !== null" class="temp-info">
          <text class="temp-label">临时用药</text>
          <text class="temp-days">剩余 {{ getRemainingDays(selectedPlan) }} 天</text>
        </view>

        <!-- 长期用药也显示剩余天数 -->
        <view v-if="!selectedPlan?.is_temporary && remainingDays(selectedPlan) !== null && remainingDays(selectedPlan)! > 0" class="temp-info long-term">
          <text class="temp-label">长期用药</text>
          <text class="temp-days">剩余 {{ getRemainingDays(selectedPlan) }} 天</text>
        </view>

        <view v-if="remainingDays(selectedPlan) !== null && (remainingDays(selectedPlan) || 0) <= 7" class="stock-warning">
          <text class="warn-text">库存不足，仅剩 {{ remainingDays(selectedPlan!) }} 天用量</text>
        </view>

        <view v-if="selectedPlan?.is_temporary" class="detail-actions">
          <view class="da-btn extend" @click="handleExtend(selectedPlan)">
            <text class="da-icon">📅</text>
            <text class="da-text">延期</text>
          </view>
          <view class="da-btn end" @click="handleEnd(selectedPlan)">
            <text class="da-icon">✓</text>
            <text class="da-text">结束用药</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 延期日期输入对话框 -->
    <view v-if="extendDialogVisible" class="extend-overlay" @click="closeExtendDialog">
      <view class="extend-dialog" @click.stop>
        <view class="dialog-header">
          <text class="dialog-title">延期用药计划</text>
          <view class="dialog-close" @click="closeExtendDialog">
            <text class="close-icon">✕</text>
          </view>
        </view>
        
        <view class="dialog-content">
          <view class="current-info">
            <text class="info-label">当前结束日期</text>
            <text class="info-value">{{ extendingPlan?.end_date || '未设置' }}</text>
          </view>
          
          <view class="date-input-section">
            <text class="input-label">选择新的结束日期</text>
            <view class="date-input-wrapper">
              <input 
                class="date-input"
                type="text"
                v-model="extendDateInput"
                placeholder="请输入日期（YYYY-MM-DD）"
                maxlength="10"
                @blur="validateDateFormat"
              />
              <text class="format-hint">格式：YYYY-MM-DD（如：2026-04-15）</text>
            </view>
          </view>
          
          <view class="quick-options">
            <text class="quick-label">快速选择</text>
            <view class="quick-btns">
              <view class="quick-btn" @click="quickExtend(3)">
                <text>延3天</text>
              </view>
              <view class="quick-btn" @click="quickExtend(7)">
                <text>延7天</text>
              </view>
              <view class="quick-btn" @click="quickExtend(14)">
                <text>延14天</text>
              </view>
              <view class="quick-btn" @click="quickExtend(30)">
                <text>延30天</text>
              </view>
            </view>
          </view>
        </view>
        
        <view class="dialog-footer">
          <button class="btn-cancel" @click="closeExtendDialog">取消</button>
          <button class="btn-confirm" @click="confirmExtend">确认延期</button>
        </view>
      </view>
    </view>
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="1" />
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'
import { useMemberStore } from '@/stores/member'
import * as medApi from '@/api/medication'
import { isLoggedIn, checkLoginWithRedirect } from '@/utils/auth'
import AuthPrompt from '@/components/AuthPrompt.vue'
import CustomTabBar from '@/components/tabbar/CustomTabBar.vue'

const userStore = useUserStore()
const memberStore = useMemberStore()

const currentTab = ref(0)
const dailyTasks = ref<any[]>([])
const planList = ref<any[]>([])
const searchText = ref('')

const filteredPlanList = computed(() => {
  if (!searchText.value) return planList.value
  const query = searchText.value.toLowerCase()
  return planList.value.filter(p => 
    p.name.toLowerCase().includes(query) || 
    (p.manufacturer && p.manufacturer.toLowerCase().includes(query))
  )
})

const expiringTempPlans = computed(() => {
  return planList.value.filter(p => {
    if (!p.is_temporary || !p.end_date) return false
    const days = getRemainingDays(p)
    return days !== null && days >= 0 && days <= 3
  })
})

const getRemainingDays = (plan: any): number | null => {
  if (!plan?.end_date) return null
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  const endDate = new Date(plan.end_date)
  if (Number.isNaN(endDate.getTime())) return null
  const diff = Math.ceil((endDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
  return diff < 0 ? 0 : diff
}

const extendDialogVisible = ref(false)
const extendDateInput = ref('')
const extendingPlan = ref<any | null>(null)

const minExtendDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const handleExtend = (plan: any) => {
  // 先关闭详情弹窗，避免层级冲突
  detailVisible.value = false
  
  extendingPlan.value = plan
  
  // 默认设置为当前结束日期或今天
  const currentEnd = plan.end_date ? new Date(plan.end_date) : new Date()
  extendDateInput.value = currentEnd.toISOString().split('T')[0]
  
  // 延迟打开延期对话框，确保详情弹窗已关闭
  setTimeout(() => {
    extendDialogVisible.value = true
  }, 100)
}

const closeExtendDialog = () => {
  extendDialogVisible.value = false
  extendingPlan.value = null
  extendDateInput.value = ''
}

const validateDateFormat = () => {
  if (!extendDateInput.value) return
  
  const input = extendDateInput.value.trim()
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  
  if (!dateRegex.test(input)) {
    uni.showToast({ title: '格式：YYYY-MM-DD', icon: 'none', duration: 2000 })
    return false
  }
  
  const date = new Date(input)
  if (isNaN(date.getTime())) {
    uni.showToast({ title: '无效的日期', icon: 'none', duration: 2000 })
    return false
  }
  
  return true
}

const onExtendDateChange = (e: any) => {
  extendDateInput.value = e.detail.value
}

const quickExtend = (days: number) => {
  const currentEnd = extendingPlan.value?.end_date 
    ? new Date(extendingPlan.value.end_date) 
    : new Date()
  const newEnd = new Date(currentEnd)
  newEnd.setDate(newEnd.getDate() + days)
  extendDateInput.value = newEnd.toISOString().split('T')[0]
}

const confirmExtend = async () => {
  if (!extendDateInput.value) {
    uni.showToast({ title: '请选择延期日期', icon: 'none' })
    return
  }
  
  // 验证日期格式
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!dateRegex.test(extendDateInput.value)) {
    uni.showToast({ title: '日期格式不正确', icon: 'none' })
    return
  }
  
  // 验证日期是否有效
  const newDate = new Date(extendDateInput.value)
  if (isNaN(newDate.getTime())) {
    uni.showToast({ title: '无效的日期', icon: 'none' })
    return
  }
  
  // 验证日期是否大于当前结束日期
  const currentEnd = extendingPlan.value?.end_date 
    ? new Date(extendingPlan.value.end_date) 
    : new Date()
  currentEnd.setHours(0, 0, 0, 0)
  newDate.setHours(0, 0, 0, 0)
  
  if (newDate <= currentEnd) {
    uni.showToast({ title: '延期日期必须晚于当前结束日期', icon: 'none' })
    return
  }
  
  try {
    uni.showLoading({ title: '处理中' })
    await medApi.updatePlan(extendingPlan.value.id, {
      end_date: extendDateInput.value
    })
    uni.hideLoading()
    
    const diffDays = Math.ceil((newDate.getTime() - currentEnd.getTime()) / (24 * 60 * 60 * 1000))
    uni.showToast({ title: `已延期${diffDays}天`, icon: 'success' })
    
    // 保存当前用药计划ID
    const planId = extendingPlan.value.id
    
    closeExtendDialog()
    
    // 重新加载数据
    await loadPlans()
    await loadDailyTasks()
    
    // 重新打开详情弹窗，显示更新后的数据
    setTimeout(() => {
      const updatedPlan = planList.value.find(p => p.id === planId)
      if (updatedPlan) {
        selectedPlan.value = updatedPlan
        detailVisible.value = true
      }
    }, 500)
  } catch (error) {
    uni.hideLoading()
    console.error('延期失败:', error)
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

const handleEnd = async (plan: any) => {
  uni.showModal({
    title: '结束用药',
    content: `确定要结束"${plan.name}"的用药计划吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await medApi.updatePlan(plan.id, { is_active: false })
          uni.showToast({ title: '已结束' })
          loadPlans()
          loadDailyTasks()
        } catch {
          uni.showToast({ title: '操作失败', icon: 'none' })
        }
      }
    }
  })
}

const switchTab = (index: number) => {
  currentTab.value = index
  if (index === 0) loadDailyTasks()
  if (index === 1) loadPlans()
}

onShow(() => {
  loadData()
})

const loadData = async () => {
  if (!isLoggedIn()) {
    dailyTasks.value = []
    planList.value = []
    return
  }
  await memberStore.loadMembers()
  await Promise.all([loadDailyTasks(), loadPlans()])
}

const loadDailyTasks = async () => {
  if (!isLoggedIn()) {
    dailyTasks.value = []
    return
  }
  try {
    const today = new Date().toISOString().split('T')[0]
    const memberId = memberStore.currentMember?.id
    const res: any = await medApi.getDailyTasks(today, memberId)
    dailyTasks.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    dailyTasks.value = []
  }
}

const loadPlans = async () => {
  if (!isLoggedIn()) {
    planList.value = []
    return
  }
  try {
    const memberId = memberStore.currentMember?.id
    const res: any = await medApi.getPlans(true, memberId)
    planList.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    planList.value = []
  }
}

const pendingTasks = computed(() => dailyTasks.value.filter(t => t.status === 'pending'))
const doneTasks = computed(() => dailyTasks.value.filter(t => t.status !== 'pending'))

const taskKey = (task: any) => `${task.plan_id}-${task.scheduled_time}`

const formatHHmm = (isoStr: string) => {
  if (!isoStr) return '--:--'
  try {
    return new Date(isoStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '--:--'
  }
}

const formatTakenText = (task: any) => {
  const t = task?.taken_time || task?.scheduled_time
  return formatHHmm(t)
}

const handleTake = async (task: any) => {
  if (!isLoggedIn()) {
    checkLoginWithRedirect('/pages/medication/index')
    return
  }
  try {
    await medApi.checkin({
      plan_id: task.plan_id,
      scheduled_time: task.scheduled_time,
      status: 'taken'
    })
    uni.showToast({ title: '打卡成功' })
    loadDailyTasks()
  } catch {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

const formatFrequency = (plan: any) => {
  if (plan.frequency_type === 'daily') return '每日'
  if (plan.frequency_type === 'interval') return `每隔${plan.frequency_value}天`
  return plan.frequency_value || '-'
}

const formatTaskDosage = (task: any) => {
  if (!task.dosage_amount) return ''
  const amount = task.dosage_amount
  const unit = task.dosage_unit || ''
  
  const unitLower = unit.toLowerCase()
  if (unitLower.includes('片') || unitLower === 'tablet') {
    return `${amount}片/次`
  }
  if (unitLower.includes('袋') || unitLower.includes('包') || unitLower === 'bag' || unitLower === 'pack') {
    return `${amount}袋/次`
  }
  if (unitLower.includes('粒') || unitLower === 'capsule' || unitLower === 'pill') {
    return `${amount}粒/次`
  }
  if (unitLower.includes('ml') || unitLower.includes('毫升')) {
    return `${amount}ml/次`
  }
  if (unitLower.includes('mg') || unitLower.includes('毫克')) {
    return `${amount}mg/次`
  }
  
  return `${amount}${unit}/次`
}

const formatDosageDisplay = (plan: any) => {
  if (!plan.dosage_amount) return '-'
  const amount = plan.dosage_amount
  const unit = plan.dosage_unit || ''
  
  // 根据单位判断显示方式
  const unitLower = unit.toLowerCase()
  if (unitLower.includes('片') || unitLower === 'tablet') {
    return `每次${amount}片`
  }
  if (unitLower.includes('袋') || unitLower.includes('包') || unitLower === 'bag' || unitLower === 'pack') {
    return `每次${amount}袋`
  }
  if (unitLower.includes('粒') || unitLower === 'capsule' || unitLower === 'pill') {
    return `每次${amount}粒`
  }
  if (unitLower.includes('ml') || unitLower.includes('毫升')) {
    return `每次${amount}ml`
  }
  if (unitLower.includes('mg') || unitLower.includes('毫克')) {
    return `每次${amount}mg`
  }
  if (unitLower.includes('滴')) {
    return `每次${amount}滴`
  }
  if (unitLower.includes('勺')) {
    return `每次${amount}勺`
  }
  
  // 默认显示原单位
  return `每次${amount}${unit}`
}

const formatFrequencyDisplay = (plan: any) => {
  if (plan.frequency_type === 'daily') {
    // 从 taken_times 数组长度判断每日次数
    const timesCount = (plan.taken_times || []).length
    if (timesCount > 0) {
      return `每日${timesCount}次`
    }
    return '每日1次'
  }
  if (plan.frequency_type === 'interval') {
    return `每隔${plan.frequency_value || 1}天服用`
  }
  if (plan.frequency_type === 'weekly') {
    return `每周${plan.frequency_value || 1}次`
  }
  return plan.frequency_value || '按需服用'
}

const remainingDays = (plan: any): number | null => {
  if (plan === null || plan === undefined) return null
  const end = plan?.end_date
  if (!end) return null
  const now = new Date()
  const endDate = new Date(end)
  if (Number.isNaN(endDate.getTime())) return null
  const diff = Math.ceil((endDate.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
  return diff < 0 ? 0 : diff
}

const handleEdit = (plan: any) => {
  if (!isLoggedIn()) {
    checkLoginWithRedirect('/pages/medication/index')
    return
  }
  uni.navigateTo({
    url: `/pages/medication/add?id=${plan.id}`
  })
}

const handleDelete = async (plan: any) => {
  if (!isLoggedIn()) {
    checkLoginWithRedirect('/pages/medication/index')
    return
  }
  uni.showModal({
    title: '确认删除',
    content: `确定要删除药品"${plan.name}"吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await medApi.deletePlan(plan.id)
          uni.showToast({ title: '已删除' })
          loadPlans()
        } catch {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

const openAdd = () => {
  if (!isLoggedIn()) {
    checkLoginWithRedirect('/pages/medication/index')
    return
  }
  uni.navigateTo({ url: '/pages/medication/add' })
}

const detailVisible = ref(false)
const selectedPlan = ref<any | null>(null)

const openPlan = (plan: any) => {
  selectedPlan.value = plan
  detailVisible.value = true
}

const closePlan = () => {
  detailVisible.value = false
  selectedPlan.value = null
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  display: flex;
  flex-direction: column;
  padding-bottom: 120rpx;
}

.header {
  padding: 18px 20px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--color-bg-elevated);
}

.title {
  font-size: 28px;
  font-weight: 900;
  color: #0f172a;
}

.segmented {
  margin: 0 20px 14px;
  background: rgba(15, 23, 42, 0.04);
  border-radius: 18px;
  padding: 4px;
  display: flex;
  gap: 6px;
}

.seg-item {
  flex: 1;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
}

.seg-item.active {
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
}

.scroll {
  flex: 1;
  padding: 0 20px;
  box-sizing: border-box;
}

.search-box {
  background: #ffffff;
  border-radius: 14px;
  padding: 0 14px;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  border: 1px solid rgba(15, 23, 42, 0.06);
}

.search-input {
  flex: 1;
  font-size: 14px;
  color: #0f172a;
}

.section-head {
  margin: 14px 0 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-head.done {
  margin-top: 18px;
}

.sh-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sh-title {
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
}

.count-badge {
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
}

.count-badge text {
  font-size: 12px;
  font-weight: 900;
  color: #ffffff;
}

.count-badge.blue { background: #2563eb; }
.count-badge.green { background: #16a34a; }

.task-card {
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 18px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  position: relative;
  overflow: hidden;
}

.task-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.6));
}

.task-card.done-card {
  background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.task-icon {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 48px;
}

.task-icon.done-icon {
  background: #eaf7ef;
}

.task-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-name {
  font-size: 16px;
  font-weight: 900;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-sub {
  font-size: 13px;
  color: #64748b;
  font-weight: 600;
}

.task-info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-dosage {
  font-size: 13px;
  color: #2563eb;
  font-weight: 700;
  background: #eff6ff;
  padding: 2px 8px;
  border-radius: 6px;
  display: inline-block;
  width: fit-content;
}

.task-time {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.task-dosage.done {
  color: #64748b;
  background: #f1f5f9;
}

.take-btn {
  height: 40px;
  padding: 0 14px;
  border-radius: 20px;
  background: #2563eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.take-text {
  color: #ffffff;
  font-size: 14px;
  font-weight: 900;
}

.pill {
  height: 28px;
  padding: 0 12px;
  border-radius: 14px;
  background: rgba(22, 163, 74, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pill.gray {
  background: rgba(100, 116, 139, 0.14);
}

.pill-text {
  font-size: 12px;
  font-weight: 900;
  color: #16a34a;
}

.pill.gray .pill-text {
  color: #64748b;
}

.plans-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 12px;
}

.plans-count {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
}

.add-btn {
  height: 36px;
  padding: 0 14px;
  border-radius: 18px;
  background: #2563eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-plus {
  color: #ffffff;
  font-weight: 900;
  font-size: 18px;
  line-height: 1;
}

.add-text {
  color: #ffffff;
  font-size: 13px;
  font-weight: 900;
}

.plan-card {
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  display: flex;
  align-items: stretch;
  gap: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  min-height: 200rpx;
  position: relative;
  overflow: hidden;
}

.plan-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.6));
}

.plan-left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.plan-name {
  font-size: 36rpx;
  font-weight: 900;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.plan-manufacturer {
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
  line-height: 1.6;
}

.plan-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  flex: 0 0 auto;
  padding-left: 24rpx;
  border-left: 2rpx solid #f1f5f9;
  gap: 16rpx;
}

.status-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.action-section {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.temp-pill {
  padding: 8rpx 20rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 2rpx solid rgba(249, 115, 22, 0.4);
  flex-shrink: 0;
  white-space: nowrap;
  box-shadow: 0 2rpx 8rpx rgba(249, 115, 22, 0.15);
}

.temp-pill text {
  font-size: 24rpx;
  font-weight: 800;
  color: #ea580c;
}

.action-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:active {
  transform: scale(0.95);
  background: #f1f5f9;
}

.action-btn.delete {
  background: #fef2f2;
  border-color: #fee2e2;
}

.remain-pill {
  height: 48rpx;
  padding: 0 20rpx;
  border-radius: 24rpx;
  background: rgba(15, 23, 42, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.remain-pill text {
  font-size: 26rpx;
  font-weight: 900;
  color: #0f172a;
  white-space: nowrap;
}

.remain-pill.danger {
  background: #ef4444;
  box-shadow: 0 4rpx 12rpx rgba(239, 68, 68, 0.3);
}

.remain-pill.danger text {
  color: #ffffff;
}

.remain-pill.warning {
  background: #f97316;
  box-shadow: 0 4rpx 12rpx rgba(249, 115, 22, 0.3);
}

.remain-pill.warning text {
  color: #ffffff;
}

.plan-sub {
  font-size: 28rpx;
  color: #475569;
  font-weight: 700;
  line-height: 1.6;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.plan-sub::before {
  content: '';
  width: 6rpx;
  height: 6rpx;
  background: #2563eb;
  border-radius: 50%;
  margin-right: 4rpx;
}

.time-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 4rpx;
}

.time-chip {
  height: 48rpx;
  padding: 0 20rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 2rpx solid rgba(37, 99, 235, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-chip text {
  font-size: 26rpx;
  font-weight: 800;
  color: #2563eb;
}

.plan-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.plan-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 4rpx;
}

.plan-name-section {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
  min-width: 0;
}

.plan-name {
  font-size: 36rpx;
  font-weight: 900;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.plan-manufacturer {
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
  line-height: 1.6;
}

.empty {
  padding: 16px 0;
  text-align: center;
}

.empty text {
  font-size: 13px;
  color: #94a3b8;
  font-weight: 600;
}

.detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 24px;
  box-sizing: border-box;
}

.detail-sheet {
  width: 100%;
  max-width: 520px;
  background: #eaf2f9;
  border-radius: 20px;
  padding: 16px;
  box-sizing: border-box;
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

.detail-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.detail-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.detail-icon {
  width: 46px;
  height: 46px;
  border-radius: 18px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 46px;
}

.detail-name {
  font-size: 20px;
  font-weight: 900;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-close {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(255,255,255,0.65);
  border: 1px solid rgba(148, 163, 184, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-box {
  background: rgba(241, 245, 249, 0.9);
  border-radius: 14px;
  padding: 16px;
}

.detail-box.full {
  grid-column: 1 / -1;
}

.box-label {
  display: block;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
  margin-bottom: 8px;
}

.box-value {
  display: block;
  font-size: 18px;
  font-weight: 900;
  color: #0f172a;
  line-height: 22px;
}

.start-row {
  margin-top: 12px;
  background: rgba(37, 99, 235, 0.10);
  border: 1px solid rgba(37, 99, 235, 0.24);
  border-radius: 16px;
  padding: 14px 16px;
}

.start-text {
  color: #2563eb;
  font-size: 14px;
  font-weight: 900;
}

.stock-warning {
  margin-top: 14px;
  background: rgba(249, 115, 22, 0.12);
  border: 1px solid rgba(249, 115, 22, 0.22);
  border-radius: 16px;
  padding: 14px;
}

.warn-text {
  color: #f97316;
  font-size: 14px;
  font-weight: 900;
}

.task-emoji { font-size: 22px; line-height: 1; }
.btn-check { font-size: 16px; color: #ffffff; font-weight: 900; line-height: 1; }
.search-icon { font-size: 18px; line-height: 1; }
.action-icon { font-size: 14px; line-height: 1; }
.close-text { font-size: 18px; color: #64748b; line-height: 1; }

/* 临时用药标识 */
.task-icon.temporary {
  background: #fff7ed;
}

.task-icon.temporary .task-emoji {
  font-size: 20px;
}

.temp-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 32rpx;
  padding: 0 8rpx;
  border-radius: 6rpx;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 1rpx solid rgba(249, 115, 22, 0.3);
  flex-shrink: 0;
  white-space: nowrap;
}

.temp-badge text {
  font-size: 18rpx;
  font-weight: 700;
  color: #ea580c;
  line-height: 1;
}

.temp-pill {
  padding: 8rpx 20rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 2rpx solid rgba(249, 115, 22, 0.4);
  flex-shrink: 0;
  white-space: nowrap;
  box-shadow: 0 2rpx 8rpx rgba(249, 115, 22, 0.15);
}

.temp-pill text {
  font-size: 24rpx;
  font-weight: 800;
  color: #ea580c;
}

/* 即将到期提醒 */
.expiring-section {
  margin: 0 20px 14px;
  background: #fef3c7;
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.expiring-header {
  margin-bottom: 12px;
}

.expiring-title {
  font-size: 15px;
  font-weight: 900;
  color: #92400e;
}

.expiring-hint {
  font-size: 12px;
  color: #b45309;
  margin-left: 8px;
}

.expiring-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.expiring-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.expiring-name {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.expiring-days {
  font-size: 12px;
  color: #f97316;
  font-weight: 600;
}

.expiring-actions {
  display: flex;
  gap: 10px;
}

.ep-btn {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
}

.ep-btn.extend {
  background: #fff7ed;
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.ep-btn.end {
  background: #f1f5f9;
  color: #64748b;
}

.end-text {
  color: #64748b;
  font-size: 14px;
  font-weight: 700;
  margin-left: 12px;
}

.temp-info {
  margin-top: 12px;
  background: #fff7ed;
  border: 1px solid rgba(249, 115, 22, 0.24);
  border-radius: 16px;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.temp-info.long-term {
  background: #eff6ff;
  border: 1px solid rgba(37, 99, 235, 0.24);
}

.temp-info.long-term .temp-label {
  color: #2563eb;
}

.temp-info.long-term .temp-days {
  color: #1d4ed8;
}

.temp-label {
  color: #f97316;
  font-size: 14px;
  font-weight: 900;
}

.temp-days {
  color: #ea580c;
  font-size: 13px;
  font-weight: 700;
}

.detail-actions {
  margin-top: 14px;
  display: flex;
  gap: 12px;
}

.da-btn {
  flex: 1;
  padding: 14px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.da-btn.extend {
  background: #fff7ed;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.da-btn.extend .da-text {
  color: #f97316;
}

.da-btn.end {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.da-btn.end .da-text {
  color: #64748b;
}

.da-icon {
  font-size: 16px;
}

.da-text {
  font-size: 14px;
  font-weight: 700;
}

/* 延期对话框 */
.extend-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
  box-sizing: border-box;
}

.extend-dialog {
  width: 100%;
  max-width: 560rpx;
  background: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 20rpx 60rpx rgba(15, 23, 42, 0.3);
}

.dialog-header {
  padding: 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dialog-title {
  font-size: 32rpx;
  font-weight: 900;
  color: #ffffff;
}

.dialog-close {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-icon {
  font-size: 28rpx;
  color: #ffffff;
  line-height: 1;
}

.dialog-content {
  padding: 32rpx;
}

.current-info {
  background: #f8fafc;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
}

.info-value {
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 900;
}

.date-input-section {
  margin-bottom: 32rpx;
}

.input-label {
  display: block;
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.date-input-wrapper {
  width: 100%;
}

.date-input {
  width: 100%;
  height: 88rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 600;
  box-sizing: border-box;
  transition: all 0.3s;
}

.date-input:focus {
  border-color: #667eea;
  background: #ffffff;
  box-shadow: 0 0 0 6rpx rgba(102, 126, 234, 0.1);
}

.date-input::placeholder {
  color: #94a3b8;
  font-weight: 400;
}

.format-hint {
  display: block;
  font-size: 22rpx;
  color: #94a3b8;
  margin-top: 12rpx;
  line-height: 1.4;
}

.quick-options {
  margin-top: 24rpx;
}

.quick-label {
  display: block;
  font-size: 26rpx;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.quick-btns {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.quick-btn {
  flex: 1;
  min-width: 120rpx;
  height: 64rpx;
  background: #eff6ff;
  border: 2rpx solid #bfdbfe;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.quick-btn:active {
  background: #bfdbfe;
  border-color: #667eea;
}

.quick-btn text {
  font-size: 26rpx;
  font-weight: 700;
  color: #2563eb;
}

.dialog-footer {
  padding: 24rpx 32rpx;
  display: flex;
  gap: 24rpx;
  border-top: 1rpx solid #f1f5f9;
}

.btn-cancel {
  flex: 1;
  height: 88rpx;
  background: #f8fafc;
  border: 2rpx solid #e2e8f0;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-cancel::after {
  border: none;
}

.btn-confirm {
  flex: 2;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 900;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}

.btn-confirm::after {
  border: none;
}
</style>
