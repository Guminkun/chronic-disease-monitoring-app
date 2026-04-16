<template>
  <view class="history-page">
    <PageHeader title="历史用药" />

    <!-- 统计卡片 -->
    <view class="stats-card">
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ stats.totalDays }}</text>
          <text class="stat-label">记录天数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.takenCount }}</text>
          <text class="stat-label">已服用</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value highlight">{{ stats.adherenceRate }}%</text>
          <text class="stat-label">依从率</text>
        </view>
      </view>
    </view>

    <!-- 时间筛选 -->
    <view class="filter-section">
      <view class="filter-tabs">
        <view 
          class="filter-tab" 
          :class="{ active: filterPeriod === 'week' }" 
          @click="changeFilter('week')"
        >
          <text>近7天</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterPeriod === 'month' }" 
          @click="changeFilter('month')"
        >
          <text>近30天</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterPeriod === 'all' }" 
          @click="changeFilter('all')"
        >
          <text>全部</text>
        </view>
      </view>
      
      <!-- 补卡入口 -->
      <view class="makeup-entry" @click="goToMakeup">
        <text class="makeup-icon">📝</text>
        <text class="makeup-text">漏服补卡</text>
        <text class="makeup-arrow">›</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-content" @scrolltolower="loadMore">
      <!-- 日期分组列表 -->
      <view v-for="group in groupedRecords" :key="group.date" class="date-group">
        <view class="date-header">
          <text class="date-text">{{ formatDateHeader(group.date) }}</text>
          <text class="date-weekday">{{ formatWeekday(group.date) }}</text>
        </view>

        <view v-for="record in group.records" :key="record.id" class="record-card">
          <view class="record-icon" :class="getStatusClass(record.status)">
            <text class="icon-emoji">{{ getStatusEmoji(record.status) }}</text>
          </view>
          <view class="record-main">
            <view class="record-top">
              <text class="record-name">{{ record.plan_name }}</text>
              <view class="record-status" :class="getStatusClass(record.status)">
                <text class="status-text">{{ getStatusText(record.status) }}</text>
              </view>
            </view>
            <view class="record-info">
              <text class="info-item">剂量: {{ record.dosage }}</text>
              <text class="info-divider">·</text>
              <text class="info-item">{{ formatTime(record.scheduled_time) }}</text>
            </view>
            <view v-if="record.taken_time" class="record-taken">
              <text class="taken-label">实际服用:</text>
              <text class="taken-time">{{ formatTime(record.taken_time) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="groupedRecords.length === 0 && !loading" class="empty-state">
        <view class="empty-icon">📋</view>
        <text class="empty-title">暂无用药记录</text>
        <text class="empty-desc">开始记录您的用药情况吧</text>
      </view>

      <!-- 加载更多 -->
      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-if="!hasMore && groupedRecords.length > 0" class="no-more">
        <text class="no-more-text">没有更多记录了</text>
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>
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

import { computed, ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import * as medApi from '@/api/medication'

interface MedicationRecord {
  id: number
  plan_id: number
  plan_name: string
  dosage: string
  scheduled_time: string
  taken_time: string | null
  status: 'pending' | 'taken' | 'skipped'
  skipped_reason?: string
}

interface RecordGroup {
  date: string
  records: MedicationRecord[]
}

const filterPeriod = ref<'week' | 'month' | 'all'>('week')
const loading = ref(false)
const hasMore = ref(true)
const allRecords = ref<MedicationRecord[]>([])
const currentPage = ref(0)
const pageSize = 20

const stats = ref({
  totalDays: 0,
  takenCount: 0,
  adherenceRate: 0
})

// 按日期分组
const groupedRecords = computed(() => {
  const groups: RecordGroup[] = []
  const dateMap = new Map<string, MedicationRecord[]>()
  
  allRecords.value.forEach(record => {
    const date = record.scheduled_time.split('T')[0]
    if (!dateMap.has(date)) {
      dateMap.set(date, [])
    }
    dateMap.get(date)!.push(record)
  })
  
  // 按日期降序排列
  const sortedDates = Array.from(dateMap.keys()).sort((a, b) => b.localeCompare(a))
  
  sortedDates.forEach(date => {
    const records = dateMap.get(date) || []
    // 按时间排序
    records.sort((a, b) => a.scheduled_time.localeCompare(b.scheduled_time))
    groups.push({ date, records })
  })
  
  return groups
})

const changeFilter = (period: 'week' | 'month' | 'all') => {
  filterPeriod.value = period
  currentPage.value = 0
  allRecords.value = []
  hasMore.value = true
  loadData()
}

const loadData = async () => {
  if (loading.value) return
  loading.value = true
  
  try {
    // 获取统计数据
    const statsRes: any = await medApi.getStats(filterPeriod.value === 'all' ? 'month' : filterPeriod.value)
    if (statsRes) {
      stats.value = {
        totalDays: statsRes.trend?.length || 0,
        takenCount: statsRes.taken_count || 0,
        adherenceRate: statsRes.overall_rate || 0
      }
    }
    
    // 获取历史记录 - 需要调用新的API
    await loadHistoryRecords()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadHistoryRecords = async () => {
  try {
    // 计算日期范围
    const endDate = new Date()
    let startDate = new Date()
    
    if (filterPeriod.value === 'week') {
      startDate.setDate(startDate.getDate() - 7)
    } else if (filterPeriod.value === 'month') {
      startDate.setDate(startDate.getDate() - 30)
    } else {
      startDate = new Date('2020-01-01') // 全部记录
    }
    
    // 调用后端API获取历史记录
    const res: any = await medApi.getMedicationHistory({
      start_date: formatDate(startDate),
      end_date: formatDate(endDate),
      skip: currentPage.value * pageSize,
      limit: pageSize
    })
    
    const records = Array.isArray(res?.items) ? res.items : (Array.isArray(res) ? res : [])
    
    if (records.length < pageSize) {
      hasMore.value = false
    }
    
    allRecords.value = [...allRecords.value, ...records]
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

const loadMore = () => {
  if (!hasMore.value || loading.value) return
  currentPage.value++
  loadHistoryRecords()
}

const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

const formatDateHeader = (dateStr: string) => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

const formatWeekday = (dateStr: string) => {
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (dateStr === formatDate(today)) {
    return '今天'
  } else if (dateStr === formatDate(yesterday)) {
    return '昨天'
  }
  return weekdays[date.getDay()]
}

const formatTime = (isoStr: string) => {
  if (!isoStr) return '--:--'
  try {
    const date = new Date(isoStr)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '--:--'
  }
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'taken': return 'status-taken'
    case 'skipped': return 'status-skipped'
    default: return 'status-pending'
  }
}

const getStatusEmoji = (status: string) => {
  switch (status) {
    case 'taken': return '✅'
    case 'skipped': return '⏭️'
    default: return '⏳'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'taken': return '已服用'
    case 'skipped': return '已跳过'
    default: return '待服用'
  }
}

const goToMakeup = () => {
  safeNavigate({ url: '/pages/medication/makeup' })
}

onShow(() => {
  loadData()
})
</script>

<style>
/* 页面容器 */
.history-page {
  min-height: 100vh;
  background: #f0f4ff;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.nav-bar {
  height: 100rpx;
  padding: 56rpx 32rpx 16rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 10;
  background: transparent;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.nav-back-icon {
  font-size: 48rpx;
  color: #1e293b;
  font-weight: 300;
  line-height: 1;
}

.nav-back-text {
  font-size: 28rpx;
  color: #1e293b;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1e293b;
  letter-spacing: 2rpx;
}

.nav-right {
  width: 100rpx;
}

/* 统计卡片 */
.stats-card {
  margin: 0 32rpx 24rpx;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 32rpx;
  padding: 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #1e293b;
}

.stat-value.highlight {
  color: #0ea5e9;
}

.stat-label {
  font-size: 24rpx;
  color: #64748b;
}

.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background: #e2e8f0;
}

/* 筛选区域 */
.filter-section {
  padding: 0 32rpx;
  margin-bottom: 24rpx;
  position: relative;
  z-index: 10;
}

.filter-tabs {
  display: flex;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 6rpx;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.filter-tab {
  flex: 1;
  height: 64rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 600;
  color: #64748b;
  transition: all 0.3s;
}

.filter-tab.active {
  background: #0ea5e9;
  color: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(14, 165, 233, 0.3);
}

/* 补卡入口 */
.makeup-entry {
  margin-top: 16rpx;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
}

.makeup-icon {
  font-size: 32rpx;
}

.makeup-text {
  flex: 1;
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
}

.makeup-arrow {
  font-size: 36rpx;
  color: #94a3b8;
  font-weight: 300;
}

/* 滚动内容 */
.scroll-content {
  flex: 1;
  padding: 0 32rpx;
  box-sizing: border-box;
}

/* 日期分组 */
.date-group {
  margin-bottom: 24rpx;
}

.date-header {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.date-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #1e293b;
}

.date-weekday {
  font-size: 24rpx;
  color: #64748b;
}

/* 记录卡片 */
.record-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
}

.record-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.record-icon.status-taken {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.record-icon.status-skipped {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.record-icon.status-pending {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
}

.icon-emoji {
  font-size: 28rpx;
}

.record-main {
  flex: 1;
  min-width: 0;
}

.record-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.record-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.record-status {
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.record-status.status-taken {
  background: #dcfce7;
}

.record-status.status-skipped {
  background: #fef3c7;
}

.record-status.status-pending {
  background: #e0e7ff;
}

.status-text {
  font-size: 22rpx;
  font-weight: 600;
}

.record-status.status-taken .status-text {
  color: #16a34a;
}

.record-status.status-skipped .status-text {
  color: #d97706;
}

.record-status.status-pending .status-text {
  color: #6366f1;
}

.record-info {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.info-item {
  font-size: 24rpx;
  color: #64748b;
}

.info-divider {
  color: #cbd5e1;
}

.record-taken {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 8rpx;
}

.taken-label {
  font-size: 22rpx;
  color: #94a3b8;
}

.taken-time {
  font-size: 22rpx;
  color: #16a34a;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #64748b;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx 0;
}

.loading-text {
  font-size: 26rpx;
  color: #64748b;
}

/* 没有更多 */
.no-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32rpx 0;
}

.no-more-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.5);
}
</style>
