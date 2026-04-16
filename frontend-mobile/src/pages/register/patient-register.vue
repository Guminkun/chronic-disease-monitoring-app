<template>
  <view class="register-page">
    <view class="status-bar"></view>
    
    <!-- 顶部操作栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="goBack">
        <text class="icon-back">‹</text>
      </view>
      <text class="nav-title">用户注册</text>
      <view class="help-btn">
        <text class="help-text">帮助</text>
      </view>
    </view>

    <!-- 主内容区域 -->
    <view class="content">
      <view class="header-section">
        <text class="main-title">欢迎加入</text>
        <text class="sub-title">请填写以下信息完成注册，开启健康之旅</text>
      </view>

      <view class="form-section">
        <!-- 账号信息 -->
        <view class="section-group">
          <text class="section-label">账号信息</text>
          
          <!-- 手机号 -->
          <view class="input-wrapper">
            <view class="icon-line-phone"></view>
            <input 
              class="main-input"
              type="number"
              maxlength="11"
              v-model="form.phone"
              placeholder="请输入手机号"
              placeholder-style="color: #C0C4CC"
            />
          </view>

          <!-- 验证码 -->
          <view class="input-wrapper code-wrapper">
            <view class="icon-line-code"></view>
            <input 
              class="main-input"
              type="number"
              maxlength="6"
              v-model="form.code"
              placeholder="请输入验证码"
              placeholder-style="color: #C0C4CC"
            />
            <view 
              class="get-code-btn" 
              :class="{ disabled: countdown > 0 || !isPhoneValid }"
              @click="handleGetCode"
            >
              <text class="code-btn-text">{{ countdown > 0 ? `${countdown}s后重发` : '获取验证码' }}</text>
            </view>
          </view>

          <!-- 密码 -->
          <view class="input-wrapper">
            <view class="icon-line-lock"></view>
            <input 
              class="main-input"
              :secure-text-entry="!showPassword"
              v-model="form.password"
              placeholder="设置登录密码 (至少6位)"
              placeholder-style="color: #C0C4CC"
            />
            <view class="eye-icon" @click="showPassword = !showPassword">
              <text class="icon-eye">{{ showPassword ? '👁️' : '👁️‍G' }}</text>
            </view>
          </view>
        </view>

        <!-- 个人信息 -->
        <view class="section-group">
          <text class="section-label">个人资料</text>
          
          <view class="input-wrapper">
            <view class="icon-line-user"></view>
            <input 
              class="main-input"
              type="text"
              v-model="form.name"
              placeholder="真实姓名"
              placeholder-style="color: #C0C4CC"
            />
          </view>

          <view class="input-wrapper">
            <view class="icon-line-age"></view>
            <input 
              class="main-input"
              type="number"
              maxlength="3"
              v-model="form.age"
              placeholder="年龄"
              placeholder-style="color: #C0C4CC"
            />
          </view>

          <view class="gender-selector">
            <view 
              class="gender-item" 
              :class="{ active: form.gender === 'male' }"
              @click="form.gender = 'male'"
            >
              <view class="icon-line-male" :class="{ active: form.gender === 'male' }"></view>
              <text class="gender-text">男</text>
            </view>
            <view 
              class="gender-item" 
              :class="{ active: form.gender === 'female' }"
              @click="form.gender = 'female'"
            >
              <view class="icon-line-female" :class="{ active: form.gender === 'female' }"></view>
              <text class="gender-text">女</text>
            </view>
          </view>
        </view>

        <!-- 注册按钮 -->
        <view 
          class="register-btn" 
          :class="{ 'btn-disabled': !canSubmit || loading }"
          @click="handleRegister"
        >
          <text class="btn-text">{{ loading ? '注册中...' : '立即注册' }}</text>
        </view>

        <!-- 登录跳转 -->
        <view class="login-link" @click="goBack">
          <text class="link-text">已有账号？立即登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onUnmounted } from 'vue'
import { registerPatient } from '@/api/auth'

const loading = ref(false)
const showPassword = ref(false)
const countdown = ref(0)
let timer: any = null

const form = reactive({
  phone: '',
  code: '',
  password: '',
  name: '',
  age: '',
  gender: 'male'
})

const isPhoneValid = computed(() => form.phone.length === 11)

const canSubmit = computed(() => {
  return isPhoneValid.value && 
         form.code.length >= 4 &&
         form.password.length >= 6 && 
         form.name.trim().length >= 2 && 
         form.age.length > 0
})

const goBack = () => {
  uni.navigateBack()
}

const handleGetCode = () => {
  if (countdown.value > 0 || !isPhoneValid.value) return
  
  uni.showToast({ title: '验证码已发送', icon: 'none' })
  countdown.value = 60
  timer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(timer)
    }
  }, 1000)
}

const handleRegister = async () => {
  if (!canSubmit.value || loading.value) return
  
  loading.value = true
  const payload = {
    user: {
      phone: form.phone,
      password: form.password,
      role: 'patient'
    },
    patient_info: {
      name: form.name,
      age: parseInt(form.age),
      gender: form.gender,
      medical_history: '',
      allergies: ''
    }
  }
  
  try {
    await registerPatient(payload)
    uni.showToast({ title: '注册成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (e: any) {
    uni.showToast({ title: e.detail || e.message || '注册失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style lang="scss" scoped>
.register-page {
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
  
  .icon-back {
    font-size: 48rpx;
    color: #303133;
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
  padding: 40rpx 50rpx;
}

.header-section {
  margin-bottom: 60rpx;
  
  .main-title {
    font-size: 48rpx;
    font-weight: bold;
    color: #1a1a1a;
    display: block;
  }
  
  .sub-title {
    font-size: 26rpx;
    color: #909399;
    margin-top: 16rpx;
    display: block;
  }
}

.section-group {
  margin-bottom: 40rpx;
  
  .section-label {
    font-size: 24rpx;
    color: #909399;
    margin-bottom: 20rpx;
    display: block;
    padding-left: 10rpx;
  }
}

.input-wrapper {
  background-color: #FFFFFF;
  border-radius: 20rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.02);
  
  .main-input {
    flex: 1;
    font-size: 30rpx;
    color: #303133;
    margin-left: 20rpx;
  }
  
  .eye-icon {
    padding: 10rpx;
    .icon-eye {
      font-size: 32rpx;
      color: #C0C4CC;
    }
  }

  &.code-wrapper {
    .get-code-btn {
      padding: 10rpx 20rpx;
      background-color: #F0F7FF;
      border-radius: 12rpx;
      margin-left: 20rpx;
      
      &.disabled {
        opacity: 0.6;
      }
      
      .code-btn-text {
        font-size: 24rpx;
        color: #1890FF;
        white-space: nowrap;
      }
    }
  }
}

/* CSS Icons - Minimal Line Style */
.icon-line-phone {
  width: 24rpx;
  height: 40rpx;
  border: 3rpx solid #606266;
  border-radius: 5rpx;
  position: relative;
  &::after {
    content: '';
    position: absolute;
    bottom: 5rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 8rpx;
    height: 2rpx;
    background-color: #606266;
  }
}

.icon-line-code {
  width: 32rpx;
  height: 24rpx;
  border: 3rpx solid #606266;
  border-radius: 4rpx;
  position: relative;
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 4rpx;
    width: 24rpx;
    height: 3rpx;
    background-color: #606266;
    box-shadow: 0 -6rpx #606266, 0 6rpx #606266;
  }
}

.icon-line-lock {
  width: 28rpx;
  height: 24rpx;
  background-color: #606266;
  border-radius: 4rpx;
  position: relative;
  margin-top: 12rpx;
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

.icon-line-user {
  width: 28rpx;
  height: 28rpx;
  border: 3rpx solid #606266;
  border-radius: 50%;
  position: relative;
  &::after {
    content: '';
    position: absolute;
    bottom: -16rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 36rpx;
    height: 14rpx;
    border: 3rpx solid #606266;
    border-bottom: none;
    border-radius: 18rpx 18rpx 0 0;
  }
}

.icon-line-age {
  width: 32rpx;
  height: 32rpx;
  border: 3rpx solid #606266;
  border-radius: 50%;
  position: relative;
  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 14rpx;
    height: 14rpx;
    border: 3rpx solid #606266;
    border-top: none;
    border-left: none;
    transform: translate(-50%, -70%) rotate(45deg);
  }
}

.icon-line-male {
  width: 24rpx;
  height: 24rpx;
  border: 3rpx solid #606266;
  border-radius: 50%;
  position: relative;
  margin-right: 12rpx;
  &.active { border-color: #1890FF; &::after { background-color: #1890FF; border-color: #1890FF; } }
  &::after {
    content: '';
    position: absolute;
    top: -10rpx;
    right: -10rpx;
    width: 12rpx;
    height: 12rpx;
    border: 3rpx solid #606266;
    border-bottom: none;
    border-left: none;
  }
}

.icon-line-female {
  width: 24rpx;
  height: 24rpx;
  border: 3rpx solid #606266;
  border-radius: 50%;
  position: relative;
  margin-right: 12rpx;
  &.active { border-color: #FF4D4F; &::after { background-color: #FF4D4F; } }
  &::after {
    content: '';
    position: absolute;
    bottom: -12rpx;
    left: 50%;
    transform: translateX(-50%);
    width: 3rpx;
    height: 12rpx;
    background-color: #606266;
    box-shadow: 0 -4rpx #606266;
    &.active { background-color: #FF4D4F; box-shadow: 0 -4rpx #FF4D4F; }
  }
}

.gender-selector {
  display: flex;
  gap: 30rpx;
  margin-top: 20rpx;
  
  .gender-item {
    flex: 1;
    height: 90rpx;
    background-color: #FFFFFF;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2rpx solid transparent;
    transition: all 0.2s;
    
    .gender-text {
      font-size: 28rpx;
      color: #606266;
    }
    
    &.active {
      background-color: #F0F7FF;
      border-color: #6EBFF7;
      .gender-text {
        color: #1890FF;
        font-weight: 500;
      }
      &:nth-child(2) {
        background-color: #FFF1F0;
        border-color: #FFCCC7;
        .gender-text { color: #FF4D4F; }
      }
    }
  }
}

.register-btn {
  background-color: #6EBFF7;
  height: 100rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 80rpx;
  box-shadow: 0 8rpx 20rpx rgba(110, 191, 247, 0.3);
  
  &.btn-disabled {
    opacity: 0.6;
    background-color: #6EBFF7;
    box-shadow: none;
  }
  
  .btn-text {
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
  }
}

.login-link {
  margin-top: 40rpx;
  text-align: center;
  
  .link-text {
    font-size: 26rpx;
    color: #6EBFF7;
  }
}
</style>
