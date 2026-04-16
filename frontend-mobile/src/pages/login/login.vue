<template>
  <view class="login-page">
    <!-- 顶部操作栏 -->
    <view class="top-bar">
      <view class="close-btn" @click="goBack">
        <text class="icon-close">✕</text>
      </view>
      <view class="help-btn">
        <text class="help-text">帮助</text>
      </view>
    </view>

    <!-- 主标题区域 -->
    <view class="header-section">
      <text class="main-title">{{ loginType === 'password' ? '密码登录' : '手机号登录' }}</text>
      <text class="sub-title">未注册的手机号登录成功后将自动注册</text>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <!-- 手机号输入 -->
      <view class="input-wrapper">
        <view class="phone-prefix" @click="showAreaCodePicker">
          <text class="prefix-text">+86</text>
          <text class="arrow-down">▼</text>
        </view>
        <view class="vertical-line"></view>
        <input 
          class="main-input"
          type="number"
          maxlength="11"
          v-model="phone"
          placeholder="输入手机号"
          placeholder-style="color: #C0C4CC"
        />
      </view>

      <!-- 密码输入 (仅在密码登录模式下显示) -->
      <view v-if="loginType === 'password'" class="input-wrapper password-wrapper">
        <input 
          class="main-input"
          :secure-text-entry="!showPassword"
          v-model="password"
          placeholder="输入密码"
          placeholder-style="color: #C0C4CC"
        />
        <view class="eye-icon" @click="showPassword = !showPassword">
          <text class="icon-eye">{{ showPassword ? '👁️' : '👁️‍🗨️' }}</text>
        </view>
      </view>

      <!-- 登录按钮 -->
      <view 
        class="login-btn" 
        :class="{ 'btn-disabled': !canSubmit }"
        @click="handleLogin"
      >
        <text class="login-btn-text">{{ loginType === 'password' ? '登录' : '验证并登录' }}</text>
      </view>

      <!-- 协议勾选 -->
      <view class="agreement-section">
        <view class="checkbox-wrapper" @click="agreeProtocol = !agreeProtocol">
          <view class="checkbox" :class="{ checked: agreeProtocol }">
            <text v-if="agreeProtocol" class="check-mark">✓</text>
          </view>
        </view>
        <view class="agreement-text">
          已阅读并同意<text class="link-text">服务协议</text>和<text class="link-text">隐私保护指引</text>
        </view>
      </view>
    </view>

    <!-- 底部快捷登录 -->
    <view class="quick-login-section">
      <!-- 微信登录 -->
      <view class="quick-login-item" @click="handleWechatLogin">
        <view class="icon-circle wechat-bg">
          <view class="icon-wechat-css">
            <view class="bubble-large">
              <view class="eyes"></view>
            </view>
            <view class="bubble-small">
              <view class="eyes"></view>
            </view>
          </view>
        </view>
        <text class="item-label">微信登录</text>
      </view>
      
      <!-- 手机号登录 -->
      <view class="quick-login-item" @click="loginType = 'sms'">
        <view class="icon-circle" :class="loginType === 'sms' ? 'blue-bg' : 'gray-bg'">
          <view class="icon-phone-css" :class="{ 'active': loginType === 'sms' }"></view>
        </view>
        <text class="item-label">手机号登录</text>
      </view>

      <!-- 密码登录 -->
      <view class="quick-login-item" @click="loginType = 'password'">
        <view class="icon-circle" :class="loginType === 'password' ? 'blue-bg' : 'gray-bg'">
          <view class="icon-lock-css" :class="{ 'active': loginType === 'password' }"></view>
        </view>
        <text class="item-label">密码登录</text>
      </view>

      <!-- 注册 -->
      <view class="quick-login-item" @click="goRegister">
        <view class="icon-circle gray-bg">
          <view class="icon-register-css"></view>
        </view>
        <text class="item-label">注册</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { navigateAfterLogin } from '@/utils/auth'

const userStore = useUserStore()
const loginType = ref<'sms' | 'password'>('password')
const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const agreeProtocol = ref(false)
const loading = ref(false)

const canSubmit = computed(() => {
  if (loginType.value === 'password') {
    return phone.value.length === 11 && password.value.length > 0 && agreeProtocol.value
  }
  return phone.value.length === 11 && agreeProtocol.value
})

const goBack = () => {
  uni.navigateBack({ delta: 1 })
}

const showAreaCodePicker = () => {
  uni.showToast({ title: '暂仅支持+86', icon: 'none' })
}

const goRegister = () => {
  uni.navigateTo({ url: '/pages/register/patient-register' })
}

const handleLogin = async () => {
  if (!canSubmit.value) {
    if (!agreeProtocol.value) {
      uni.showToast({ title: '请阅读并同意协议', icon: 'none' })
    }
    return
  }

  loading.value = true
  try {
    if (loginType.value === 'password') {
      await userStore.login({ username: phone.value, password: password.value })
    } else {
      // 验证码登录逻辑（当前后端未支持，暂留空或提示）
      uni.showToast({ title: '验证码登录功能开发中', icon: 'none' })
      return
    }
    
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => navigateAfterLogin(), 800)
  } catch (e: any) {
    uni.showToast({ title: e.detail || e.message || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const handleWechatLogin = async () => {
  if (!agreeProtocol.value) {
    uni.showToast({ title: '请阅读并同意协议', icon: 'none' })
    return
  }
  
  loading.value = true
  try {
    await userStore.loginByWechat()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => navigateAfterLogin(), 800)
  } catch (e: any) {
    uni.showToast({ title: e.detail || e.message || '微信登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background-color: var(--color-bg-base);
  padding: 40rpx 60rpx;
  display: flex;
  flex-direction: column;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 60rpx;
  
  .icon-close {
    font-size: 40rpx;
    color: #909399;
  }
  
  .help-text {
    font-size: 30rpx;
    color: #606266;
  }
}

.header-section {
  margin-top: 100rpx;
  
  .main-title {
    font-size: 56rpx;
    font-weight: bold;
    color: #1a1a1a;
    display: block;
  }
  
  .sub-title {
    font-size: 28rpx;
    color: #C0C4CC;
    margin-top: 20rpx;
    display: block;
  }
}

.form-section {
  margin-top: 80rpx;
  flex: 1;
}

.input-wrapper {
  background-color: #FFFFFF;
  border-radius: 24rpx;
  height: 110rpx;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.15);
  transition: all 0.3s ease;
  
  &:focus-within {
    box-shadow: 0 6rpx 20rpx rgba(59, 130, 246, 0.12), 0 0 0 2rpx rgba(59, 130, 246, 0.2);
    border-color: var(--color-primary);
  }
  
  .phone-prefix {
    display: flex;
    align-items: center;
    padding-right: 20rpx;
    
    .prefix-text {
      font-size: 32rpx;
      color: #303133;
      font-weight: 500;
    }
    
    .arrow-down {
      font-size: 20rpx;
      color: #909399;
      margin-left: 10rpx;
    }
  }
  
  .vertical-line {
    width: 2rpx;
    height: 40rpx;
    background-color: #EBEEF5;
    margin: 0 20rpx;
  }
  
  .main-input {
    flex: 1;
    font-size: 32rpx;
    color: #303133;
  }
  
  .eye-icon {
    padding: 10rpx;
    .icon-eye {
      font-size: 36rpx;
      color: #C0C4CC;
    }
  }
}

.login-btn {
  background-color: #6EBFF7;
  height: 100rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 60rpx;
  box-shadow: 0 8rpx 20rpx rgba(110, 191, 247, 0.3);
  
  &.btn-disabled {
    opacity: 0.6;
  }
  
  .login-btn-text {
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
  }
}

.agreement-section {
  margin-top: 40rpx;
  display: flex;
  align-items: flex-start;
  
  .checkbox-wrapper {
    padding-top: 4rpx;
    margin-right: 16rpx;
  }
  
  .checkbox {
    width: 32rpx;
    height: 32rpx;
    border: 2rpx solid #DCDFE6;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.checked {
      background-color: #6EBFF7;
      border-color: #6EBFF7;
    }
    
    .check-mark {
      color: #FFFFFF;
      font-size: 20rpx;
    }
  }
  
  .agreement-text {
    font-size: 24rpx;
    color: #909399;
    line-height: 1.4;
    
    .link-text {
      color: #6EBFF7;
    }
  }
}

.quick-login-section {
  display: flex;
  justify-content: space-around;
  padding-bottom: 120rpx;
  margin-top: 40rpx;
  
  .quick-login-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .icon-circle {
      width: 84rpx;
      height: 84rpx;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12rpx;
      background-color: #FFFFFF;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
      
      &.blue-bg {
        background-color: #F0F7FF;
        border: 2rpx solid #D1E9FF;
      }
      
      &.gray-bg {
        color: #606266;
        background-color: #F5F7FA;
        border: 2rpx solid #EBEEF5;
      }
    }
    
    .item-label {
      font-size: 22rpx;
      color: #909399;
    }

    /* CSS Icons */
    .icon-wechat-css {
      width: 42rpx;
      height: 36rpx;
      position: relative;
      
      .bubble-large {
        width: 30rpx;
        height: 25rpx;
        background-color: #07C160;
        border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
        position: absolute;
        top: 0;
        left: 0;
        
        .eyes {
          width: 3rpx;
          height: 3rpx;
          background-color: #FFF;
          border-radius: 50%;
          position: absolute;
          top: 8rpx;
          left: 6rpx;
          box-shadow: 14rpx 0 #FFF;
        }
      }
      
      .bubble-small {
        width: 24rpx;
        height: 20rpx;
        background-color: #07C160;
        border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
        position: absolute;
        bottom: 0;
        right: 0;
        border: 1.5rpx solid #FFF;
        
        .eyes {
          width: 2.5rpx;
          height: 2.5rpx;
          background-color: #FFF;
          border-radius: 50%;
          position: absolute;
          top: 7rpx;
          left: 5rpx;
          box-shadow: 10rpx 0 #FFF;
        }
      }
    }
    
    .icon-phone-css {
      width: 24rpx;
      height: 40rpx;
      border: 3rpx solid #606266;
      border-radius: 5rpx;
      position: relative;
      
      &.active {
        border-color: #1890FF;
        &::after { background-color: #1890FF; }
      }
      
      &::after {
        content: '';
        position: absolute;
        bottom: 5rpx;
        left: 50%;
        transform: translateX(-50%);
        width: 10rpx;
        height: 2rpx;
        background-color: #606266;
        border-radius: 2rpx;
      }
    }
    
    .icon-lock-css {
      width: 28rpx;
      height: 24rpx;
      background-color: #606266;
      border-radius: 4rpx;
      position: relative;
      margin-top: 12rpx;
      
      &.active {
        background-color: #1890FF;
        &::before { border-color: #1890FF; }
      }
      
      &::before {
        content: '';
        position: absolute;
        top: -14rpx;
        left: 50%;
        transform: translateX(-50%);
        width: 18rpx;
        height: 16rpx;
        border: 3rpx solid #606266;
        border-bottom: none;
        border-radius: 10rpx 10rpx 0 0;
      }
    }
    
    .icon-register-css {
      width: 30rpx;
      height: 30rpx;
      position: relative;
      
      &::before, &::after {
        content: '';
        position: absolute;
        background-color: #606266;
        border-radius: 2rpx;
      }
      
      &::before {
        width: 100%;
        height: 3rpx;
        top: 50%;
        left: 0;
        transform: translateY(-50%);
      }
      
      &::after {
        width: 3rpx;
        height: 100%;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
      }
    }
  }
}
</style>
