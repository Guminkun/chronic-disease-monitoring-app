<template>
  <view class="container">
    <view class="header-section">
      <text class="page-title">扫描或输入患者验证码</text>
      <text class="page-subtitle">通过患者的验证码或二维码与患者建立关联</text>
    </view>

    <!-- Tab Switcher -->
    <view class="tab-switcher">
      <view 
        class="tab-btn" 
        :class="{ active: inputMethod === 'manual' }"
        @click="inputMethod = 'manual'"
      >
        <text class="icon">📱</text>
        <text>手动输入</text>
      </view>
      <view 
        class="tab-btn" 
        :class="{ active: inputMethod === 'scan' }"
        @click="inputMethod = 'scan'"
      >
        <text class="icon">📷</text>
        <text>扫描二维码</text>
      </view>
    </view>

    <!-- Manual Input Form -->
    <view v-if="inputMethod === 'manual'" class="form-card">
      <view class="input-group">
        <text class="label">患者验证码</text>
        <input 
          class="input-field" 
          type="text" 
          v-model="authCode" 
          placeholder="输入患者的6位数字验证码" 
          maxlength="6"
        />
        <text class="hint-text">患者可在"我的医生"页面生成验证码</text>
      </view>

      <button class="submit-btn" :disabled="!isManualValid" @click="handleSubmitManual">
        确认添加患者
      </button>
    </view>

    <!-- Scan QR Code -->
    <view v-else class="scan-card">
      <view class="scan-area">
        <view class="scan-placeholder">
          <text class="qr-icon">🏁</text>
          <text class="scan-hint">将患者的二维码放入框内</text>
          <text class="scan-hint-sub">系统将自动识别</text>
        </view>
      </view>

      <button class="scan-btn" @click="handleScan">
        <text class="icon">📷</text> 启动摄像头扫描
      </button>

      <view class="upload-section">
        <view class="divider">
          <text class="divider-text">或</text>
        </view>
        <text class="upload-label">上传二维码图片</text>
        <view class="upload-box" @click="handleUploadImage">
          <text class="upload-text">点击上传或拖拽文件</text>
          <text class="upload-sub">支持 JPG、PNG、BMP 格式</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { bindPatient } from '../../api/doctor'

const inputMethod = ref<'manual' | 'scan'>('manual')
const authCode = ref('')

const isManualValid = computed(() => {
  return authCode.value.length === 6
})

const handleSubmitManual = async () => {
  if (!isManualValid.value) return
  
  uni.showLoading({ title: '正在验证...' })
  
  try {
    await bindPatient(authCode.value)
    
    uni.showToast({
      title: '添加成功',
      icon: 'success'
    })
    
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    uni.showToast({
      title: '绑定失败，请检查验证码',
      icon: 'none'
    })
  } finally {
    uni.hideLoading()
  }
}

const handleScan = () => {
  uni.scanCode({
    success: (res) => {
      console.log('Scan result:', res)
      uni.showToast({
        title: '扫描成功',
        icon: 'success'
      })
      // Process scan result here
    },
    fail: (err) => {
      console.error('Scan failed:', err)
      uni.showToast({
        title: '扫描取消或失败',
        icon: 'none'
      })
    }
  })
}

const handleUploadImage = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['album'],
    success: (res) => {
      console.log('Image selected:', res)
      // In a real app, you might decode QR from image here if supported
      uni.showToast({
        title: '图片已选择',
        icon: 'none'
      })
    }
  })
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 24px 16px;
  box-sizing: border-box;
}

.header-section {
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #0f172a;
  display: block;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

/* Tab Switcher */
.tab-switcher {
  display: flex;
  background-color: #e2e8f0;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #64748b;
  border-radius: 6px;
  gap: 6px;
  transition: all 0.3s;
}

.tab-btn.active {
  background-color: #ffffff;
  color: #0f172a;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Form Card */
.form-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.input-group {
  margin-bottom: 24px;
}

.label {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
  display: block;
}

.input-field {
  height: 48px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0 16px;
  font-size: 15px;
  color: #0f172a;
  background-color: #ffffff;
}

.input-field:focus {
  border-color: #3b82f6;
}

.hint-text {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
  display: block;
}

.submit-btn {
  background-color: #64748b; /* Muted blue/gray as in design */
  color: white;
  border-radius: 8px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 500;
  margin-top: 32px;
}

.submit-btn[disabled] {
  opacity: 0.6;
}

/* Scan Card */
.scan-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scan-area {
  width: 100%;
  aspect-ratio: 1;
  background-color: #f1f5f9;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scan-placeholder {
  text-align: center;
}

.qr-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
  opacity: 0.5;
}

.scan-hint {
  font-size: 14px;
  color: #64748b;
  display: block;
  margin-bottom: 4px;
}

.scan-hint-sub {
  font-size: 12px;
  color: #94a3b8;
}

.scan-btn {
  width: 100%;
  background-color: #0369a1; /* Darker blue as in design */
  color: white;
  border-radius: 8px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  gap: 8px;
}

.upload-section {
  width: 100%;
  margin-top: 24px;
}

.divider {
  position: relative;
  text-align: center;
  margin-bottom: 24px;
}

.divider::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background-color: #e2e8f0;
}

.divider-text {
  position: relative;
  background-color: #ffffff;
  padding: 0 12px;
  font-size: 12px;
  color: #94a3b8;
}

.upload-label {
  font-size: 14px;
  color: #334155;
  margin-bottom: 12px;
  display: block;
}

.upload-box {
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  background-color: #f8fafc;
}

.upload-text {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  display: block;
  margin-bottom: 4px;
}

.upload-sub {
  font-size: 12px;
  color: #94a3b8;
}
</style>
