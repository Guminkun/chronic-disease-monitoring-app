<template>
  <view class="page-wrap">

    <!-- ─── 顶部区域 ─── -->
    <view class="top-bar-v2">
      <!-- 左侧用户信息 -->
      <view class="user-info-section" @click="toggleMemberPanel">
        <view class="avatar-wrapper">
          <image 
            v-if="currentMemberAvatar" 
            :src="currentMemberAvatar" 
            class="user-avatar" 
            mode="aspectFill"
          />
          <view v-else class="user-avatar-placeholder">
            <text class="avatar-text">{{ currentMemberInitial }}</text>
          </view>
          <!-- 切换图标（小箭头） -->
          <view class="member-switch-dot">
            <view class="icon-arrow-down-s"></view>
          </view>
        </view>
        <view class="user-text-info">
          <text class="user-name">{{ memberStore.currentMember?.nickname || '自己' }}</text>
          <text class="user-role">{{ memberStore.currentMember?.id === userStore.user?.id ? '自己' : '家庭成员' }}</text>
        </view>
      </view>

      <!-- 右侧消息通知 -->
      <view class="notice-section" @click="goToNotifications">
        <view class="notice-icon-wrapper">
          <text class="notice-bell-emoji">🔔</text>
          <view class="notice-badge" v-if="unreadNotificationCount > 0">
            <text class="badge-text">{{ unreadNotificationCount > 9 ? '9+' : unreadNotificationCount }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 成员卡片弹出面板 -->
    <view v-if="showMemberPanel" class="member-panel-mask" @click="closeMemberPanel">
      <view class="member-panel" @click.stop>
        <view class="member-panel-head">
          <text class="member-panel-title">切换成员</text>
          <view class="member-panel-close" @click="closeMemberPanel">
            <text>✕</text>
          </view>
        </view>
        
        <scroll-view scroll-x class="member-scroll" :show-scrollbar="false">
          <view class="member-cards-wrap">
            <!-- 所有成员卡片 -->
            <view 
              v-for="member in allMembers" 
              :key="member.id"
              class="member-card"
              :class="{ 'is-selected': member.id === memberStore.currentMember?.id }"
              @click="selectMember(member.id)"
            >
              <view class="member-avatar-circle">
                <image 
                  v-if="member.avatar_url" 
                  :src="member.avatar_url" 
                  class="avatar-img" 
                  mode="aspectFill"
                />
                <view v-else class="avatar-placeholder">
                  <view class="default-avatar-silhouette">
                    <view class="silhouette-head"></view>
                    <view class="silhouette-body"></view>
                  </view>
                </view>
              </view>
              <text class="member-nickname">{{ member.nickname || '自己' }}</text>
            </view>
            
            <!-- 管理按钮卡片 -->
            <view class="member-card manage-card" @click="goToMember">
              <view class="member-avatar-circle manage-circle">
                <text class="gear-emoji">⚙️</text>
              </view>
              <text class="member-nickname">管理</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 搜索栏 -->
    <view class="search-bar" @click="handleSearch">
      <view class="search-icon-wrap">
        <view class="search-circle"></view>
        <view class="search-handle"></view>
      </view>
      <text class="search-placeholder">搜索药品、疾病、检查项目...</text>
    </view>

    <!-- 未登录提示 -->
    <AuthPrompt 
      v-if="!userStore.token"
      title="登录以使用完整功能"
      description="登录后可管理慢病、记录用药、监测健康"
      icon="🔐"
      theme="primary"
      size="medium"
    />

    <!-- ─── 通知弹层 ─── -->
    <view v-if="showNotifications" class="noti-mask" @click="toggleNotifications">
      <view class="noti-panel" @click.stop>
        <view class="noti-head">
          <text class="noti-head-title">消息通知</text>
          <view @click="toggleNotifications"><text class="noti-close">✕</text></view>
        </view>
        <scroll-view scroll-y class="noti-list">
          <view v-for="item in latestNotifications" :key="item.id" class="noti-row" @click="handleNotiClick(item)">
            <view class="noti-dot" :class="item.type === 'revisit' ? 'dot-green' : 'dot-blue'"></view>
            <view class="noti-body">
              <view class="noti-member" v-if="item.member_nickname">
                <text class="member-label">{{ item.member_nickname }}</text>
              </view>
              <text class="noti-name">{{ item.title }}</text>
              <text class="noti-sub">{{ item.content }}</text>
              <text class="noti-time">{{ formatNotiTime(item.created_at) }}</text>
            </view>
          </view>
          <view v-if="latestNotifications.length === 0" class="noti-empty"><text>暂无通知</text></view>
          <view class="noti-footer" v-if="latestNotifications.length > 0" @click="goToNotifications">
            <text class="noti-more">查看全部消息</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- ─── 我的慢病 ─── -->
    <view class="card" v-if="diseaseList.length > 0">
      <view class="card-head">
        <view class="card-head-left">
          <view class="card-icon-wrap icon-pink">
            <text class="card-icon">📊</text>
          </view>
          <text class="card-title">我的慢病</text>
        </view>
        <view class="card-action" @click="goToDisease">
          <text class="action-text">管理</text>
          <text class="arrow">›</text>
        </view>
      </view>
      <view class="disease-tags">
        <view
          v-for="d in diseaseList"
          :key="d.id"
          class="d-tag"
          :class="getDiseaseClass(d.name)"
          @click="goToDisease"
        >
          <text class="d-tag-name">{{ d.name }}</text>
        </view>
      </view>
    </view>

    <!-- ─── 今日用药 ─── -->
    <view class="card" v-if="todayMeds.length > 0">
      <view class="card-head">
        <view class="card-head-left">
          <view class="card-icon-wrap icon-blue">
            <text class="card-icon">💊</text>
          </view>
          <text class="card-title">今日用药</text>
        </view>
        <view class="card-action" @click="goToMedication">
          <text class="action-text">查看全部</text>
          <text class="arrow">›</text>
        </view>
      </view>
      <view>
        <view v-for="(med, idx) in todayMeds.slice(0,4)" :key="idx" class="med-row">
          <view class="med-dot" :class="med.status === 'taken' ? 'dot-gray' : 'dot-blue'"></view>
          <view class="med-info">
            <text class="med-name" :class="{ 'med-taken': med.status === 'taken' }">{{ med.plan_name }}</text>
            <text class="med-dosage">{{ med.dosage }}・{{ med.timing }}</text>
          </view>
          <view v-if="med.status !== 'taken'" class="med-tag-pending">
            <text>待服用</text>
          </view>
          <view v-else class="med-tag-done">
            <text>已服用</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ─── 最新监测 ─── -->
    <view class="card" v-if="hasAnyMonitorData">
      <view class="card-head">
        <view class="card-head-left">
          <view class="card-icon-wrap icon-purple">
            <text class="card-icon">📈</text>
          </view>
          <text class="card-title">最新监测</text>
        </view>
        <view class="card-action" @click="goToMonitor">
          <text class="action-text">查看全部</text>
          <text class="arrow">›</text>
        </view>
      </view>
      <view class="monitor-grid">
        <view class="monitor-item" @click="goToMonitor">
          <view class="monitor-icon-wrap bg-red-soft">
            <text class="monitor-emoji">❤️</text>
          </view>
          <text class="monitor-label">血压</text>
          <view class="monitor-value-row">
            <text class="monitor-value">{{ monitorData.blood_pressure.value || '--' }}</text>
            <text class="monitor-unit" v-if="monitorData.blood_pressure.value">mmHg</text>
          </view>
          <text class="monitor-time">{{ monitorData.blood_pressure.time || '暂无数据' }}</text>
        </view>
        <view class="monitor-item" @click="goToMonitor">
          <view class="monitor-icon-wrap bg-blue-soft">
            <text class="monitor-emoji">💧</text>
          </view>
          <text class="monitor-label">血糖</text>
          <view class="monitor-value-row">
            <text class="monitor-value">{{ monitorData.blood_sugar.value || '--' }}</text>
            <text class="monitor-unit" v-if="monitorData.blood_sugar.value">mmol/L</text>
          </view>
          <text class="monitor-time">{{ monitorData.blood_sugar.time || '暂无数据' }}</text>
        </view>
        <view class="monitor-item" @click="goToMonitor">
          <view class="monitor-icon-wrap bg-green-soft">
            <text class="monitor-emoji">⚖️</text>
          </view>
          <text class="monitor-label">体重</text>
          <view class="monitor-value-row">
            <text class="monitor-value">{{ monitorData.weight.value || '--' }}</text>
            <text class="monitor-unit" v-if="monitorData.weight.value">kg</text>
          </view>
          <text class="monitor-time">{{ monitorData.weight.time || '暂无数据' }}</text>
        </view>
        <view class="monitor-item" @click="goToMonitor">
          <view class="monitor-icon-wrap bg-yellow-soft">
            <text class="monitor-emoji">⚡</text>
          </view>
          <text class="monitor-label">心率</text>
          <view class="monitor-value-row">
            <text class="monitor-value">{{ monitorData.heart_rate.value || '--' }}</text>
            <text class="monitor-unit" v-if="monitorData.heart_rate.value">次/分</text>
          </view>
          <text class="monitor-time">{{ monitorData.heart_rate.time || '暂无数据' }}</text>
        </view>
      </view>
    </view>

    <!-- ─── 待办提醒 ─── -->
    <view class="card" v-if="latestNotifications.length > 0">
      <view class="card-head">
        <view class="card-head-left">
          <view class="card-icon-wrap icon-orange">
            <text class="card-icon">⏰</text>
          </view>
          <text class="card-title">待办提醒</text>
        </view>
        <view class="card-action" @click="goToNotifications">
          <text class="action-text">查看全部</text>
          <text class="arrow">›</text>
        </view>
      </view>
      <view v-for="item in latestNotifications.slice(0, 3)" :key="item.id" class="todo-row" @click="handleNotiClick(item)">
        <view class="todo-icon-box" :class="item.type === 'revisit' ? 'date-purple' : 'date-blue'">
          <text class="todo-icon">{{ item.type === 'revisit' ? '📅' : '💊' }}</text>
        </view>
        <view class="todo-content">
          <view class="todo-member" v-if="item.member_nickname">
            <text class="todo-member-tag">{{ item.member_nickname }}</text>
          </view>
          <text class="todo-name">{{ item.title }}</text>
          <text class="todo-desc">{{ item.content }}</text>
        </view>
        <text class="todo-arrow">›</text>
      </view>
    </view>

    <!-- ─── 实用工具 ─── -->
    <view class="section-title-wrap">
      <text class="section-title">实用工具</text>
    </view>
    <view class="more-grid-v2">
      <view class="more-item-v2" @click="navigateToRecordList">
        <view class="more-icon-container bg-blue-light">
          <view class="icon-v2 icon-record-v2">
            <view class="doc-body">
              <view class="doc-line"></view>
              <view class="doc-line"></view>
              <view class="doc-line short"></view>
            </view>
          </view>
        </view>
        <text class="more-label">病历管理</text>
      </view>
      
      <view class="more-item-v2" @click="goToReport">
        <view class="more-icon-container bg-orange-light">
          <view class="icon-v2 icon-report-v2">
            <view class="report-split">
              <view class="split-left">
                <view class="dot"></view>
                <view class="dot"></view>
                <view class="dot"></view>
              </view>
              <view class="split-right">
                <view class="dot"></view>
                <view class="dot"></view>
                <view class="dot"></view>
              </view>
            </view>
          </view>
        </view>
        <text class="more-label">检查报告</text>
      </view>
      
      <view class="more-item-v2" @click="goToRevisit">
        <view class="more-icon-container bg-purple-light">
          <view class="icon-v2 icon-revisit-v2">
            <view class="toggle-track">
              <view class="toggle-thumb"></view>
            </view>
          </view>
        </view>
        <text class="more-label">复诊管理</text>
      </view>
      
      <view class="more-item-v2" @click="goToTrends">
        <view class="more-icon-container bg-cyan-light">
          <view class="icon-v2 icon-monitor-v2">
            <view class="ecg-line">
              <view class="peak"></view>
            </view>
          </view>
        </view>
        <text class="more-label">指标监测</text>
      </view>
      
      <view class="more-item-v2" @click="goToDisease">
        <view class="more-icon-container bg-red-light">
          <view class="icon-v2 icon-disease-v2">
            <view class="ecg-wave">
              <view class="ecg-base"></view>
              <view class="ecg-up"></view>
              <view class="ecg-down"></view>
            </view>
          </view>
        </view>
        <text class="more-label">慢病管理</text>
      </view>
      
      <view class="more-item-v2" @click="goToMedicationGuide">
        <view class="more-icon-container bg-teal-light">
          <view class="icon-v2 icon-med-guide-v2">
            <view class="pill-capsule">
              <view class="pill-top"></view>
              <view class="pill-bottom"></view>
            </view>
          </view>
        </view>
        <text class="more-label">药品说明</text>
      </view>
    </view>

    <!-- 底部留白：避免内容被 TabBar 遮挡 -->
    <view class="safe-bottom" />
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="0" />
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useMemberStore } from '@/stores/member'
import { getDiseases, getHealthReadings } from '@/api/patient'
import { getDailyTasks, getStats } from '@/api/medication'
import { getNotifications, getUnreadNotificationCount, getPatientDynamicNotifications } from '@/api/notification'
import { checkLoginWithRedirect } from '@/utils/auth'
import { onShow } from '@dcloudio/uni-app'
import AuthPrompt from '@/components/AuthPrompt.vue'
import CustomTabBar from '@/components/tabbar/CustomTabBar.vue'

const userStore = useUserStore()
const memberStore = useMemberStore()
const diseaseList = ref<any[]>([])
const showNotifications = ref(false)
const showMemberPanel = ref(false)
const todayMeds = ref<any[]>([])
const unreadNotificationCount = ref(0)
const latestNotifications = ref<NotificationItem[]>([])

interface MonitorItem {
  value: string
  time: string
}
const monitorData = ref<Record<string, MonitorItem>>({
  blood_pressure: { value: '', time: '' },
  blood_sugar:    { value: '', time: '' },
  weight:         { value: '', time: '' },
  heart_rate:     { value: '', time: '' }
})

const loadNotificationCount = async () => {
  if (!userStore.token) { unreadNotificationCount.value = 0; return }
  try {
    const res: any = await getUnreadNotificationCount()
    unreadNotificationCount.value = res.unread_count || 0
  } catch { unreadNotificationCount.value = 0 }
}

const loadLatestNotifications = async () => {
  if (!userStore.token) { latestNotifications.value = []; return }
  try {
    const res = await getNotifications({ 
      all_members: true, 
      is_handled: false,
      limit: 5 
    })
    latestNotifications.value = res.items || []
  } catch { latestNotifications.value = [] }
}

const currentMemberAvatar = computed(() => {
  return memberStore.currentMember?.avatar_url || null
})

const currentMemberInitial = computed(() => {
  const nickname = memberStore.currentMember?.nickname || '用'
  return nickname.charAt(0).toUpperCase()
})

const allMembers = computed(() => {
  return memberStore.members
})

const selectMember = async (memberId: string) => {
  if (memberId === memberStore.currentMember?.id) {
    closeMemberPanel()
    return
  }
  
  await memberStore.switchMember(memberId)
  closeMemberPanel()
  
  const newMemberId = memberStore.currentMember?.id
  loadMyDiseases(newMemberId)
  loadTodayMeds(newMemberId)
  loadMonitorData(newMemberId)
}

const toggleMemberPanel = () => {
  showMemberPanel.value = !showMemberPanel.value
}

const closeMemberPanel = () => {
  showMemberPanel.value = false
}

const hasAnyMonitorData = computed(() => {
  return Object.values(monitorData.value).some(item => item.value && item.value !== '')
})

const checkLogin = (targetUrl?: string) => {
  return checkLoginWithRedirect(targetUrl)
}

const loadMyDiseases = async (memberId?: string) => {
  if (!userStore.token) { diseaseList.value = []; return }
  try {
    const res: any = await getDiseases(memberId)
    diseaseList.value = Array.isArray(res) ? res : (res?.data || [])
  } catch { diseaseList.value = [] }
}

const loadTodayMeds = async (memberId?: string) => {
  if (!userStore.token) { todayMeds.value = []; return }
  try {
    const today = new Date().toISOString().split('T')[0]
    const res: any = await getDailyTasks(today, memberId)
    todayMeds.value = Array.isArray(res) ? res : []
  } catch { todayMeds.value = [] }
}

const formatMonitorTime = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  const today = new Date()
  const isToday = d.toDateString() === today.toDateString()
  const hm = `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
  if (isToday) return `今天 ${hm}`
  const mm = String(d.getMonth()+1).padStart(2,'0')
  const dd = String(d.getDate()).padStart(2,'0')
  return `${mm}-${dd} ${hm}`
}

const loadMonitorData = async (memberId?: string) => {
  if (!userStore.token) return
  const types = ['blood_pressure', 'blood_sugar', 'weight', 'heart_rate'] as const
  await Promise.all(types.map(async (type) => {
    try {
      const res: any = await getHealthReadings(type, memberId)
      const arr = Array.isArray(res) ? res : []
      if (arr.length === 0) {
        monitorData.value[type] = { value: '', time: '' }
        return
      }
      const last = arr[arr.length - 1]
      let value = ''
      if (type === 'blood_pressure') {
        value = last.value_2 != null ? `${last.value_1}/${last.value_2}` : `${last.value_1}`
      } else {
        value = `${last.value_1}`
      }
      monitorData.value[type] = {
        value,
        time: formatMonitorTime(last.recorded_at)
      }
    } catch {
      monitorData.value[type] = { value: '', time: '' }
    }
  }))
}

const getDiseaseClass = (name: string) => {
  if (!name) return 'tag-default'
  if (name.includes('糖尿病')) return 'tag-green'
  if (name.includes('高血压')) return 'tag-orange'
  if (name.includes('高脂') || name.includes('血脂')) return 'tag-blue'
  return 'tag-pink'
}

const formatDay = (dateStr: string) => {
  if (!dateStr) return '--'
  return new Date(dateStr).getDate().toString()
}

const formatMonth = (dateStr: string) => {
  if (!dateStr) return ''
  return (new Date(dateStr).getMonth() + 1) + '月'
}

const formatNotiTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

const handleSearch = () => {
  uni.showToast({ title: '搜索功能开发中', icon: 'none' })
}

const toggleNotifications = () => {
  if (!checkLogin()) return
  showNotifications.value = !showNotifications.value
}

const handleNotiClick = (item: any) => {
  showNotifications.value = false
  if (item.type === 'revisit') safeNavigate({ url: '/pages/revisit/plan' })
  else uni.switchTab({ url: '/pages/medication/index' })
}

const goToDisease = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/disease/manage' }) }
const goToMedication = () => { if (!checkLogin()) return; uni.switchTab({ url: '/pages/medication/index' }) }
const goToMonitor = () => { if (!checkLogin()) return; uni.switchTab({ url: '/pages/monitor/index' }) }
const goToReport = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/report/report' }) }
const goToRevisit = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/revisit/plan' }) }
const goToTrends = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/report/trends' }) }
const goToMember = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/member/list' }) }
const goToNotifications = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/notification/index' }) }
const navigateToRecordList = () => { if (!checkLogin()) return; safeNavigate({ url: '/pages/medical-record/list' }) }
const goToMedicationGuide = () => { safeNavigate({ url: '/pages/medication-guide/category' }) }

onShow(async () => {
  if (!userStore.token) return
  
  await memberStore.loadMembers()
  
  const currentMemberId = memberStore.currentMember?.id
  
  loadMyDiseases(currentMemberId)
  loadNotificationCount()
  loadLatestNotifications()
  loadTodayMeds(currentMemberId)
  loadMonitorData(currentMemberId)
})
</script>

<style>
/* ── 基础布局 ── */
.page-wrap {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  display: flex;
  flex-direction: column;
  padding-bottom: 120rpx;
}
.safe-bottom {
  height: 0;
  pointer-events: none;
}

/* ── 顶部 ── */
.top-bar-v2 {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 100rpx 40rpx 30rpx;
  background-color: transparent;
}

/* 左侧用户信息 */
.user-info-section {
  display: flex;
  align-items: center;
}

.avatar-wrapper {
  position: relative;
  width: 90rpx;
  height: 90rpx;
  margin-right: 20rpx;
}

.user-avatar, .user-avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #E6F4FF;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4rpx solid #FFFFFF;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.avatar-text {
  font-size: 36rpx;
  font-weight: bold;
  color: #1890FF;
}

.member-switch-dot {
  position: absolute;
  right: -4rpx;
  bottom: -4rpx;
  width: 32rpx;
  height: 32rpx;
  background-color: #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.icon-arrow-down-s {
  width: 12rpx;
  height: 12rpx;
  border: 3rpx solid #909399;
  border-top: none;
  border-left: none;
  transform: translateY(-2rpx) rotate(45deg);
}

.user-text-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #1a1a1a;
  line-height: 1.2;
}

.user-role {
  font-size: 22rpx;
  color: #909399;
  margin-top: 4rpx;
}

/* 右侧通知 */
.notice-section {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notice-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notice-bell-emoji {
  font-size: 44rpx;
  line-height: 1;
}

.notice-badge {
  position: absolute;
  top: -8rpx;
  right: -16rpx;
  background-color: #ef4444;
  min-width: 32rpx;
  height: 32rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3rpx solid #ffffff;
  padding: 0 6rpx;
}

.badge-text {
  color: #FFFFFF;
  font-size: 20rpx;
  font-weight: bold;
}

/* ── 成员面板 ── */
.member-panel-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 999;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 100px;
}

.member-panel {
  width: 92%;
  max-width: 360px;
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.member-panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px 14px;
  border-bottom: 1px solid #f1f5f9;
}

.member-panel-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
}

.member-panel-close {
  width: 28px;
  height: 28px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.member-panel-close text {
  font-size: 14px;
  color: #64748b;
}

.member-scroll {
  width: 100%;
  white-space: nowrap;
  padding: 16px 0;
}

.member-cards-wrap {
  display: inline-flex;
  align-items: flex-start;
  padding: 0 16px;
  gap: 14px;
}

.member-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 68px;
  padding: 12px 8px 10px;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 22px;
  border: 2px solid transparent;
  transition: all 0.25s ease;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.member-card.is-selected {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.member-avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-avatar-silhouette {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-top: 8px;
}

.silhouette-head {
  width: 18px;
  height: 18px;
  background: #ffffff;
  border-radius: 50%;
  margin-bottom: 3px;
}

.silhouette-body {
  width: 28px;
  height: 14px;
  background: #ffffff;
  border-radius: 14px 14px 0 0;
}

.member-nickname {
  font-size: 12px;
  color: #757575;
  text-align: center;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-card.manage-card .member-avatar-circle {
  background: #eff6ff;
  border: 2px solid #93c5fd;
}

.gear-emoji {
  font-size: 24px;
  line-height: 1;
  filter: grayscale(0);
}

/* ── 搜索栏 ── */
.search-bar {
  margin: 0 16px 16px;
  background: #FFFFFF;
  border: 1.5px solid rgba(148, 163, 184, 0.2);
  border-radius: 24px;
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.02);
  transition: all 0.2s ease;
}

.search-bar:active {
  background: #FAFBFC;
  border-color: var(--color-primary);
  box-shadow: 0 2px 12px rgba(59, 130, 246, 0.1);
}

.search-icon-wrap {
  width: 16px;
  height: 16px;
  position: relative;
  flex-shrink: 0;
}

.search-circle {
  width: 10px;
  height: 10px;
  border: 2px solid #94a3b8;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
}

.search-handle {
  width: 2px;
  height: 6px;
  background: #94a3b8;
  border-radius: 1px;
  position: absolute;
  bottom: 0;
  right: 2px;
  transform: rotate(-45deg);
  transform-origin: bottom center;
}

.search-placeholder { font-size: 14px; color: #94a3b8; }

/* ── 通知弹层 ── */
.noti-mask {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 1000;
  display: flex;
  justify-content: center;
  padding-top: 100px;
  align-items: flex-start;
}
.noti-panel {
  width: 90%;
  background: white;
  border-radius: 20px;
  max-height: 65vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}
.noti-head {
  padding: 18px 20px 14px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.noti-head-title { font-size: 16px; font-weight: 700; color: #1e293b; }
.noti-close { font-size: 20px; color: #94a3b8; }
.noti-list { flex: 1; }
.noti-row {
  display: flex;
  align-items: flex-start;
  padding: 14px 20px;
  gap: 12px;
  border-bottom: 1px solid #f8fafc;
}
.noti-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.dot-green { background: #22c55e; }
.dot-red { background: #ef4444; }
.dot-blue { background: #3b82f6; }
.noti-body { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.noti-member { margin-bottom: 2px; }
.member-label {
  display: inline-block;
  font-size: 11px;
  color: #0ea5e9;
  background: #e0f2fe;
  padding: 2px 8px;
  border-radius: 10px;
}
.noti-name { font-size: 15px; font-weight: 600; color: #1e293b; }
.noti-sub { font-size: 13px; color: #64748b; }
.noti-time { font-size: 12px; color: #94a3b8; }
.noti-empty { padding: 40px 0; text-align: center; }
.noti-empty text { color: #94a3b8; font-size: 14px; }
.noti-footer {
  padding: 14px 20px;
  text-align: center;
  border-top: 1px solid #f1f5f9;
}
.noti-more {
  font-size: 14px;
  color: #0ea5e9;
  font-weight: 500;
}

/* ── 通用卡片 ── */
.card {
  margin: 0 16px 12px;
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.6));
}

.card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1rpx;
  background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.04), transparent);
}
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.card-head-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-icon-wrap {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-pink { background: #fce7f3; }
.icon-blue { background: #dbeafe; }
.icon-purple { background: #d1fae5; }
.icon-orange { background: #ffedd5; }
.card-icon { font-size: 18px; }
.card-title { font-size: 16px; font-weight: 700; color: #1e293b; }
.card-action { display: flex; align-items: center; gap: 2px; }
.action-text { font-size: 13px; color: #0ea5e9; }
.arrow { font-size: 16px; color: #0ea5e9; }
.card-empty { padding: 10px 0 4px; }
.empty-tip { font-size: 13px; color: #94a3b8; }

/* ── 慢病标签 ── */
.disease-tags { display: flex; gap: 10px; flex-wrap: wrap; }
.d-tag {
  display: flex;
  align-items: center;
  padding: 8px 14px;
  border-radius: 14px;
  transition: transform 0.2s ease;
}
.d-tag:active {
  transform: scale(0.96);
}
.d-tag-name { font-size: 14px; font-weight: 600; }
.tag-green { background: #f0fdf4; }
.tag-green .d-tag-name { color: #15803d; }
.tag-orange { background: #fff7ed; }
.tag-orange .d-tag-name { color: #c2410c; }
.tag-blue { background: #eff6ff; }
.tag-blue .d-tag-name { color: #1d4ed8; }
.tag-pink { background: #fdf2f8; }
.tag-pink .d-tag-name { color: #be185d; }
.tag-default { background: #f8fafc; }
.tag-default .d-tag-name { color: #64748b; }

/* ── 今日用药 ── */
.med-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f8fafc;
}
.med-row:last-child { border-bottom: none; }
.med-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-blue { background: #3b82f6; }
.dot-gray { background: #cbd5e1; }
.med-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.med-name { font-size: 15px; font-weight: 600; color: #1e293b; }
.med-taken { color: #94a3b8 !important; }
.med-dosage { font-size: 12px; color: #94a3b8; }
.med-tag-pending {
  background: #eff6ff;
  border-radius: 8px;
  padding: 3px 8px;
}
.med-tag-pending text { font-size: 12px; color: #3b82f6; }
.med-tag-done {
  background: #f0fdf4;
  border-radius: 8px;
  padding: 3px 8px;
}
.med-tag-done text { font-size: 12px; color: #22c55e; }

/* ── 最新监测 2×2 ── */
.monitor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.monitor-item {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
  border-radius: 14px;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: 0 3rpx 12rpx rgba(0, 0, 0, 0.08), 0 10rpx 32rpx rgba(0, 0, 0, 0.10), 0 0 0 1rpx rgba(0, 0, 0, 0.05);
  border: 1rpx solid rgba(120, 130, 150, 0.15);
  position: relative;
  overflow: hidden;
}

.monitor-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.5));
}
.monitor-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}
.bg-red-soft { background: #fff0f0; }
.bg-blue-soft { background: #eef6ff; }
.bg-green-soft { background: #f0fdf4; }
.bg-yellow-soft { background: #fffbeb; }
.monitor-emoji { font-size: 18px; }
.monitor-label { font-size: 12px; color: #94a3b8; }
.monitor-value-row { display: flex; align-items: baseline; gap: 3px; }
.monitor-value { font-size: 22px; font-weight: 800; color: #1e293b; }
.monitor-unit { font-size: 11px; color: #64748b; }
.monitor-time { font-size: 11px; color: #94a3b8; }

/* ── 待办提醒 ── */
.todo-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 0;
  border-bottom: 1px solid #f8fafc;
}
.todo-row:last-child { border-bottom: none; }
.todo-icon-box {
  width: 44px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.todo-icon { font-size: 22px; }
.todo-date-box {
  width: 44px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.date-purple { background: #0ea5e9; }
.date-blue { background: #3b82f6; }
.todo-day { font-size: 18px; font-weight: 800; color: white; line-height: 1.2; }
.todo-month { font-size: 11px; color: rgba(255,255,255,0.85); }
.todo-content { flex: 1; display: flex; flex-direction: column; gap: 3px; }
.todo-member { margin-bottom: 2px; }
.todo-member-tag {
  display: inline-block;
  font-size: 11px;
  color: #0ea5e9;
  background: #e0f2fe;
  padding: 2px 8px;
  border-radius: 10px;
}
.todo-name { font-size: 15px; font-weight: 600; color: #1e293b; }
.todo-desc { font-size: 12px; color: #64748b; }
.todo-arrow { font-size: 20px; color: #cbd5e1; }

/* ── 实用工具标题 ── */
.section-title-wrap {
  padding: 16px 20px 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #374151;
  letter-spacing: 0.5px;
}

/* ── 实用工具 ── */
.more-grid-v2 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding: 0 16px;
  gap: 16px;
  margin-bottom: 24px;
}

.more-item-v2 {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  transition: all 0.2s ease;
}

.more-item-v2:active {
  transform: scale(0.95);
}

.more-icon-container {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
}

/* 统一中性背景 */
.bg-blue-light,
.bg-orange-light,
.bg-purple-light,
.bg-cyan-light,
.bg-red-light,
.bg-teal-light {
  background: #f3f4f6;
}

/* 极简图标样式 */
.icon-v2 {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 慢病管理图标 - 心电图波形 */
.icon-disease-v2 .ecg-wave {
  width: 48rpx;
  height: 36rpx;
  position: relative;
  display: flex;
  align-items: center;
}

.icon-disease-v2 .ecg-base {
  position: absolute;
  bottom: 16rpx;
  left: 0;
  right: 0;
  height: 3rpx;
  background-color: #ef4444;
}

.icon-disease-v2 .ecg-up {
  position: absolute;
  left: 12rpx;
  bottom: 16rpx;
  width: 0;
  height: 0;
  border-left: 8rpx solid transparent;
  border-right: 8rpx solid transparent;
  border-bottom: 20rpx solid #ef4444;
}

.icon-disease-v2 .ecg-down {
  position: absolute;
  left: 20rpx;
  bottom: 0;
  width: 3rpx;
  height: 16rpx;
  background-color: #ef4444;
}

/* 药品说明图标 - 胶囊 */
.icon-med-guide-v2 .pill-capsule {
  width: 36rpx;
  height: 18rpx;
  position: relative;
  border-radius: 9rpx;
  overflow: hidden;
}

.icon-med-guide-v2 .pill-top {
  width: 50%;
  height: 100%;
  background-color: #14b8a6;
  position: absolute;
  left: 0;
  top: 0;
}

.icon-med-guide-v2 .pill-bottom {
  width: 50%;
  height: 100%;
  background-color: #0d9488;
  position: absolute;
  right: 0;
  top: 0;
}

/* 病历管理图标 */
.icon-record-v2 .doc-body {
  width: 24rpx;
  height: 32rpx;
  background-color: #3b82f6;
  border-radius: 4rpx;
  padding: 6rpx 4rpx;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.icon-record-v2 .doc-line {
  width: 100%;
  height: 3rpx;
  background-color: #ffffff;
  border-radius: 1rpx;
}
.icon-record-v2 .doc-line.short {
  width: 60%;
}

/* 检查报告图标 */
.icon-report-v2 .report-split {
  display: flex;
  gap: 4rpx;
}
.icon-report-v2 .split-left, .icon-report-v2 .split-right {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.icon-report-v2 .dot {
  width: 12rpx;
  height: 6rpx;
  background-color: #f97316;
  border-radius: 2rpx;
}

/* 复诊管理图标 */
.icon-revisit-v2 .toggle-track {
  width: 36rpx;
  height: 20rpx;
  background-color: #8b5cf6;
  border-radius: 10rpx;
  position: relative;
  display: flex;
  align-items: center;
  padding: 0 4rpx;
}
.icon-revisit-v2 .toggle-thumb {
  width: 12rpx;
  height: 12rpx;
  background-color: #ffffff;
  border-radius: 50%;
  position: absolute;
  right: 4rpx;
}

/* 指标监测图标 */
.icon-monitor-v2 .ecg-line {
  width: 36rpx;
  height: 24rpx;
  border-bottom: 3rpx solid #ea580c;
  position: relative;
}
.icon-monitor-v2 .peak {
  width: 20rpx;
  height: 16rpx;
  border: 3rpx solid #ea580c;
  border-bottom: none;
  border-radius: 4rpx 4rpx 0 0;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
}

.icon-monitor-v2 .peak::before {
  content: '';
  position: absolute;
  width: 3rpx;
  height: 10rpx;
  background-color: #ea580c;
  top: 4rpx;
  left: 4rpx;
}

.more-label {
  font-size: 22rpx;
  font-weight: 600;
  color: #374151;
  text-align: center;
}

/* ── 其他辅助样式 ── */
.safe-bottom {
  height: 0;
  pointer-events: none;
}
</style>
