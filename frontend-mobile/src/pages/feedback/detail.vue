<template>
  <view class="container" v-if="feedback">
    <!-- 反馈内容 -->
    <view class="section">
      <view class="section-header">
        <view class="status-badge" :class="feedback.status">
          {{ getStatusText(feedback.status) }}
        </view>
        <text class="date">{{ formatDate(feedback.created_at) }}</text>
      </view>
      <view class="content-text">{{ feedback.content }}</view>
      
      <!-- 图片列表 -->
      <view class="image-list" v-if="feedback.images && feedback.images.length > 0">
        <image 
          v-for="(img, idx) in feedback.images" 
          :key="idx"
          :src="img" 
          mode="aspectFill"
          @click="previewImage(idx)"
        />
      </view>
      
      <!-- 联系方式 -->
      <view class="contact-info" v-if="feedback.contact">
        <text class="label">联系方式：</text>
        <text class="value">{{ feedback.contact }}</text>
      </view>
    </view>

    <!-- 管理员回复 -->
    <view class="section reply-section" v-if="feedback.reply_content">
      <view class="section-title">
        <text class="icon">💬</text>
        <text>管理员回复</text>
      </view>
      <view class="reply-content">{{ feedback.reply_content }}</view>
      <view class="reply-meta">
        <text v-if="feedback.replier_name">回复人：{{ feedback.replier_name }}</text>
        <text v-if="feedback.replied_at">{{ formatDateTime(feedback.replied_at) }}</text>
      </view>
    </view>

    <!-- 提交新反馈 -->
    <view class="action-section">
      <button class="btn-new-feedback" @click="goToSubmit">提交新反馈</button>
    </view>
  </view>

  <!-- 加载状态 -->
  <view class="loading-container" v-else>
    <text>加载中...</text>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, onMounted } from 'vue'
import { getFeedbackDetail } from '@/api/feedback'
import type { Feedback, FeedbackStatus } from '@/api/feedback'

const feedback = ref<Feedback | null>(null)

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
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const day = date.getDate().toString().padStart(2, '0')
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 预览图片
const previewImage = (index: number) => {
  if (feedback.value?.images) {
    uni.previewImage({
      urls: feedback.value.images,
      current: index
    })
  }
}

// 跳转到提交页面
const goToSubmit = () => {
  safeNavigate({ url: '/pages/feedback/submit' })
}

// 加载详情
onMounted(async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const id = currentPage.options?.id
  
  if (id) {
    try {
      feedback.value = await getFeedbackDetail(Number(id)) as any
    } catch (error) {
      console.error('加载反馈详情失败:', error)
      uni.showToast({ title: '加载失败', icon: 'none' })
    }
  }
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

.section {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-sizing: border-box;
  width: 100%;
}

.section-header {
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

.content-text {
  font-size: 15px;
  color: #334155;
  line-height: 1.8;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.image-list image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
}

.contact-info {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.contact-info .label {
  font-size: 14px;
  color: #64748b;
}

.contact-info .value {
  font-size: 14px;
  color: #334155;
}

.reply-section {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #166534;
  margin-bottom: 12px;
}

.section-title .icon {
  font-size: 18px;
}

.reply-content {
  font-size: 15px;
  color: #334155;
  line-height: 1.8;
  padding: 12px;
  background-color: #ffffff;
  border-radius: 8px;
}

.reply-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #64748b;
}

.action-section {
  margin-top: 24px;
}

.btn-new-feedback {
  width: 100%;
  height: 48px;
  background-color: #3b82f6;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
}

.loading-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}
</style>
