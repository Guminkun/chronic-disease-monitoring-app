<template>
  <view class="page-container">
    <!-- 顶部搜索栏 -->
    <view v-if="!selectedMed" class="search-header">
      <view class="search-bar-wrap">
        <view class="search-icon-box">
          <view class="search-circle"></view>
          <view class="search-handle"></view>
        </view>
        <input
          v-model="searchKeyword"
          class="search-input"
          placeholder="搜索药品名称、批准文号..."
          placeholder-class="search-placeholder"
          @confirm="handleSearch"
          @input="handleSearchInput"
        />
        <view v-if="searchKeyword" class="search-clear" @click="clearSearch">
          <text class="clear-icon">×</text>
        </view>
      </view>
    </view>

    <!-- 热门搜索 -->
    <view v-if="!searchKeyword && !selectedMed" class="hot-section">
      <view class="section-head">
        <text class="section-title">热门搜索</text>
      </view>
      <view class="hot-tags">
        <view 
          v-for="tag in hotTags" 
          :key="tag" 
          class="hot-tag"
          @click="searchByTag(tag)"
        >
          <text class="hot-tag-text">{{ tag }}</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果列表 -->
    <scroll-view 
      v-if="searchKeyword && !selectedMed" 
      scroll-y 
      class="result-scroll"
      :show-scrollbar="false"
    >
      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
        <text class="loading-text">搜索中...</text>
      </view>

      <view v-else-if="searchResults.length === 0" class="empty-state">
        <text class="empty-icon">💊</text>
        <text class="empty-title">未找到相关药品</text>
        <text class="empty-desc">请尝试其他关键词</text>
      </view>

      <view v-else class="result-list">
        <view 
          v-for="med in searchResults" 
          :key="med.id" 
          class="med-card"
          @click="selectMedication(med)"
        >
          <view class="med-header">
            <view class="med-name-wrap">
              <text class="med-name">{{ med.name }}</text>
              <text v-if="med.trade_name" class="med-trade-name">（{{ med.trade_name }}）</text>
            </view>
            <view v-if="med.category" class="med-category">
              <text class="category-text">{{ med.category }}</text>
            </view>
          </view>
          <view class="med-info-row">
            <text class="med-info-label">规格</text>
            <text class="med-info-value">{{ med.specification || '暂无' }}</text>
          </view>
          <view class="med-info-row">
            <text class="med-info-label">厂家</text>
            <text class="med-info-value">{{ med.manufacturer || '暂无' }}</text>
          </view>
          <view v-if="med.indications" class="med-indications">
            <text class="indications-text">{{ med.indications }}</text>
          </view>
          <view class="med-arrow">
            <text class="arrow-icon">›</text>
          </view>
        </view>
      </view>

      <view v-if="searchResults.length > 0 && hasMore" class="load-more" @click="loadMore">
        <text class="load-more-text">加载更多</text>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <!-- 药品详情 -->
    <scroll-view 
      v-if="selectedMed" 
      scroll-y 
      class="detail-scroll"
      :show-scrollbar="false"
    >
      <view class="detail-content">
        <!-- 基本信息卡片 -->
        <view class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-teal">
              <text class="title-icon">💊</text>
            </view>
            <text class="card-title">基本信息</text>
          </view>
          
          <view class="info-grid">
            <view class="info-item full">
              <text class="info-label">通用名称</text>
              <text class="info-value primary">{{ selectedMed.name }}</text>
            </view>
            <view v-if="selectedMed.trade_name" class="info-item">
              <text class="info-label">商品名称</text>
              <text class="info-value">{{ selectedMed.trade_name }}</text>
            </view>
            <view v-if="selectedMed.category" class="info-item">
              <text class="info-label">药品分类</text>
              <text class="info-value">{{ selectedMed.category }}</text>
            </view>
            <view v-if="selectedMed.specification" class="info-item">
              <text class="info-label">规格</text>
              <text class="info-value">{{ selectedMed.specification }}</text>
            </view>
            <view v-if="selectedMed.manufacturer" class="info-item full">
              <text class="info-label">生产企业</text>
              <text class="info-value">{{ selectedMed.manufacturer }}</text>
            </view>
            <view v-if="selectedMed.approval_number" class="info-item full">
              <text class="info-label">批准文号</text>
              <text class="info-value small">{{ selectedMed.approval_number }}</text>
            </view>
          </view>
        </view>

        <!-- 适应症卡片 -->
        <view v-if="selectedMed.indications" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-green">
              <text class="title-icon">🎯</text>
            </view>
            <text class="card-title">适应症</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.indications }}</text>
          </view>
        </view>

        <!-- 用法用量卡片 -->
        <view v-if="selectedMed.usage_dosage" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-blue">
              <text class="title-icon">📋</text>
            </view>
            <text class="card-title">用法用量</text>
          </view>
          <view class="info-text-content highlight">
            <text class="info-text">{{ selectedMed.usage_dosage }}</text>
          </view>
        </view>

        <!-- 不良反应卡片 -->
        <view v-if="selectedMed.adverse_reactions" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-orange">
              <text class="title-icon">⚠️</text>
            </view>
            <text class="card-title">不良反应</text>
          </view>
          <view class="info-text-content warning">
            <text class="info-text">{{ selectedMed.adverse_reactions }}</text>
          </view>
        </view>

        <!-- 禁忌卡片 -->
        <view v-if="selectedMed.contraindications" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-red">
              <text class="title-icon">🚫</text>
            </view>
            <text class="card-title">禁忌</text>
          </view>
          <view class="info-text-content danger">
            <text class="info-text">{{ selectedMed.contraindications }}</text>
          </view>
        </view>

        <!-- 注意事项卡片 -->
        <view v-if="selectedMed.precautions" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-purple">
              <text class="title-icon">💡</text>
            </view>
            <text class="card-title">注意事项</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.precautions }}</text>
          </view>
        </view>

        <!-- 特殊人群用药 -->
        <view v-if="hasSpecialPopulation" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-pink">
              <text class="title-icon">👥</text>
            </view>
            <text class="card-title">特殊人群用药</text>
          </view>
          <view class="special-population">
            <view v-if="selectedMed.pregnancy_lactation" class="special-item">
              <text class="special-label">孕妇及哺乳期妇女</text>
              <text class="special-value">{{ selectedMed.pregnancy_lactation }}</text>
            </view>
            <view v-if="selectedMed.pediatric_use" class="special-item">
              <text class="special-label">儿童用药</text>
              <text class="special-value">{{ selectedMed.pediatric_use }}</text>
            </view>
            <view v-if="selectedMed.geriatric_use" class="special-item">
              <text class="special-label">老人用药</text>
              <text class="special-value">{{ selectedMed.geriatric_use }}</text>
            </view>
          </view>
        </view>

        <!-- 药物相互作用 -->
        <view v-if="selectedMed.drug_interactions" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-cyan">
              <text class="title-icon">🔄</text>
            </view>
            <text class="card-title">药物相互作用</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.drug_interactions }}</text>
          </view>
        </view>

        <!-- 药理毒理 -->
        <view v-if="selectedMed.pharmacology_toxicology" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-indigo">
              <text class="title-icon">🔬</text>
            </view>
            <text class="card-title">药理毒理</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.pharmacology_toxicology }}</text>
          </view>
        </view>

        <!-- 贮藏与有效期 -->
        <view v-if="selectedMed.storage || selectedMed.expiry_period" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-gray">
              <text class="title-icon">📦</text>
            </view>
            <text class="card-title">贮藏与有效期</text>
          </view>
          <view class="storage-info">
            <view v-if="selectedMed.storage" class="storage-item">
              <text class="storage-label">贮藏条件</text>
              <text class="storage-value">{{ selectedMed.storage }}</text>
            </view>
            <view v-if="selectedMed.expiry_period" class="storage-item">
              <text class="storage-label">有效期</text>
              <text class="storage-value">{{ selectedMed.expiry_period }}</text>
            </view>
          </view>
        </view>

        <!-- 性状 -->
        <view v-if="selectedMed.properties" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-teal">
              <text class="title-icon">📝</text>
            </view>
            <text class="card-title">性状</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.properties }}</text>
          </view>
        </view>

        <!-- 主要成分 -->
        <view v-if="selectedMed.main_ingredients" class="info-card">
          <view class="card-title-row">
            <view class="title-icon-wrap bg-amber">
              <text class="title-icon">🧪</text>
            </view>
            <text class="card-title">主要成分</text>
          </view>
          <view class="info-text-content">
            <text class="info-text">{{ selectedMed.main_ingredients }}</text>
          </view>
        </view>
      </view>

      <view class="bottom-space"></view>

      <!-- 浮动按钮 -->
      <view class="float-btn-wrap">
        <view class="add-to-cabinet-btn" @click="addToMedicationCabinet">
          <text class="btn-icon">💊</text>
          <text class="btn-text">添加到药箱</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed } from 'vue'
import { searchMedicationDict, type MedicationDictItem } from '@/api/medication_dict'

const searchKeyword = ref('')
const searchResults = ref<MedicationDictItem[]>([])
const selectedMed = ref<MedicationDictItem | null>(null)
const loading = ref(false)
const hasMore = ref(false)
const currentSkip = ref(0)
const pageSize = 20

const hotTags = ['阿莫西林', '布洛芬', '头孢', '阿司匹林', '感冒灵', '维生素C']

const hasSpecialPopulation = computed(() => {
  if (!selectedMed.value) return false
  return !!(
    selectedMed.value.pregnancy_lactation ||
    selectedMed.value.pediatric_use ||
    selectedMed.value.geriatric_use
  )
})

const handleSearchInput = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    hasMore.value = false
  }
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) return
  
  loading.value = true
  currentSkip.value = 0
  
  try {
    const res = await searchMedicationDict({
      q: searchKeyword.value.trim(),
      skip: 0,
      limit: pageSize
    })
    searchResults.value = res.items || []
    hasMore.value = (res.items || []).length >= pageSize
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (!hasMore.value || loading.value) return
  
  loading.value = true
  currentSkip.value += pageSize
  
  try {
    const res = await searchMedicationDict({
      q: searchKeyword.value.trim(),
      skip: currentSkip.value,
      limit: pageSize
    })
    searchResults.value = [...searchResults.value, ...(res.items || [])]
    hasMore.value = (res.items || []).length >= pageSize
  } catch (error) {
    console.error('加载更多失败:', error)
  } finally {
    loading.value = false
  }
}

const searchByTag = (tag: string) => {
  searchKeyword.value = tag
  handleSearch()
}

const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
  hasMore.value = false
}

const selectMedication = (med: MedicationDictItem) => {
  selectedMed.value = med
}

const closeDetail = () => {
  selectedMed.value = null
}

const addToMedicationCabinet = () => {
  if (!selectedMed.value) return
  
  const med = selectedMed.value
  const params = new URLSearchParams()
  
  // 只传递基本信息，避免 URL 过长
  if (med.generic_name) params.append('generic_name', med.generic_name)
  if (med.trade_name) params.append('trade_name', med.trade_name)
  if (med.manufacturer) params.append('manufacturer', med.manufacturer)
  if (med.properties) params.append('properties', med.properties)
  if (med.specification) params.append('specification', med.specification)
  
  // 用法用量和注意事项可能很长，只取前200字符
  if (med.usage_dosage) {
    const text = med.usage_dosage.length > 200 ? med.usage_dosage.substring(0, 200) + '...' : med.usage_dosage
    params.append('usage_dosage', text)
  }
  if (med.adverse_reactions) {
    const text = med.adverse_reactions.length > 150 ? med.adverse_reactions.substring(0, 150) + '...' : med.adverse_reactions
    params.append('adverse_reactions', text)
  }
  if (med.precautions) {
    const text = med.precautions.length > 150 ? med.precautions.substring(0, 150) + '...' : med.precautions
    params.append('precautions', text)
  }
  
  uni.navigateTo({
    url: `/pages/medication/add?${params.toString()}`
  })
}
</script>

<style>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 搜索栏 */
.search-header {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  padding: 20rpx 28rpx;
  border-bottom: 1rpx solid rgba(0, 0, 0, 0.06);
}

.search-bar-wrap {
  display: flex;
  align-items: center;
  background: #ffffff;
  border-radius: 48rpx;
  padding: 20rpx 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08), 0 8rpx 24rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid rgba(148, 163, 184, 0.2);
}

.search-icon-box {
  width: 32rpx;
  height: 32rpx;
  position: relative;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.search-circle {
  width: 20rpx;
  height: 20rpx;
  border: 3rpx solid #94a3b8;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
}

.search-handle {
  width: 3rpx;
  height: 12rpx;
  background: #94a3b8;
  border-radius: 2rpx;
  position: absolute;
  bottom: 0;
  right: 4rpx;
  transform: rotate(-45deg);
  transform-origin: bottom center;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #1e293b;
  background: transparent;
}

.search-placeholder {
  color: #94a3b8;
}

.search-clear {
  width: 40rpx;
  height: 40rpx;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
}

.clear-icon {
  color: #64748b;
  font-size: 28rpx;
  font-weight: 300;
}

/* 热门搜索 */
.hot-section {
  padding: 32rpx 28rpx;
}

.section-head {
  margin-bottom: 18rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #374151;
}

.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.hot-tag {
  background: #ffffff;
  border: 1rpx solid rgba(148, 163, 184, 0.15);
  border-radius: 28rpx;
  padding: 12rpx 24rpx;
  box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.03);
}

.hot-tag-text {
  font-size: 26rpx;
  color: #64748b;
}

/* 搜索结果 */
.result-scroll {
  height: calc(100vh - 180rpx);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #e2e8f0;
  border-top-color: #14b8a6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #94a3b8;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #94a3b8;
}

.result-list {
  padding: 20rpx 28rpx;
}

.med-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05), 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid rgba(148, 163, 184, 0.12);
  position: relative;
}

.med-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14rpx;
}

.med-name-wrap {
  flex: 1;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
}

.med-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
  margin-right: 10rpx;
}

.med-trade-name {
  font-size: 24rpx;
  color: #64748b;
}

.med-category {
  background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
  border-radius: 10rpx;
  padding: 4rpx 12rpx;
  flex-shrink: 0;
}

.category-text {
  font-size: 22rpx;
  color: #ffffff;
  font-weight: 500;
}

.med-info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8rpx;
}

.med-info-label {
  font-size: 24rpx;
  color: #94a3b8;
  width: 70rpx;
  flex-shrink: 0;
}

.med-info-value {
  font-size: 24rpx;
  color: #475569;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.med-indications {
  background: #f8fafc;
  border-radius: 10rpx;
  padding: 12rpx 16rpx;
  margin-top: 8rpx;
}

.indications-text {
  font-size: 24rpx;
  color: #64748b;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.med-arrow {
  position: absolute;
  right: 28rpx;
  top: 50%;
  transform: translateY(-50%);
}

.arrow-icon {
  font-size: 40rpx;
  color: #cbd5e1;
}

.load-more {
  text-align: center;
  padding: 32rpx 0;
}

.load-more-text {
  font-size: 26rpx;
  color: #14b8a6;
}

.bottom-space {
  height: 160rpx;
}

/* 药品详情 */
.detail-scroll {
  height: 100vh;
  background: #f5f7fa;
}

.detail-content {
  padding: 20rpx 28rpx;
}

.info-card {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05), 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid rgba(148, 163, 184, 0.12);
}

.card-title-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.title-icon-wrap {
  width: 40rpx;
  height: 40rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
}

.bg-teal { background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%); }
.bg-green { background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); }
.bg-blue { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
.bg-orange { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
.bg-red { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
.bg-purple { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
.bg-pink { background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); }
.bg-cyan { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); }
.bg-indigo { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); }
.bg-gray { background: linear-gradient(135deg, #64748b 0%, #475569 100%); }
.bg-amber { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }

.title-icon {
  font-size: 22rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
}

.info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx 24rpx;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  min-width: calc(50% - 12rpx);
}

.info-item.full {
  min-width: 100%;
}

.info-label {
  font-size: 24rpx;
  color: #94a3b8;
}

.info-value {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.5;
}

.info-value.primary {
  font-size: 30rpx;
  font-weight: 600;
  color: #1e293b;
}

.info-value.small {
  font-size: 24rpx;
  color: #64748b;
}

.info-text-content {
  background: #f8fafc;
  border-radius: 10rpx;
  padding: 16rpx 20rpx;
  border-left: 3rpx solid #14b8a6;
}

.info-text-content.highlight {
  background: #eff6ff;
  border-left-color: #3b82f6;
}

.info-text-content.warning {
  background: #fff7ed;
  border-left-color: #f97316;
}

.info-text-content.danger {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.info-text {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.8;
}

.special-population {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.special-item {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  padding: 14rpx 16rpx;
  background: #fdf2f8;
  border-radius: 10rpx;
}

.special-label {
  font-size: 24rpx;
  color: #db2777;
  font-weight: 600;
}

.special-value {
  font-size: 26rpx;
  color: #334155;
  line-height: 1.6;
}

.storage-info {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.storage-item {
  display: flex;
  align-items: center;
  padding: 12rpx 16rpx;
  background: #f8fafc;
  border-radius: 10rpx;
}

.storage-label {
  font-size: 24rpx;
  color: #94a3b8;
  width: 120rpx;
  flex-shrink: 0;
}

.storage-value {
  font-size: 26rpx;
  color: #334155;
}

/* 浮动按钮 */
.float-btn-wrap {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 28rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.96) 20%);
  z-index: 100;
}

.add-to-cabinet-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #14b8a6 0%, #0d9488 100%);
  border-radius: 44rpx;
  padding: 24rpx 0;
  box-shadow: 0 6rpx 20rpx rgba(20, 184, 166, 0.25), 0 3rpx 10rpx rgba(0, 0, 0, 0.08);
}

.btn-icon {
  font-size: 30rpx;
  margin-right: 10rpx;
}

.btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.5rpx;
}
</style>
