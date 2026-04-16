<template>
  <view class="container">
    <view v-if="loading" class="loading">
      <text>加载中...</text>
    </view>
    <view v-else-if="!article" class="error">
      <text>文章不存在或已被删除</text>
    </view>
    <view v-else class="content">
      <view class="header">
        <text class="title">{{ article.title }}</text>
        <view class="meta">
          <text class="author">{{ article.author || '健康小助手' }}</text>
          <text class="date">{{ formatDate(article.published_at) }}</text>
          <text class="views">阅读 {{ article.views }}</text>
        </view>
      </view>

      <view v-if="article.video_url" class="video-container">
        <video 
          :src="article.video_url" 
          controls 
          class="video-player"
          :poster="article.cover_image"
        ></video>
      </view>

      <view class="rich-content">
        <!-- Using rich-text for now, can be upgraded to mp-html or similar -->
        <rich-text :nodes="formatContent(article.content)"></rich-text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getArticleDetail, type Article } from '@/api/education'

const article = ref<Article | null>(null)
const loading = ref(true)

const formatDate = (iso: string) => {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}

const formatContent = (content: string | undefined) => {
  if (!content) return ''
  // Basic handling for images to fit screen
  return content.replace(/<img/g, '<img style="max-width:100%;height:auto;"')
}

onLoad(async (options: any) => {
  const id = options.id
  if (id) {
    try {
      article.value = await getArticleDetail(Number(id))
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }
})
</script>

<style>
.container {
  padding: 20px;
  background-color: #fff;
  min-height: 100vh;
}

.header {
  margin-bottom: 20px;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 16px;
}

.title {
  font-size: 22px;
  font-weight: bold;
  color: #1f2937;
  line-height: 1.4;
  margin-bottom: 12px;
}

.meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #9ca3af;
}

.video-container {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 200px;
}

.rich-content {
  font-size: 16px;
  line-height: 1.8;
  color: #374151;
}

.loading, .error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
  color: #9ca3af;
}
</style>
