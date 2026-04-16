<template>
  <view class="page-wrap">
    <view class="filter-bar">
      <view class="filter-tabs">
        <view 
          class="filter-tab" 
          :class="{ active: currentFilter === 'all' }" 
          @click="setFilter('all')"
        >
          <text>全部</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentFilter === 'unread' }" 
          @click="setFilter('unread')"
        >
          <text>未读</text>
          <view class="badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentFilter === 'health' }" 
          @click="setFilter('health')"
        >
          <text>健康提醒</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentFilter === 'system' }" 
          @click="setFilter('system')"
        >
          <text>系统通知</text>
        </view>
      </view>
      <view class="action-btn" @click="markAllRead" v-if="unreadCount > 0">
        <text>全部已读</text>
      </view>
    </view>

    <scroll-view 
      scroll-y 
      class="notification-list" 
      @scrolltolower="loadMore"
      :refresher-enabled="true"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-for="item in notifications" :key="item.id" class="notification-item" @click="handleItemClick(item)">
        <view class="item-header">
          <view class="member-tag" v-if="item.member_nickname">
            <text class="member-icon">{{ getMemberIcon(item.member_relation) }}</text>
            <text class="member-name">{{ item.member_nickname }}</text>
          </view>
          <view class="item-time">
            <text>{{ formatTime(item.created_at) }}</text>
          </view>
        </view>
        <view class="item-content">
          <view class="item-title-row">
            <view class="type-dot" :class="getTypeClass(item.type)"></view>
            <text class="item-title">{{ item.title }}</text>
            <view class="unread-dot" v-if="!item.is_read"></view>
          </view>
          <text class="item-text">{{ item.content }}</text>
        </view>
      </view>

      <view class="loading-more" v-if="isLoading">
        <text>加载中...</text>
      </view>

      <view class="empty-state" v-if="!isLoading && notifications.length === 0">
        <view class="empty-icon">
          <text>📭</text>
        </view>
        <text class="empty-text">暂无通知</text>
      </view>

      <view class="no-more" v-if="!isLoading && !hasMore && notifications.length > 0">
        <text>没有更多了</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { 
  getNotifications, 
  markAllNotificationsAsRead, 
  markNotificationAsRead,
  type NotificationItem 
} from '@/api/notification'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const notifications = ref<NotificationItem[]>([])
const currentFilter = ref('all')
const unreadCount = ref(0)
const isLoading = ref(false)
const isRefreshing = ref(false)
const hasMore = ref(true)
const page = ref(0)
const pageSize = 20

const setFilter = (filter: string) => {
  currentFilter.value = filter
  page.value = 0
  hasMore.value = true
  notifications.value = []
  loadNotifications()
}

const loadNotifications = async () => {
  if (!userStore.token || isLoading.value) return
  
  isLoading.value = true
  try {
    const params: any = {
      skip: page.value * pageSize,
      limit: pageSize,
      all_members: true
    }
    
    if (currentFilter.value === 'unread') {
      params.is_read = false
    } else if (currentFilter.value === 'health' || currentFilter.value === 'system') {
      params.category = currentFilter.value
    }
    
    const res = await getNotifications(params)
    const items = res.items || []
    
    if (page.value === 0) {
      notifications.value = items
    } else {
      notifications.value = [...notifications.value, ...items]
    }
    
    unreadCount.value = res.unread_count || 0
    hasMore.value = items.length >= pageSize
  } catch (error) {
    console.error('加载通知失败:', error)
  } finally {
    isLoading.value = false
    isRefreshing.value = false
  }
}

const loadMore = () => {
  if (!hasMore.value || isLoading.value) return
  page.value++
  loadNotifications()
}

const onRefresh = () => {
  isRefreshing.value = true
  page.value = 0
  hasMore.value = true
  loadNotifications()
}

const markAllRead = async () => {
  try {
    await markAllNotificationsAsRead()
    notifications.value.forEach(item => {
      item.is_read = true
    })
    unreadCount.value = 0
    uni.showToast({ title: '已全部标记为已读', icon: 'success' })
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const handleItemClick = async (item: NotificationItem) => {
  if (!item.is_read) {
    try {
      await markNotificationAsRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
  
  if (item.type === 'revisit') {
    uni.navigateTo({ url: '/pages/revisit/plan' })
  } else if (item.type === 'medication') {
    uni.switchTab({ url: '/pages/medication/index' })
  }
}

const getMemberIcon = (relation?: string) => {
  if (!relation) return '👤'
  const icons: Record<string, string> = {
    '自己': '😊',
    '父亲': '👨',
    '母亲': '👩',
    '丈夫': '👨',
    '妻子': '👩',
    '儿子': '👦',
    '女儿': '👧',
    '爷爷': '👴',
    '奶奶': '👵',
    '外公': '👴',
    '外婆': '👵'
  }
  return icons[relation] || '👤'
}

const getTypeClass = (type: string) => {
  const classes: Record<string, string> = {
    'revisit': 'dot-purple',
    'medication': 'dot-blue',
    'system': 'dot-orange',
    'health': 'dot-green'
  }
  return classes[type] || 'dot-gray'
}

const formatTime = (timeStr: string) => {
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

onShow(() => {
  page.value = 0
  hasMore.value = true
  notifications.value = []
  loadNotifications()
})
</script>

<style>
.page-wrap {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 6px 12px;
  border-radius: 16px;
  background: #f5f7fa;
  position: relative;
}

.filter-tab.active {
  background: #0ea5e9;
}

.filter-tab.active text {
  color: #ffffff;
}

.filter-tab text {
  font-size: 13px;
  color: #64748b;
}

.filter-tab .badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background: #ef4444;
  color: white;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 16px;
  background: #eff6ff;
}

.action-btn text {
  font-size: 13px;
  color: #3b82f6;
}

.notification-list {
  height: calc(100vh - 60px);
  padding: 12px 16px;
}

.notification-item {
  background: #ffffff;
  border-radius: 16px;
  padding: 14px 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.member-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f0f9ff;
  padding: 4px 10px;
  border-radius: 12px;
}

.member-icon {
  font-size: 14px;
}

.member-name {
  font-size: 12px;
  color: #0284c7;
  font-weight: 500;
}

.item-time text {
  font-size: 12px;
  color: #94a3b8;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-purple { background: #0ea5e9; }
.dot-blue { background: #3b82f6; }
.dot-orange { background: #f97316; }
.dot-green { background: #22c55e; }
.dot-gray { background: #94a3b8; }

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  flex-shrink: 0;
}

.item-text {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  padding-left: 16px;
}

.loading-more,
.no-more {
  text-align: center;
  padding: 20px 0;
}

.loading-more text,
.no-more text {
  font-size: 13px;
  color: #94a3b8;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: #94a3b8;
}
</style>
