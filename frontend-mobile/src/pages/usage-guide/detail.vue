<template>
  <view class="container">
    <scroll-view scroll-y class="content-scroll">
      <!-- 加载中 -->
      <view v-if="loading" class="loading-container">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="guide">
        <!-- 封面图 -->
        <view v-if="guide.cover_image" class="cover-section">
          <image :src="guide.cover_image" mode="widthFix" class="cover-image" @click="previewImage(guide.cover_image)" />
        </view>

        <!-- 基本信息 -->
        <view class="info-section">
          <view class="title-row">
            <text class="guide-title">{{ guide.title }}</text>
          </view>
          
          <view class="meta-row">
            <text class="meta-text">👁️ {{ guide.views || 0 }}次浏览</text>
            <text class="meta-text">{{ formatDate(guide.created_at) }}</text>
          </view>

          <view v-if="guide.description" class="description-section">
            <text class="description-text">{{ guide.description }}</text>
          </view>
        </view>

        <!-- 详细内容 -->
        <view v-if="guide.content" class="content-section">
          <text class="section-title">详细内容</text>
          <rich-text :nodes="guide.content" class="content-text"></rich-text>
        </view>

        <!-- 图片列表 -->
        <view v-if="guide.images && guide.images.length > 0" class="media-section">
          <text class="section-title">相关图片</text>
          <view class="image-grid">
            <view 
              v-for="(img, index) in guide.images" 
              :key="index" 
              class="image-item"
              @click="previewImages(guide.images, index)"
            >
              <image :src="img" mode="aspectFill" class="grid-image" />
            </view>
          </view>
        </view>

        <!-- 视频列表 -->
        <view v-if="guide.videos && guide.videos.length > 0" class="media-section">
          <text class="section-title">相关视频</text>
          <view class="video-list">
            <view v-for="(video, index) in guide.videos" :key="index" class="video-item">
              <video 
                :src="video" 
                class="video-player"
                :controls="true"
                :show-center-play-btn="true"
                :enable-progress-gesture="true"
              />
            </view>
          </view>
        </view>
      </view>

      <!-- 加载失败 -->
      <view v-else class="error-container">
        <text class="error-text">加载失败，请重试</text>
        <button class="retry-btn" @click="fetchDetail">重新加载</button>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUsageGuide, type UsageGuide } from '@/api/usageGuide'

const guide = ref<UsageGuide | null>(null)
const loading = ref(true)

const formatDate = (iso: string) => {
  if (!iso) return ''
  const date = new Date(iso)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const fetchDetail = async () => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const id = (currentPage as any).options?.id
  
  if (!id) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    guide.value = await getUsageGuide(Number(id)) as UsageGuide
  } catch (e) {
    console.error('获取使用说明详情失败:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const previewImage = (url: string) => {
  uni.previewImage({
    urls: [url],
    current: url
  })
}

const previewImages = (urls: string[], index: number) => {
  uni.previewImage({
    urls: urls,
    current: index
  })
}

onMounted(() => {
  fetchDetail()
})
</script>

<style>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #ffffff;
}

.content-scroll {
  flex: 1;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 100px 0;
}

.loading-text,
.error-text {
  font-size: 14px;
  color: #94a3b8;
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  font-size: 14px;
  background-color: #3b82f6;
  color: #ffffff;
  border-radius: 20px;
  border: none;
}

.cover-section {
  width: 100%;
}

.cover-image {
  width: 100%;
}

.info-section {
  padding: 16px;
  border-bottom: 8px solid #f1f5f9;
}

.title-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
}

.guide-title {
  flex: 1;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.meta-row {
  display: flex;
  flex-direction: row;
  gap: 16px;
  margin-top: 12px;
}

.meta-text {
  font-size: 13px;
  color: #94a3b8;
}

.description-section {
  margin-top: 16px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.description-text {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

.content-section,
.media-section {
  padding: 16px;
  border-bottom: 8px solid #f1f5f9;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.content-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.8;
}

.image-grid {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
}

.image-item {
  width: calc(33.33% - 6px);
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
}

.grid-image {
  width: 100%;
  height: 100%;
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.video-item {
  border-radius: 8px;
  overflow: hidden;
  background-color: #000000;
}

.video-player {
  width: 100%;
  height: 200px;
}
</style>
