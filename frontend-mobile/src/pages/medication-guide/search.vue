<template>
  <view class="page">
    <!-- 搜索头部 -->
    <view class="search-header">
      <view class="search-input-wrap">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input" 
          v-model="keyword" 
          placeholder="搜索药品名称或疾病名称"
          focus
          @confirm="handleSearch"
        />
        <view v-if="keyword" class="clear-btn" @click="clearSearch">
          <text class="clear-icon">×</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <scroll-view scroll-y class="result-scroll" v-if="hasSearched">
      <view v-if="loading" class="loading-state">
        <text class="loading-text">搜索中...</text>
      </view>

      <view v-else-if="results.length === 0" class="empty-state">
        <text class="empty-icon">🔍</text>
        <text class="empty-title">未找到相关结果</text>
        <text class="empty-desc">请尝试其他关键词</text>
      </view>

      <view v-else class="result-list">
        <view 
          v-for="item in results" 
          :key="`${item.type}-${item.id}`" 
          class="result-item"
          @click="goToDetail(item)"
        >
          <view class="item-icon" :class="item.type">
            <text>{{ item.type === 'medication' ? '💊' : '🏥' }}</text>
          </view>
          <view class="item-main">
            <text class="item-name">{{ item.name }}</text>
            <text v-if="item.sub_name" class="item-subname">（{{ item.sub_name }}）</text>
            <view class="item-info">
              <text v-if="item.category" class="item-category">{{ item.category }}</text>
              <text v-if="item.manufacturer" class="item-manufacturer">{{ item.manufacturer }}</text>
            </view>
          </view>
          <text class="item-arrow">›</text>
        </view>
      </view>
    </scroll-view>

    <!-- 热门搜索 -->
    <view v-else class="hot-section">
      <view class="section-title">
        <text>热门搜索</text>
      </view>
      <view class="hot-tags">
        <view 
          v-for="tag in hotTags" 
          :key="tag" 
          class="hot-tag"
          @click="searchByTag(tag)"
        >
          <text>{{ tag }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref } from 'vue'
import { searchAll, type SearchResultItem } from '@/api/medication_dict'

const keyword = ref('')
const results = ref<SearchResultItem[]>([])
const loading = ref(false)
const hasSearched = ref(false)

const hotTags = ['阿莫西林', '布洛芬', '高血压', '糖尿病', '头孢克肟', '感冒']

const goBack = () => uni.navigateBack()

const clearSearch = () => {
  keyword.value = ''
  results.value = []
  hasSearched.value = false
}

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  
  loading.value = true
  hasSearched.value = true
  
  try {
    const res = await searchAll(keyword.value.trim())
    results.value = res.items || []
  } catch (e) {
    console.error('Search failed:', e)
    results.value = []
  } finally {
    loading.value = false
  }
}

const searchByTag = (tag: string) => {
  keyword.value = tag
  handleSearch()
}

const goToDetail = (item: SearchResultItem) => {
  if (item.type === 'medication') {
    // Go to medication detail page with id
    uni.navigateTo({
      url: `/pages/medication-guide/detail?id=${item.id}`
    })
  } else {
    // Go to disease detail
    uni.showToast({ title: '疾病详情开发中', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: #f8fafc;
}

.search-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff;
  gap: 12px;
}

.search-input-wrap {
  flex: 1;
  height: 40px;
  background-color: #f1f5f9;
  border-radius: 20px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
}

.search-icon {
  font-size: 16px;
}

.search-input {
  flex: 1;
  font-size: 14px;
  color: #0f172a;
}

.clear-btn {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-icon {
  font-size: 14px;
  color: #fff;
}

.result-scroll {
  height: calc(100vh - 64px);
  padding: 16px;
}

.loading-state {
  padding: 40px 0;
  text-align: center;
}

.loading-text {
  font-size: 14px;
  color: #64748b;
}

.empty-state {
  padding: 80px 0;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  display: block;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #64748b;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  background-color: #fff;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.item-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background-color: #e0f2fe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-icon.disease {
  background-color: #fce7f3;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.item-subname {
  font-size: 14px;
  color: #64748b;
  margin-left: 4px;
}

.item-info {
  margin-top: 4px;
  display: flex;
  gap: 8px;
}

.item-category {
  font-size: 12px;
  color: #0891b2;
  background-color: #e0f2fe;
  padding: 2px 8px;
  border-radius: 4px;
}

.item-manufacturer {
  font-size: 12px;
  color: #64748b;
}

.item-arrow {
  font-size: 20px;
  color: #cbd5e1;
}

.hot-section {
  padding: 24px 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 16px;
}

.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hot-tag {
  padding: 10px 20px;
  background-color: #fff;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
}

.hot-tag text {
  font-size: 14px;
  color: #475569;
}
</style>
