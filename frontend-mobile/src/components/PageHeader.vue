<template>
  <view class="page-header" :class="{ 'has-subtitle': subtitle }">
    <!-- 返回按钮 -->
    <view class="header-back" @click="handleBack">
      <text class="back-icon">‹</text>
      <text v-if="showBackText" class="back-text">返回</text>
    </view>
    
    <!-- 标题区域 -->
    <view class="header-content">
      <text class="header-title">{{ title }}</text>
      <text v-if="subtitle" class="header-subtitle">{{ subtitle }}</text>
    </view>
    
    <!-- 右侧插槽 -->
    <view class="header-right">
      <slot name="right"></slot>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  /** 页面标题 */
  title: string
  /** 副标题 */
  subtitle?: string
  /** 是否显示返回文字 */
  showBackText?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showBackText: false
})

/**
 * 返回上一页
 * 如果没有上一页，则跳转到首页
 */
const handleBack = () => {
  const pages = getCurrentPages()
  
  if (pages.length <= 1) {
    // 没有上一页，跳转到 tabbar 首页
    uni.switchTab({
      url: '/pages/index/index',
      fail: () => {
        uni.reLaunch({
          url: '/pages/index/index'
        })
      }
    })
  } else {
    uni.navigateBack({
      fail: () => {
        uni.switchTab({
          url: '/pages/index/index'
        })
      }
    })
  }
}
</script>

<style scoped>
/* 导航栏容器 */
.page-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 56px;
  padding: 0 16px;
  padding-top: env(safe-area-inset-top);
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 有副标题时增加高度 */
.page-header.has-subtitle {
  height: 64px;
}

/* 返回按钮 */
.header-back {
  display: flex;
  align-items: center;
  padding: 8px;
  margin-left: -8px;
  flex-shrink: 0;
}

.back-icon {
  font-size: 28px;
  color: #1e293b;
  font-weight: 300;
  line-height: 1;
}

.back-text {
  font-size: 15px;
  color: #64748b;
  font-weight: 500;
  margin-left: 2px;
}

/* 标题区域 */
.header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 4px 0;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 0.2px;
  text-align: center;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  text-align: center;
  line-height: 1.2;
}

/* 右侧区域 */
.header-right {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  flex-shrink: 0;
}
</style>