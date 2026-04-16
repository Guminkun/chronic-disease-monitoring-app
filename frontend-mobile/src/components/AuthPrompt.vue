<template>
  <view class="auth-prompt" :class="[`theme-${theme}`, `size-${size}`]">
    <!-- 背景装饰 -->
    <view class="bg-decoration">
      <view class="circle circle-1"></view>
      <view class="circle circle-2"></view>
    </view>

    <!-- 内容区域 -->
    <view class="content-wrapper">
      <!-- 图标区域 -->
      <view class="icon-section">
        <view class="icon-container" :style="{ backgroundColor: iconBgColor }">
          <text class="icon" :style="{ color: iconColor }">{{ icon }}</text>
        </view>
      </view>

      <!-- 文本区域 -->
      <view class="text-section">
        <text class="title">{{ title }}</text>
        <text class="description">{{ description }}</text>
      </view>

      <!-- 操作区域 -->
      <view class="action-section">
        <view class="login-btn" @click="handleLoginClick">
          <text class="btn-text">{{ buttonText }}</text>
          <text class="btn-arrow">→</text>
        </view>
      </view>
    </view>

    <!-- 底部装饰线 -->
    <view class="bottom-accent"></view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  description?: string
  buttonText?: string
  icon?: string
  theme?: 'primary' | 'success' | 'warning' | 'info'
  size?: 'small' | 'medium' | 'large'
  redirectUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '登录以使用完整功能',
  description: '登录后可管理慢病、记录用药、监测健康',
  buttonText: '立即登录',
  icon: '🔐',
  theme: 'primary',
  size: 'medium',
  redirectUrl: ''
})

const themeColors = {
  primary: { bg: '#EFF6FF', iconBg: '#3B82F6', icon: '#FFFFFF', accent: '#3B82F6' },
  success: { bg: '#F0FDF4', iconBg: '#22C55E', icon: '#FFFFFF', accent: '#22C55E' },
  warning: { bg: '#FFF7ED', iconBg: '#F97316', icon: '#FFFFFF', accent: '#F97316' },
  info: { bg: '#F8FAFC', iconBg: '#64748B', icon: '#FFFFFF', accent: '#64748B' }
}

const iconBgColor = computed(() => themeColors[props.theme].iconBg)
const iconColor = computed(() => themeColors[props.theme].icon)

const handleLoginClick = () => {
  const currentPath = getCurrentPages()[0]?.route || ''
  const redirect = props.redirectUrl || `/${currentPath}`
  uni.navigateTo({
    url: `/pages/login/login?redirect=${encodeURIComponent(redirect)}`
  })
}
</script>

<style lang="scss" scoped>
/* CSS Variables for Design Tokens */
.auth-prompt {
  --spacing-xs: 16rpx;
  --spacing-sm: 24rpx;
  --spacing-md: 32rpx;
  --spacing-lg: 48rpx;
  --spacing-xl: 64rpx;
  
  --radius-sm: 12rpx;
  --radius-md: 20rpx;
  --radius-lg: 28rpx;
  
  --shadow-sm: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  --shadow-md: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 16rpx 48rpx rgba(0, 0, 0, 0.12);
  
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  margin: 24rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  /* Background */
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  box-shadow: var(--shadow-md);
  
  &:active {
    transform: scale(0.98);
    box-shadow: var(--shadow-sm);
  }
}

/* Background Decoration */
.bg-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200rpx;
  height: 200rpx;
  overflow: hidden;
  pointer-events: none;
  
  .circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.08;
    
    &.circle-1 {
      width: 300rpx;
      height: 300rpx;
      top: -100rpx;
      right: -100rpx;
    }
    
    &.circle-2 {
      width: 200rpx;
      height: 200rpx;
      top: -50rpx;
      right: -50rpx;
      opacity: 0.05;
    }
  }
}

/* Theme Variations */
.theme-primary .bg-decoration .circle {
  background: #3B82F6;
}

.theme-success .bg-decoration .circle {
  background: #22C55E;
}

.theme-warning .bg-decoration .circle {
  background: #F97316;
}

.theme-info .bg-decoration .circle {
  background: #64748B;
}

.theme-primary .bottom-accent {
  background: linear-gradient(90deg, #3B82F6 0%, #60A5FA 100%);
}

.theme-success .bottom-accent {
  background: linear-gradient(90deg, #22C55E 0%, #4ADE80 100%);
}

.theme-warning .bottom-accent {
  background: linear-gradient(90deg, #F97316 0%, #FB923C 100%);
}

.theme-info .bottom-accent {
  background: linear-gradient(90deg, #64748B 0%, #94A3B8 100%);
}

/* Content Wrapper */
.content-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  gap: var(--spacing-sm);
}

/* Icon Section */
.icon-section {
  flex-shrink: 0;
}

.icon-container {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.15);
  
  .icon {
    font-size: 48rpx;
    line-height: 1;
  }
}

/* Text Section */
.text-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description {
  font-size: 26rpx;
  color: #64748B;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Action Section */
.action-section {
  flex-shrink: 0;
}

.login-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 28rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: var(--radius-md);
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3);
  transition: all 0.2s ease;
  
  &:active {
    transform: scale(0.95);
  }
  
  .btn-text {
    font-size: 28rpx;
    font-weight: 500;
    color: #FFFFFF;
  }
  
  .btn-arrow {
    font-size: 32rpx;
    color: #FFFFFF;
    transition: transform 0.2s ease;
  }
}

.auth-prompt:active .login-btn .btn-arrow {
  transform: translateX(8rpx);
}

/* Bottom Accent */
.bottom-accent {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 6rpx;
  opacity: 0.8;
}

/* Size Variations */
.size-small {
  .content-wrapper {
    padding: var(--spacing-sm);
    gap: var(--spacing-xs);
  }
  
  .icon-container {
    width: 72rpx;
    height: 72rpx;
    
    .icon {
      font-size: 36rpx;
    }
  }
  
  .title {
    font-size: 28rpx;
  }
  
  .description {
    font-size: 24rpx;
  }
  
  .login-btn {
    padding: 12rpx 20rpx;
    
    .btn-text {
      font-size: 26rpx;
    }
  }
}

.size-large {
  .content-wrapper {
    padding: var(--spacing-lg);
    gap: var(--spacing-md);
  }
  
  .icon-container {
    width: 120rpx;
    height: 120rpx;
    
    .icon {
      font-size: 56rpx;
    }
  }
  
  .title {
    font-size: 36rpx;
  }
  
  .description {
    font-size: 28rpx;
  }
  
  .login-btn {
    padding: 20rpx 36rpx;
    
    .btn-text {
      font-size: 30rpx;
    }
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .auth-prompt,
  .login-btn,
  .btn-arrow {
    transition: none;
  }
}

/* Focus States (for keyboard navigation) */
.login-btn:focus {
  outline: 3rpx solid #3B82F6;
  outline-offset: 2rpx;
}
</style>
