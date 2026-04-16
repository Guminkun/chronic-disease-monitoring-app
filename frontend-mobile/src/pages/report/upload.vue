<template>
  <view class="page-container">
    <view class="upload-card">
      <view class="upload-header">
        <view class="upload-icon-wrapper">
          <text class="upload-icon">↑</text>
        </view>
        <text class="upload-title">上传检查报告</text>
        <text class="upload-subtitle">支持图片格式，系统将自动识别报告类型</text>
      </view>

      <view class="upload-actions">
        <view class="action-btn camera" @click="chooseFromCamera">
          <text class="action-icon">📷</text>
          <text class="action-text">拍照上传</text>
        </view>
        <view class="action-btn album" @click="chooseFromAlbum">
          <text class="action-icon">🖼️</text>
          <text class="action-text">从相册选择</text>
        </view>
      </view>
    </view>

    <view v-if="uploading" class="uploading-overlay">
      <view class="uploading-content">
        <view class="loading-spinner"></view>
        <text class="uploading-text">{{ uploadStatus }}</text>
      </view>
    </view>

    <view v-if="showManualSelect" class="manual-select-overlay" @click="closeManualSelect">
      <view class="manual-select-card" @click.stop>
        <view class="manual-header">
          <text class="manual-title">选择报告类型</text>
          <text class="manual-close" @click="closeManualSelect">×</text>
        </view>
        <text class="manual-hint">自动识别失败，请手动选择报告类型</text>
        <view class="manual-actions">
          <view class="manual-btn lab" @click="confirmManualSelect('lab')">
            <text class="manual-icon">🧪</text>
            <text class="manual-label">化验单</text>
          </view>
          <view class="manual-btn imaging" @click="confirmManualSelect('imaging')">
            <text class="manual-icon">📷</text>
            <text class="manual-label">影像报告</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { autoClassifyReport } from '@/api/report'

const uploading = ref(false)
const uploadStatus = ref('正在上传...')
const showManualSelect = ref(false)
const tempFilePath = ref('')
const pendingReportData = ref<any>(null)

const chooseFromCamera = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['camera'],
    success: (res) => {
      tempFilePath.value = res.tempFilePaths[0]
      uploadFile(res.tempFilePaths[0])
    }
  })
}

const chooseFromAlbum = () => {
  uni.chooseImage({
    count: 1,
    sourceType: ['album'],
    success: (res) => {
      tempFilePath.value = res.tempFilePaths[0]
      uploadFile(res.tempFilePaths[0])
    }
  })
}

const uploadFile = async (filePath: string) => {
  uploading.value = true
  uploadStatus.value = '正在上传...'

  try {
    uploadStatus.value = '正在解析...'
    const res: any = await autoClassifyReport(filePath)
    
    uploading.value = false
    
    if (res && res.success) {
      uni.showToast({ title: '上传成功', icon: 'success' })
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/report/report' })
      }, 1200)
    } else if (res && res.need_manual) {
      pendingReportData.value = res
      showManualSelect.value = true
    } else {
      throw new Error('上传失败')
    }
  } catch (err: any) {
    uploading.value = false
    const msg = err?.message?.includes('超时') 
      ? 'OCR服务超时，请稍后重试' 
      : (err?.message || '上传失败')
    uni.showToast({ title: msg, icon: 'none' })
  }
}

const confirmManualSelect = async (type: 'lab' | 'imaging') => {
  showManualSelect.value = false
  uploading.value = true
  uploadStatus.value = '正在保存...'

  try {
    const res: any = await autoClassifyReport(tempFilePath.value, { manual_type: type })
    uploading.value = false
    
    if (res && res.success) {
      uni.showToast({ title: '上传成功', icon: 'success' })
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/report/report' })
      }, 1200)
    } else {
      throw new Error('保存失败')
    }
  } catch (err: any) {
    uploading.value = false
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

const closeManualSelect = () => {
  showManualSelect.value = false
  tempFilePath.value = ''
  pendingReportData.value = null
}
</script>

<style>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.upload-card {
  width: 100%;
  background-color: #ffffff;
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.upload-header {
  text-align: center;
  margin-bottom: 32px;
}

.upload-icon-wrapper {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.upload-icon {
  font-size: 36px;
  color: #ffffff;
  font-weight: bold;
}

.upload-title {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.upload-subtitle {
  display: block;
  font-size: 14px;
  color: #64748b;
}

.upload-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-btn {
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 17px;
  font-weight: 600;
}

.action-btn.camera {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
}

.action-btn.album {
  background: #ffffff;
  border: 2px solid #e2e8f0;
  color: #1e293b;
}

.action-icon {
  font-size: 24px;
  line-height: 1;
}

.action-text {
  font-size: 17px;
  font-weight: 600;
}

.uploading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.uploading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.uploading-text {
  font-size: 16px;
  color: #1e293b;
  font-weight: 500;
}

.manual-select-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 20px;
}

.manual-select-card {
  width: 100%;
  background: #ffffff;
  border-radius: 20px;
  padding: 24px;
}

.manual-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.manual-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.manual-close {
  font-size: 28px;
  color: #94a3b8;
  padding: 4px;
}

.manual-hint {
  display: block;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 20px;
  text-align: center;
}

.manual-actions {
  display: flex;
  gap: 12px;
}

.manual-btn {
  flex: 1;
  height: 100px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.manual-btn.lab {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 2px solid #3b82f6;
}

.manual-btn.imaging {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  border: 2px solid #ec4899;
}

.manual-icon {
  font-size: 32px;
  line-height: 1;
}

.manual-label {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}
</style>
