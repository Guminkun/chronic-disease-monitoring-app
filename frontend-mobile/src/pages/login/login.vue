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
      <text class="main-title">欢迎使用</text>
      <text class="app-name">慢病管理系统</text>
    </view>

    <!-- 微信一键登录 -->
    <view class="wechat-login-section">
      <view 
        class="wechat-login-btn"
        :class="{ 'btn-loading': loading }"
        @click="handleWechatLogin"
      >
        <view class="wechat-icon">
          <view class="icon-wechat-css">
            <view class="bubble-large">
              <view class="eyes"></view>
            </view>
            <view class="bubble-small">
              <view class="eyes"></view>
            </view>
          </view>
        </view>
        <text class="wechat-text">{{ loading ? '登录中...' : '微信一键登录' }}</text>
      </view>
    </view>

    <!-- 分隔线 -->
    <view class="divider-section">
      <view class="divider-line"></view>
      <text class="divider-text">其他登录方式</text>
      <view class="divider-line"></view>
    </view>

    <!-- 其他登录方式 -->
    <view class="other-login-section">
      <!-- 手机号/密码登录切换 -->
      <view class="login-tabs">
        <view 
          class="tab-item" 
          :class="{ active: loginType === 'password' }"
          @click="loginType = 'password'"
        >
          <text>密码登录</text>
        </view>
        <view 
          class="tab-item" 
          :class="{ active: loginType === 'sms' }"
          @click="loginType = 'sms'"
        >
          <text>验证码登录</text>
        </view>
      </view>

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

      <!-- 验证码输入 -->
      <view v-if="loginType === 'sms'" class="input-wrapper">
        <input 
          class="main-input"
          type="number"
          maxlength="6"
          v-model="smsCode"
          placeholder="输入验证码"
          placeholder-style="color: #C0C4CC"
        />
        <view class="sms-btn" :class="{ disabled: smsCountdown > 0 }" @click="sendSmsCode">
          <text>{{ smsCountdown > 0 ? `${smsCountdown}s` : '获取验证码' }}</text>
        </view>
      </view>

      <!-- 登录按钮 -->
      <view 
        class="login-btn" 
        :class="{ 'btn-disabled': !canSubmit }"
        @click="handleLogin"
      >
        <text class="login-btn-text">登录</text>
      </view>
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

    <!-- 底部注册入口 -->
    <view class="register-section">
      <text class="register-text">还没有账号？</text>
      <text class="register-link" @click="goRegister">立即注册</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { navigateAfterLogin } from '@/utils/auth'
import { sendSmsCode as sendSmsCodeApi } from '@/api/auth'

const userStore = useUserStore()
const loginType = ref<'sms' | 'password'>('password')
const phone = ref('')
const password = ref('')
const smsCode = ref('')
const showPassword = ref(false)
const agreeProtocol = ref(true)
const loading = ref(false)
const smsCountdown = ref(0)

const canSubmit = computed(() => {
  if (loginType.value === 'password') {
    return phone.value.length === 11 && password.value.length > 0 && agreeProtocol.value
  }
  return phone.value.length === 11 && smsCode.value.length >= 4 && agreeProtocol.value
})

onMounted(() => {
  // #ifdef MP-WEIXIN
  // 在微信小程序环境下，自动尝试微信登录
  autoWechatLogin()
  // #endif
})

const autoWechatLogin = async () => {
  const token = uni.getStorageSync('token')
  if (token) return
  
  loading.value = true
  try {
    await userStore.loginByWechat()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => navigateAfterLogin(), 800)
  } catch (e: any) {
    console.log('Auto wechat login failed:', e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  uni.navigateBack({ delta: 1 })
}

const showAreaCodePicker = () => {
  uni.showToast({ title: '暂仅支持+86', icon: 'none' })
}

const goRegister = () => {
  uni.navigateTo({ url: '/pages/register/patient-register' })
}

const sendSmsCode = async () => {
  if (smsCountdown.value > 0) return
  if (phone.value.length !== 11) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
    return
  }
  
  try {
    await sendSmsCodeApi({ phone: phone.value })
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    smsCountdown.value = 60
    const timer = setInterval(() => {
      smsCountdown.value--
      if (smsCountdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (e: any) {
    uni.showToast({ title: e.detail || '发送失败', icon: 'none' })
  }
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
      await userStore.loginBySms({ phone: phone.value, code: smsCode.value })
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
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
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
  text-align: center;
  
  .main-title {
    font-size: 48rpx;
    font-weight: 600;
    color: #1a1a1a;
    display: block;
  }
  
  .app-name {
    font-size: 56rpx;
    font-weight: bold;
    color: #07C160;
    margin-top: 20rpx;
    display: block;
  }
}

.wechat-login-section {
  margin-top: 100rpx;
  
  .wechat-login-btn {
    background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
    height: 100rpx;
    border-radius: 50rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8rpx 24rpx rgba(7, 193, 96, 0.3);
    
    &.btn-loading {
      opacity: 0.7;
    }
    
    .wechat-icon {
      margin-right: 20rpx;
    }
    
    .wechat-text {
      color: #FFFFFF;
      font-size: 34rpx;
      font-weight: 600;
    }
  }
}

.divider-section {
  display: flex;
  align-items: center;
  margin: 60rpx 0 40rpx;
  
  .divider-line {
    flex: 1;
    height: 1rpx;
    background-color: #E4E7ED;
  }
  
  .divider-text {
    font-size: 24rpx;
    color: #909399;
    padding: 0 20rpx;
  }
}

.other-login-section {
  background-color: #FFFFFF;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.login-tabs {
  display: flex;
  margin-bottom: 40rpx;
  border-bottom: 1rpx solid #EBEEF5;
  
  .tab-item {
    flex: 1;
    text-align: center;
    padding: 20rpx 0;
    font-size: 28rpx;
    color: #909399;
    position: relative;
    
    &.active {
      color: #07C160;
      font-weight: 600;
      
      &::after {
        content: '';
        position: absolute;
        bottom: -1rpx;
        left: 50%;
        transform: translateX(-50%);
        width: 60rpx;
        height: 4rpx;
        background-color: #07C160;
        border-radius: 2rpx;
      }
    }
  }
}

.input-wrapper {
  background-color: #F5F7FA;
  border-radius: 16rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid transparent;
  
  &:focus-within {
    background-color: #FFFFFF;
    border-color: #07C160;
  }
  
  .phone-prefix {
    display: flex;
    align-items: center;
    padding-right: 20rpx;
    
    .prefix-text {
      font-size: 30rpx;
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
    width: 1rpx;
    height: 40rpx;
    background-color: #DCDFE6;
    margin: 0 20rpx;
  }
  
  .main-input {
    flex: 1;
    font-size: 30rpx;
    color: #303133;
  }
  
  .eye-icon {
    padding: 10rpx;
    .icon-eye {
      font-size: 36rpx;
      color: #C0C4CC;
    }
  }
  
  .sms-btn {
    padding: 10rpx 20rpx;
    background-color: #07C160;
    border-radius: 8rpx;
    
    &.disabled {
      background-color: #E4E7ED;
    }
    
    text {
      font-size: 24rpx;
      color: #FFFFFF;
    }
  }
}

.login-btn {
  background: linear-gradient(135deg, #409EFF 0%, #3A8EE6 100%);
  height: 100rpx;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40rpx;
  box-shadow: 0 8rpx 20rpx rgba(64, 158, 255, 0.3);
  
  &.btn-disabled {
    opacity: 0.6;
    background: #C0C4CC;
    box-shadow: none;
  }
  
  .login-btn-text {
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 600;
  }
}

.agreement-section {
  margin-top: 40rpx;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  
  .checkbox-wrapper {
    padding-top: 4rpx;
    margin-right: 12rpx;
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
      background-color: #07C160;
      border-color: #07C160;
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
      color: #07C160;
    }
  }
}

.register-section {
  margin-top: 40rpx;
  text-align: center;
  
  .register-text {
    font-size: 26rpx;
    color: #909399;
  }
  
  .register-link {
    font-size: 26rpx;
    color: #07C160;
    font-weight: 500;
  }
}

/* CSS Icons */
.icon-wechat-css {
  width: 48rpx;
  height: 40rpx;
  position: relative;
  
  .bubble-large {
    width: 34rpx;
    height: 28rpx;
    background-color: #FFFFFF;
    border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
    position: absolute;
    top: 0;
    left: 0;
    
    .eyes {
      width: 4rpx;
      height: 4rpx;
      background-color: #07C160;
      border-radius: 50%;
      position: absolute;
      top: 10rpx;
      left: 8rpx;
      box-shadow: 16rpx 0 #07C160;
    }
  }
  
  .bubble-small {
    width: 28rpx;
    height: 22rpx;
    background-color: #FFFFFF;
    border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
    position: absolute;
    bottom: 0;
    right: 0;
    
    .eyes {
      width: 3rpx;
      height: 3rpx;
      background-color: #07C160;
      border-radius: 50%;
      position: absolute;
      top: 8rpx;
      left: 6rpx;
      box-shadow: 12rpx 0 #07C160;
    }
  }
}
</style>
