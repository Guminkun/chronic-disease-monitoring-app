<template>
  <view class="custom-tabbar">
    <view class="tabbar-container">
      <!-- 首页 -->
      <view 
        class="tab-item"
        :class="{ 'tab-active': currentIndex === 0 }"
        @click="switchTab(0)"
      >
        <text class="tab-text">{{ tabList[0].text }}</text>
      </view>
      
      <!-- 用药 -->
      <view 
        class="tab-item"
        :class="{ 'tab-active': currentIndex === 1 }"
        @click="switchTab(1)"
      >
        <text class="tab-text">{{ tabList[1].text }}</text>
      </view>
      
      <!-- 添加按钮 -->
      <view class="tab-add-btn" @click="openQuickAdd">
        <text class="add-icon">+</text>
      </view>
      
      <!-- 监测 -->
      <view 
        class="tab-item"
        :class="{ 'tab-active': currentIndex === 2 }"
        @click="switchTab(2)"
      >
        <text class="tab-text">{{ tabList[2].text }}</text>
      </view>
      
      <!-- 我的 -->
      <view 
        class="tab-item"
        :class="{ 'tab-active': currentIndex === 3 }"
        @click="switchTab(3)"
      >
        <text class="tab-text">{{ tabList[3].text }}</text>
      </view>
    </view>
    
    <!-- 快速添加面板 -->
    <view v-if="quickAddVisible" class="quick-add-overlay" @click="closeQuickAdd">
      <view class="quick-add-sheet" @click.stop>
        <view class="sheet-handle"></view>
        <view class="sheet-header">
          <text class="sheet-title">快速添加</text>
          <view class="sheet-close" @click="closeQuickAdd">
            <text>✕</text>
          </view>
        </view>
        
        <view class="quick-add-grid">
          <view class="quick-item" @click="handleQuickAdd('record')">
            <view class="quick-icon-box bg-warm-1">
              <text class="quick-emoji">📋</text>
            </view>
            <text class="quick-label">添加病历</text>
          </view>
          
          <view class="quick-item" @click="handleQuickAdd('monitor')">
            <view class="quick-icon-box bg-warm-2">
              <text class="quick-emoji">📈</text>
            </view>
            <text class="quick-label">添加监测</text>
          </view>
          
          <view class="quick-item" @click="handleQuickAdd('report')">
            <view class="quick-icon-box bg-warm-3">
              <text class="quick-emoji">📊</text>
            </view>
            <text class="quick-label">添加报告</text>
          </view>
          
          <view class="quick-item" @click="handleQuickAdd('disease')">
            <view class="quick-icon-box bg-warm-4">
              <text class="quick-emoji">❤️</text>
            </view>
            <text class="quick-label">添加慢病</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { checkLoginWithRedirect } from '@/utils/auth'

const userStore = useUserStore()
const props = defineProps<{
  current: number
}>()

const emit = defineEmits<{
  (e: 'change', index: number): void
}>()

const currentIndex = computed(() => props.current)
const quickAddVisible = ref(false)

const tabList = [
  { text: '首页', pagePath: '/pages/index/index' },
  { text: '用药', pagePath: '/pages/medication/index' },
  { text: '监测', pagePath: '/pages/monitor/index' },
  { text: '我的', pagePath: '/pages/profile/index' }
]

const switchTab = (index: number) => {
  if (index === currentIndex.value) return
  uni.switchTab({ url: tabList[index].pagePath })
  emit('change', index)
}

const openQuickAdd = () => {
  if (!userStore.token) {
    checkLoginWithRedirect()
    return
  }
  quickAddVisible.value = true
}

const closeQuickAdd = () => {
  quickAddVisible.value = false
}

const handleQuickAdd = (type: string) => {
  quickAddVisible.value = false
  
  const routes: Record<string, string> = {
    record: '/pages/medical-record/upload',
    monitor: '/pages/monitor/index',
    report: '/pages/report/upload',
    disease: '/pages/disease/manage'
  }
  
  if (type === 'monitor') {
    uni.switchTab({ url: routes[type] })
  } else {
    uni.navigateTo({ url: routes[type] })
  }
}
</script>

<style scoped>
/* 导航栏容器 */
.custom-tabbar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: #f5f7fa;
  border-top: 1px solid #e8ecf0;
  padding-bottom: env(safe-area-inset-bottom);
}

.tabbar-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
  height: 100rpx;
  padding: 0 16rpx;
}

/* Tab 项 - 纯文字 */
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16rpx 0;
  transition: opacity 0.2s ease;
}

.tab-item:active {
  opacity: 0.7;
}

.tab-text {
  font-size: 26rpx;
  color: #9ca3af;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-active .tab-text {
  color: #1f2937;
  font-weight: 700;
  font-size: 28rpx;
}

/* 添加按钮 - 圆矩形 */
.tab-add-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx 0;
}

.add-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80rpx;
  height: 56rpx;
  background: #9ea4ac;
  border-radius: 28rpx;
  font-size: 40rpx;
  color: #ffffff;
  font-weight: 300;
  line-height: 1;
  transition: all 0.2s ease;
}

.tab-add-btn:active .add-icon {
  background: #7a8490;
  transform: scale(0.96);
}

/* 快速添加面板 */
.quick-add-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.quick-add-sheet {
  width: 100%;
  background: #ffffff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 24rpx 32rpx 48rpx;
  animation: slideUp 0.25s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.sheet-handle {
  width: 64rpx;
  height: 6rpx;
  background: #d1d5db;
  border-radius: 3rpx;
  margin: 0 auto 24rpx;
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.sheet-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #111827;
}

.sheet-close {
  width: 56rpx;
  height: 56rpx;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sheet-close text {
  font-size: 24rpx;
  color: #6b7280;
}

/* 快速添加网格 */
.quick-add-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}

.quick-item:active {
  opacity: 0.8;
}

.quick-icon-box {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 温暖色调 */
.bg-warm-1 { background: #fef3c7; }
.bg-warm-2 { background: #d1fae5; }
.bg-warm-3 { background: #fce7f3; }
.bg-warm-4 { background: #fee2e2; }

.quick-emoji {
  font-size: 44rpx;
}

.quick-label {
  font-size: 22rpx;
  color: #374151;
  font-weight: 600;
  text-align: center;
}
</style>
