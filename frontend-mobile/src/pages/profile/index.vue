<template>
  <view class="container">
    <view class="profile-header">
      <view class="user-info" v-if="userStore.token" @click="handleEditProfile">
        <view class="avatar">
          <image 
            v-if="userStore.user?.wechat_avatar" 
            :src="userStore.user.wechat_avatar" 
            class="avatar-image"
            mode="aspectFill"
          />
          <text v-else class="avatar-text">{{ userInitial }}</text>
        </view>
        <view class="info-content">
          <text class="user-name">{{ userStore.user?.wechat_nickname || userStore.user?.name || '用户' }}</text>
          <text class="user-role">患者端</text>
        </view>
      </view>
      <view class="user-info" v-else @click="goToLogin">
        <view class="avatar placeholder">
          <text class="avatar-text">?</text>
        </view>
        <view class="info-content">
          <text class="user-name">点击登录</text>
          <text class="user-role">登录后查看更多信息</text>
        </view>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" @click="handleEditProfile">
        <view class="menu-left">
          <text class="icon">📝</text>
          <text class="menu-text">修改个人信息</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="menu-item" @click="goToMedicationHistory">
        <view class="menu-left">
          <text class="icon">📋</text>
          <text class="menu-text">历史用药</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="menu-item" @click="goToFeedback">
        <view class="menu-left">
          <text class="icon">💬</text>
          <text class="menu-text">意见反馈</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="menu-item" @click="goToUsageGuide">
        <view class="menu-left">
          <text class="icon">📖</text>
          <text class="menu-text">使用说明</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="menu-item" @click="handleSettings">
        <view class="menu-left">
          <text class="icon">⚙️</text>
          <text class="menu-text">系统设置</text>
        </view>
        <text class="arrow">›</text>
      </view>
      
      <view class="menu-item" @click="checkVersion">
        <view class="menu-left">
          <text class="icon">ℹ️</text>
          <text class="menu-text">查看版本</text>
        </view>
        <text class="version-text">v1.0.0</text>
      </view>
    </view>

    <view class="logout-section" v-if="userStore.token">
      <button class="btn-logout" @click="handleLogout">退出登录</button>
    </view>
    
    <!-- 自定义 TabBar -->
    <CustomTabBar :current="3" />
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { checkLoginWithRedirect } from '@/utils/auth'
import CustomTabBar from '@/components/tabbar/CustomTabBar.vue'

const userStore = useUserStore()

const userInitial = computed(() => {
  const name = userStore.user?.name || ''
  return name ? name.charAt(0) : 'U'
})

const goToLogin = () => {
  checkLoginWithRedirect('/pages/profile/index')
}

const handleEditProfile = () => {
  if (!userStore.token) return goToLogin()
  uni.navigateTo({ url: '/pages/profile/edit' })
}

const goToMedicationHistory = () => {
  if (!userStore.token) return goToLogin()
  uni.navigateTo({ url: '/pages/medication/history' })
}

const goToFeedback = () => {
  if (!userStore.token) return goToLogin()
  uni.navigateTo({ url: '/pages/feedback/submit' })
}

const goToUsageGuide = () => {
  uni.navigateTo({ url: '/pages/usage-guide/index' })
}

const handleSettings = () => {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

const checkVersion = () => {
  uni.showModal({
    title: '版本信息',
    content: '当前版本：v1.0.0\n已是最新版本',
    showCancel: false
  })
}

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  padding: 16px;
  padding-bottom: 120rpx;
}

.profile-header {
  background-color: var(--color-bg-elevated);
  padding: 24px;
  border-radius: 16px;
  margin-top: 16px;
  box-shadow: var(--shadow-sm);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 32px;
  background-color: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #dbeafe;
  overflow: hidden;
}
.placeholder {
  background-color: #f1f5f9;
  border-color: #e2e8f0;
}
.avatar-text {
  font-size: 24px;
  font-weight: bold;
  color: #3b82f6;
}
.avatar-image {
  width: 100%;
  height: 100%;
}

.info-content {
  flex: 1;
}
.user-name {
  font-size: 20px;
  font-weight: bold;
  color: #1e293b;
  display: block;
}
.user-role {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

.menu-list {
  margin-top: 24px;
  background-color: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-item:active {
  background-color: #f8fafc;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.icon {
  font-size: 20px;
}
.menu-text {
  font-size: 16px;
  color: #334155;
}

.arrow {
  color: #cbd5e1;
  font-size: 20px;
  font-weight: 300;
  line-height: 1;
}
.version-text {
  font-size: 14px;
  color: #94a3b8;
}

.logout-section {
  margin-top: 40px;
}
.btn-logout {
  background-color: #fee2e2;
  color: #ef4444;
  border-radius: 12px;
  font-size: 16px;
  border: none;
}
.btn-logout:active {
  background-color: #fecaca;
}
</style>