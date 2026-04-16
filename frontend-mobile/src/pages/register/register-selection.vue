<template>
  <view class="selection-page">
    <view class="status-bar"></view>
    
    <!-- 顶部操作栏 -->
    <view class="top-bar">
      <view class="close-btn" @click="goBack">
        <text class="icon-close">✕</text>
      </view>
      <text class="nav-title">创建账号</text>
      <view class="help-btn">
        <text class="help-text">帮助</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content">
      <view class="header-section">
        <text class="main-title">请选择您的身份</text>
        <text class="sub-title">根据您的身份提供定制化的健康管理服务</text>
      </view>

      <view class="card-list">
        <view class="role-card patient-card" @click="goToPatientRegister">
          <view class="card-left">
            <view class="icon-wrapper">
              <text class="role-icon">👤</text>
            </view>
            <view class="info-wrapper">
              <text class="role-name">我是患者</text>
              <text class="role-desc">监测数据、查看报告、咨询医生</text>
            </view>
          </view>
          <text class="arrow-icon">›</text>
        </view>

        <view class="role-card doctor-card disabled">
          <view class="card-left">
            <view class="icon-wrapper">
              <text class="role-icon">👨‍⚕️</text>
            </view>
            <view class="info-wrapper">
              <text class="role-name">我是医生</text>
              <text class="role-desc">管理患者、在线沟通、临床笔记</text>
            </view>
          </view>
          <text class="tag-coming-soon">开发中</text>
        </view>
      </view>

      <view class="footer-tips">
        <text class="tips-text">已有账号？</text>
        <text class="login-link" @click="goBack">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
const goBack = () => {
  uni.navigateBack()
}

const goToPatientRegister = () => {
  uni.navigateTo({
    url: '/pages/register/patient-register'
  })
}
</script>

<style lang="scss" scoped>
.selection-page {
  min-height: 100vh;
  background-color: #F8F9FB;
  display: flex;
  flex-direction: column;
}

.status-bar {
  height: var(--status-bar-height);
  width: 100%;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 40rpx;
  background-color: #FFFFFF;
  
  .icon-close {
    font-size: 40rpx;
    color: #909399;
  }
  
  .nav-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #303133;
  }
  
  .help-text {
    font-size: 28rpx;
    color: #606266;
  }
}

.content {
  padding: 60rpx 40rpx;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header-section {
  margin-bottom: 80rpx;
  
  .main-title {
    font-size: 52rpx;
    font-weight: bold;
    color: #1a1a1a;
    display: block;
  }
  
  .sub-title {
    font-size: 28rpx;
    color: #909399;
    margin-top: 20rpx;
    display: block;
  }
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 40rpx;
}

.role-card {
  background-color: #FFFFFF;
  border-radius: 32rpx;
  padding: 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.03);
  transition: all 0.3s;
  border: 2rpx solid transparent;
  
  &:active:not(.disabled) {
    transform: translateY(-4rpx);
    box-shadow: 0 12rpx 32rpx rgba(110, 191, 247, 0.15);
    border-color: #6EBFF7;
  }
  
  &.disabled {
    opacity: 0.7;
    background-color: #F5F7FA;
  }
  
  .card-left {
    display: flex;
    align-items: center;
  }
  
  .icon-wrapper {
    width: 100rpx;
    height: 100rpx;
    background-color: #E6F4FF;
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 30rpx;
    
    .role-icon {
      font-size: 50rpx;
    }
  }
  
  .info-wrapper {
    display: flex;
    flex-direction: column;
    
    .role-name {
      font-size: 36rpx;
      font-weight: bold;
      color: #303133;
    }
    
    .role-desc {
      font-size: 24rpx;
      color: #909399;
      margin-top: 8rpx;
    }
  }
  
  .arrow-icon {
    font-size: 48rpx;
    color: #C0C4CC;
  }
  
  .tag-coming-soon {
    font-size: 20rpx;
    background-color: #EBEEF5;
    color: #909399;
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
  }
}

.footer-tips {
  margin-top: auto;
  padding-bottom: 60rpx;
  text-align: center;
  
  .tips-text {
    font-size: 28rpx;
    color: #909399;
  }
  
  .login-link {
    font-size: 28rpx;
    color: #6EBFF7;
    margin-left: 10rpx;
    font-weight: 500;
  }
}
</style>
