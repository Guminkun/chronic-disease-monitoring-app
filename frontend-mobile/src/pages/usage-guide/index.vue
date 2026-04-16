<template>
  <view class="container">
    <!-- 使用说明列表 -->
    <scroll-view 
      scroll-y 
      class="guide-list"
      @scrolltolower="loadMore"
      :refresher-enabled="true"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
    >
      <view v-if="loading && guides.length === 0" class="loading-container">
        <text class="loading-text">加载中...</text>
      </view>
      
      <view v-else-if="guides.length === 0" class="empty-container">
        <text class="empty-text">暂无使用说明</text>
      </view>
      
      <view v-else>
        <view 
          v-for="guide in guides" 
          :key="guide.id" 
          class="guide-card"
          @click="goToDetail(guide.id)"
        >
          <view class="guide-cover">
            <image 
              v-if="guide.cover_image" 
              :src="guide.cover_image" 
              mode="aspectFill"
              class="cover-image"
            />
            <view v-else class="cover-placeholder">
              <text class="placeholder-icon">📖</text>
            </view>
          </view>
          <view class="guide-info">
            <text class="guide-title">{{ guide.title }}</text>
            <text class="guide-desc">{{ guide.description || '暂无描述' }}</text>
            <view class="guide-meta">
              <view class="meta-item">
                <text class="meta-icon">👁️</text>
                <text class="meta-text">{{ guide.views || 0 }}次浏览</text>
              </view>
              <view v-if="guide.images?.length" class="meta-item">
                <text class="meta-icon">🖼️</text>
                <text class="meta-text">{{ guide.images.length }}张图片</text>
              </view>
              <view v-if="guide.videos?.length" class="meta-item">
                <text class="meta-icon">🎬</text>
                <text class="meta-text">{{ guide.videos.length }}个视频</text>
              </view>
            </view>
          </view>
        </view>
        
        <view v-if="hasMore" class="load-more">
          <text class="load-more-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
        </view>
        <view v-else-if="guides.length > 0" class="no-more">
          <text class="no-more-text">没有更多了</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getPublishedUsageGuides, type UsageGuide } from '@/api/usageGuide'

const guides = ref<UsageGuide[]>([])
const loading = ref(false)
const isRefreshing = ref(false)
const hasMore = ref(true)
const page = ref(0)
const pageSize = 10

const fetchGuides = async () => {
  if (loading.value) return
  loading.value = true
  
  try {
    const res = await getPublishedUsageGuides({
      skip: page.value * pageSize,
      limit: pageSize
    }) as UsageGuide[]
    
    if (res.length < pageSize) {
      hasMore.value = false
    }
    
    guides.value = [...guides.value, ...res]
    page.value++
  } catch (e) {
    console.error('获取使用说明列表失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
    isRefreshing.value = false
  }
}

const loadMore = () => {
  if (!loading.value && hasMore.value) {
    fetchGuides()
  }
}

const onRefresh = () => {
  isRefreshing.value = true
  page.value = 0
  guides.value = []
  hasMore.value = true
  fetchGuides()
}

const goToDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/usage-guide/detail?id=${id}` })
}

onMounted(() => {
  fetchGuides()
})
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f8fafc;
}

.guide-list {
  flex: 1;
  padding: 16px;
}

.loading-container,
.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.loading-text,
.empty-text {
  color: #94a3b8;
  font-size: 14px;
}

.guide-card {
  display: flex;
  flex-direction: row;
  background-color: #ffffff;
  border-radius: 12px;
  margin-bottom: 12px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.guide-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background-color: #f1f5f9;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #e2e8f0;
}

.placeholder-icon {
  font-size: 32px;
}

.guide-info {
  flex: 1;
  margin-left: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.guide-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  lines: 1;
  text-overflow: ellipsis;
  overflow: hidden;
}

.guide-desc {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
  lines: 2;
  text-overflow: ellipsis;
  overflow: hidden;
}

.guide-meta {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.meta-item {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.meta-icon {
  font-size: 12px;
  margin-right: 2px;
}

.meta-text {
  font-size: 12px;
  color: #94a3b8;
}

.load-more,
.no-more {
  padding: 16px;
  text-align: center;
}

.load-more-text,
.no-more-text {
  color: #94a3b8;
  font-size: 13px;
}
</style>
