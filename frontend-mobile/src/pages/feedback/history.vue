<template>
  <view class="container">
    <!-- 反馈列表 -->
    <view class="feedback-list" v-if="feedbackList.length > 0">
      <view 
        class="feedback-item" 
        v-for="item in feedbackList" 
        :key="item.id"
        @click="goToDetail(item.id)"
      >
        <view class="item-header">
          <view class="status-badge" :class="item.status">
            {{ getStatusText(item.status) }}
          </view>
          <text class="date">{{ formatDate(item.created_at) }}</text>
        </view>
        <view class="item-content">
          {{ item.content }}
        </view>
        <view class="item-images" v-if="item.images && item.images.length > 0">
          <image 
            v-for="(img, idx) in item.images.slice(0, 3)" 
            :key="idx"
            :src="img" 
            mode="aspectFill"
          />
          <text class="more" v-if="item.images.length > 3">+{{ item.images.length - 3 }}</text>
        </view>
        <view class="item-reply" v-if="item.reply_content">
          <view class="reply-label">管理员回复：</view>
          <view class="reply-content">{{ item.reply_content }}</view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else-if="!loading">
      <text class="empty-icon">📝</text>
      <text class="empty-text">暂无反馈记录</text>
      <button class="btn-submit" @click="goToSubmit">提交反馈</button>
    </view>

    <!-- 加载状态 -->
    <view class="loading" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore && !loading" @click="loadMore">
      <text>加载更多</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, onMounted } from 'vue'
import { getMyFeedbacks } from '@/api/feedback'
import type { Feedback, FeedbackStatus } from '@/api/feedback'

const feedbackList = ref<Feedback[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 10
const total = ref(0)

const hasMore = ref(false)

// 获取状态文本
const getStatusText = (status: FeedbackStatus) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    replied: '已回复',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

// 加载反馈列表
const loadFeedbacks = async () => {
  loading.value = true
  try {
    const res = await getMyFeedbacks({
      page: page.value,
      page_size: pageSize
    }) as any
    if (page.value === 1) {
      feedbackList.value = res.items
    } else {
      feedbackList.value = [...feedbackList.value, ...res.items]
    }
    total.value = res.total
    hasMore.value = feedbackList.value.length < res.total
  } catch (error) {
    console.error('加载反馈列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !loading.value) {
    page.value++
    loadFeedbacks()
  }
}

// 跳转到详情
const goToDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/feedback/detail?id=${id}` })
}

// 跳转到提交页面
const goToSubmit = () => {
  safeNavigate({ url: '/pages/feedback/submit' })
}

onMounted(() => {
  loadFeedbacks()
})
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 16px;
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feedback-item {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-sizing: border-box;
  width: 100%;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-badge.pending {
  background-color: #fef3c7;
  color: #d97706;
}

.status-badge.processing {
  background-color: #dbeafe;
  color: #2563eb;
}

.status-badge.replied {
  background-color: #d1fae5;
  color: #059669;
}

.status-badge.closed {
  background-color: #f1f5f9;
  color: #64748b;
}

.date {
  font-size: 12px;
  color: #94a3b8;
}

.item-content {
  font-size: 15px;
  color: #334155;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-images {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  position: relative;
}

.item-images image {
  width: 60px;
  height: 60px;
  border-radius: 6px;
}

.item-images .more {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 60px;
  height: 60px;
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-reply {
  margin-top: 12px;
  padding: 12px;
  background-color: #f0fdf4;
  border-radius: 8px;
  border-left: 3px solid #22c55e;
}

.reply-label {
  font-size: 12px;
  color: #22c55e;
  margin-bottom: 4px;
}

.reply-content {
  font-size: 14px;
  color: #334155;
  line-height: 1.5;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 24px;
}

.btn-submit {
  background-color: #3b82f6;
  color: #ffffff;
  font-size: 15px;
  padding: 12px 32px;
  border-radius: 8px;
  border: none;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
}

.load-more {
  text-align: center;
  padding: 16px;
  color: #3b82f6;
  font-size: 14px;
}
</style>
