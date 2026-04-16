<template>
  <view class="page-container">
    <!-- 顶部搜索栏 -->
    <view class="search-header">
      <view class="search-bar" @click="goToSearch">
        <view class="search-icon-box">
          <view class="search-circle"></view>
          <view class="search-handle"></view>
        </view>
        <text class="search-placeholder">搜索药品名称、批准文号...</text>
      </view>
    </view>

    <!-- 分类双栏布局 -->
    <view class="split-layout">
      <!-- 左侧侧边栏 -->
      <scroll-view scroll-y class="sidebar" :show-scrollbar="false">
        <view 
          v-for="(cat, index) in categories" 
          :key="cat.name" 
          class="sidebar-item"
          :class="{ active: currentIndex === index }"
          @click="selectCategory(index)"
        >
          <text class="cat-name">{{ cat.name }}</text>
        </view>
        <view class="safe-bottom"></view>
      </scroll-view>

      <!-- 右侧内容区 -->
      <scroll-view scroll-y class="content-list" :show-scrollbar="false">
        <view 
          v-for="sub in categories[currentIndex]?.subcategories || []" 
          :key="sub" 
          class="list-row"
          @click="goToList(sub)"
        >
          <text class="row-name">{{ sub }}</text>
          <text class="row-arrow">›</text>
        </view>
        <view v-if="categories.length > 0 && (!categories[currentIndex]?.subcategories || categories[currentIndex].subcategories.length === 0)" class="empty-tip">
          <text>暂无分类</text>
        </view>
        <view class="safe-bottom"></view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, onMounted } from 'vue'
import { getCategoryTree, type CategoryTreeItem } from '@/api/medication_dict'

const categories = ref<CategoryTreeItem[]>([])
const currentIndex = ref(0)

const goToSearch = () => {
  uni.navigateTo({ url: '/pages/medication-guide/index' })
}

const selectCategory = (index: number) => {
  currentIndex.value = index
}

const goToList = (subcategory: string) => {
  uni.navigateTo({
    url: `/pages/medication-guide/list?category=${encodeURIComponent(subcategory)}`
  })
}

const loadCategories = async () => {
  try {
    const res = await getCategoryTree()
    categories.value = res || []
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

/* 搜索栏 */
.search-header {
  background: #ffffff;
  padding: 24rpx 28rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 48rpx;
  padding: 22rpx 32rpx;
  border: 1rpx solid #e2e8f0;
}

.search-icon-box {
  width: 32rpx;
  height: 32rpx;
  position: relative;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.search-circle {
  width: 18rpx;
  height: 18rpx;
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

.search-placeholder {
  flex: 1;
  font-size: 28rpx;
  color: #94a3b8;
}

.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 200rpx;
  background-color: #F7F8FA;
  height: 100%;
}

.sidebar-item {
  padding: 44rpx 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  
  .cat-name {
    font-size: 28rpx;
    color: #64748b;
    text-align: center;
    line-height: 1.4;
    transition: all 0.2s;
  }
  
  &.active {
    background-color: #ffffff;
    .cat-name {
      color: #1a1a1a;
      font-weight: bold;
      transform: scale(1.05);
    }
  }
}

/* 内容列表 */
.content-list {
  flex: 1;
  background-color: #ffffff;
  height: 100%;
}

.list-row {
  padding: 40rpx 44rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1rpx solid #f8fafc;
  
  &:active {
    background-color: #f1f5f9;
  }
  
  .row-name {
    font-size: 32rpx;
    color: #1e293b;
    font-weight: 400;
  }
  
  .row-arrow {
    font-size: 36rpx;
    color: #e2e8f0;
    font-weight: 300;
  }
}

.empty-tip {
  padding: 80rpx 0;
  text-align: center;
  
  text {
    font-size: 28rpx;
    color: #94a3b8;
  }
}

.safe-bottom {
  height: env(safe-area-inset-bottom);
}
</style>
