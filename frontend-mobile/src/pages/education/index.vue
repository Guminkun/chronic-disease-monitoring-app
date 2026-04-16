<template>
  <view class="container">
    <!-- Search Bar -->
    <view class="search-box">
      <view class="search-input-wrapper">
        <text class="iconfont icon-search">🔍</text>
        <input 
          class="search-input" 
          placeholder="搜索健康知识..." 
          v-model="searchQuery"
          @confirm="onSearch"
        />
      </view>
    </view>

    <!-- Category Tabs -->
    <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
      <view class="category-list">
        <view 
          class="category-item" 
          :class="{ active: currentCategoryId === 0 }"
          @click="selectCategory(0)"
        >
          <view class="cat-icon bg-blue">
            <text>📖</text>
          </view>
          <text class="cat-name">全部</text>
        </view>
        <view 
          v-for="cat in categories" 
          :key="cat.id"
          class="category-item"
          :class="{ active: currentCategoryId === cat.id }"
          @click="selectCategory(cat.id)"
        >
          <view class="cat-icon" :class="getCategoryColor(cat.id)">
            <image v-if="cat.icon" :src="cat.icon" class="cat-img" />
            <text v-else>{{ getCategoryEmoji(cat.name) }}</text>
          </view>
          <text class="cat-name">{{ cat.name }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Content Area -->
    <view class="content-area">
      <!-- Hot Recommended (Only show on 'All' tab) -->
      <view class="section-block" v-if="currentCategoryId === 0 && recommendedArticles.length > 0">
        <view class="section-header">
          <text class="section-title">热门推荐</text>
        </view>
        <view class="hot-list">
          <view 
            v-for="(item, index) in recommendedArticles" 
            :key="item.id"
            class="hot-item"
            @click="goToDetail(item.id)"
          >
            <view class="hot-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</view>
            <text class="hot-title">{{ item.title }}</text>
            <text class="hot-views">{{ formatViews(item.views) }}</text>
          </view>
        </view>
      </view>

      <!-- Article List -->
      <view class="section-block">
        <view class="section-header">
          <text class="section-title">{{ currentCategoryName }}</text>
          <text class="article-count">共 {{ articles.length }} 篇</text>
        </view>
        
        <view class="article-list">
          <view 
            v-for="article in articles" 
            :key="article.id"
            class="article-card"
            @click="goToDetail(article.id)"
          >
            <image class="article-cover" :src="article.cover_image || '/static/logo.png'" mode="aspectFill" />
            <view class="article-info">
              <text class="article-title">{{ article.title }}</text>
              <view class="article-meta">
                <text class="author">{{ article.author || '健康小助手' }}</text>
                <view class="meta-right">
                  <text class="views">👁 {{ article.views }}</text>
                  <text class="time">🕒 {{ article.duration || '3分钟' }}</text>
                </view>
              </view>
            </view>
          </view>
          
          <view v-if="loading" class="loading-more">
            <text>加载中...</text>
          </view>
          <view v-else-if="articles.length === 0" class="empty-state">
            <text>暂无相关文章</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed, onMounted } from 'vue'
import { onLoad, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { getArticleCategories, getArticles, type ArticleCategory, type Article } from '@/api/education'

const searchQuery = ref('')
const currentCategoryId = ref(0)
const categories = ref<ArticleCategory[]>([])
const articles = ref<Article[]>([])
const recommendedArticles = ref<Article[]>([])
const loading = ref(false)
const page = ref(0)
const hasMore = ref(true)

const currentCategoryName = computed(() => {
  if (currentCategoryId.value === 0) return '推荐阅读'
  const cat = categories.value.find(c => c.id === currentCategoryId.value)
  return cat ? cat.name : '文章列表'
})

const getCategoryEmoji = (name: string) => {
  if (name.includes('糖尿病')) return '🍬'
  if (name.includes('高血压')) return '❤️'
  if (name.includes('饮食')) return '🍎'
  if (name.includes('运动')) return '🏃'
  if (name.includes('心理')) return '🧠'
  if (name.includes('用药')) return '💊'
  return '📝'
}

const getCategoryColor = (id: number) => {
  const colors = ['bg-red', 'bg-orange', 'bg-green', 'bg-blue', 'bg-purple', 'bg-pink']
  return colors[id % colors.length]
}

const formatViews = (views: number) => {
  if (views > 10000) return (views / 10000).toFixed(1) + '万'
  return views
}

const loadCategories = async () => {
  try {
    const res = await getArticleCategories()
    if (Array.isArray(res)) {
      categories.value = res
    }
  } catch (e) {
    console.error(e)
  }
}

const loadArticles = async (refresh = false) => {
  if (loading.value || (!hasMore.value && !refresh)) return
  
  loading.value = true
  if (refresh) {
    page.value = 0
    hasMore.value = true
    articles.value = []
  }

  try {
    const res = await getArticles({
      category_id: currentCategoryId.value === 0 ? undefined : currentCategoryId.value,
      q: searchQuery.value,
      skip: page.value * 10,
      limit: 10
    })
    
    const list = Array.isArray(res) ? res : []
    if (list.length < 10) {
      hasMore.value = false
    }
    
    if (refresh) {
      articles.value = list
    } else {
      articles.value = [...articles.value, ...list]
    }
    page.value++
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
    uni.stopPullDownRefresh()
  }
}

const loadRecommended = async () => {
  try {
    const res = await getArticles({
      is_recommended: true,
      limit: 3
    })
    if (Array.isArray(res)) {
      recommendedArticles.value = res
    }
  } catch (e) {
    console.error(e)
  }
}

const selectCategory = (id: number) => {
  currentCategoryId.value = id
  loadArticles(true)
}

const onSearch = () => {
  loadArticles(true)
}

const goToDetail = (id: number) => {
  uni.navigateTo({
    url: `/pages/education/detail?id=${id}`
  })
}

onLoad(() => {
  loadCategories()
  loadRecommended()
  loadArticles(true)
})

onPullDownRefresh(() => {
  loadArticles(true)
  loadRecommended()
})

onReachBottom(() => {
  loadArticles()
})
</script>

<style>
.container {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  padding-bottom: 20px;
}

.search-box {
  background-color: var(--color-bg-elevated);
  padding: 10px 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.search-input-wrapper {
  background-color: #f3f4f6;
  border-radius: 20px;
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 12px;
}

.icon-search {
  margin-right: 8px;
  color: #9ca3af;
}

.search-input {
  flex: 1;
  font-size: 14px;
}

.category-scroll {
  background-color: #fff;
  white-space: nowrap;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.category-list {
  display: flex;
  padding: 0 16px;
  gap: 20px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  opacity: 0.7;
  transition: all 0.3s;
}

.category-item.active {
  opacity: 1;
  transform: scale(1.05);
}

.category-item.active .cat-name {
  color: #3b82f6;
  font-weight: 600;
}

.cat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background-color: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.cat-name {
  font-size: 12px;
  color: #6b7280;
}

.bg-blue { background-color: #e0f2fe; color: #0284c7; }
.bg-red { background-color: #fee2e2; color: #dc2626; }
.bg-orange { background-color: #ffedd5; color: #ea580c; }
.bg-green { background-color: #dcfce7; color: #16a34a; }
.bg-purple { background-color: #f3e8ff; color: #9333ea; }
.bg-pink { background-color: #fce7f3; color: #db2777; }

.content-area {
  padding: 16px;
}

.section-block {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

.article-count {
  font-size: 12px;
  color: #9ca3af;
}

.hot-list {
  background-color: #3b82f6;
  border-radius: 16px;
  padding: 16px;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.hot-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.hot-item:last-child {
  border-bottom: none;
}

.hot-rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 12px;
  font-weight: bold;
}

.rank-1 { background-color: #fbbf24; color: #92400e; }
.rank-2 { background-color: #9ca3af; color: #1f2937; }
.rank-3 { background-color: #b45309; color: #fff; }

.hot-title {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-views {
  font-size: 12px;
  opacity: 0.8;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.article-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.article-cover {
  width: 100px;
  height: 75px;
  border-radius: 8px;
  background-color: #f3f4f6;
}

.article-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.article-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #9ca3af;
}

.meta-right {
  display: flex;
  gap: 12px;
}

.loading-more, .empty-state {
  text-align: center;
  padding: 20px;
  color: #9ca3af;
  font-size: 13px;
}
</style>
