<template>
  <view class="page-container">
    <view class="upload-card">
      <view class="upload-header">
        <view class="upload-icon-wrapper">
          <text class="upload-icon">↑</text>
        </view>
        <text class="upload-title">上传病历报告</text>
        <text class="upload-subtitle">支持图片格式，系统将自动识别病历信息</text>
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
        <text v-if="totalFiles > 1" class="uploading-hint">{{ uploadHint }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { uploadMedicalRecord } from '@/api/medical-record'
import { useMemberStore } from '@/stores/member'

const memberStore = useMemberStore()

const uploading = ref(false)
const uploadStatus = ref('正在上传...')
const uploadHint = ref('')
const totalFiles = ref(0)

const chooseFromCamera = () => {
  uni.chooseImage({
    count: 9,
    sourceType: ['camera'],
    success: (res) => {
      handleUploadFiles(res.tempFilePaths)
    }
  })
}

const chooseFromAlbum = () => {
  uni.chooseImage({
    count: 9,
    sourceType: ['album'],
    success: (res) => {
      handleUploadFiles(res.tempFilePaths)
    }
  })
}

const handleUploadFiles = async (filePaths: string[]) => {
  if (!filePaths || filePaths.length === 0) {
    uni.showToast({ title: '请选择图片', icon: 'none' })
    return
  }

  uploading.value = true
  totalFiles.value = filePaths.length
  uploadStatus.value = '正在上传并识别病历…'
  uploadHint.value = `共 ${filePaths.length} 张`

  const memberId = memberStore.currentMember?.id || ''
  let successCount = 0
  let failCount = 0

  try {
    for (let i = 0; i < filePaths.length; i++) {
      uploadHint.value = `正在处理第 ${i + 1}/${filePaths.length} 张`
      
      try {
        const res: any = await uploadMedicalRecord(filePaths[i], memberId)
        
        if (res && res.success) {
          successCount++
        } else {
          failCount++
        }
      } catch (err: any) {
        failCount++
        console.error('Upload error:', err)
      }
    }

    uploading.value = false

    if (successCount > 0 && failCount === 0) {
      uni.showToast({ 
        title: `成功上传 ${successCount} 份病历`, 
        icon: 'success' 
      })
    } else if (successCount > 0 && failCount > 0) {
      uni.showToast({ 
        title: `成功 ${successCount} 份，失败 ${failCount} 份`, 
        icon: 'none',
        duration: 2000
      })
    } else {
      uni.showToast({ 
        title: '上传失败，请重试', 
        icon: 'none' 
      })
    }

    setTimeout(() => {
      uni.reLaunch({ url: '/pages/medical-record/list' })
    }, 1500)

  } catch (err: any) {
    uploading.value = false
    console.error('Upload files error:', err)
    uni.showToast({ 
      title: err.message || '上传失败', 
      icon: 'none' 
    })
  }
}
</script>

<style>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
}

.upload-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 24px;
  padding: 40px 32px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.upload-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40px;
}

.upload-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.upload-icon {
  font-size: 36px;
  color: #ffffff;
  font-weight: 700;
}

.upload-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}

.upload-subtitle {
  font-size: 14px;
  color: #64748b;
  text-align: center;
}

.upload-actions {
  display: flex;
  gap: 16px;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 16px;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.action-btn.camera {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.action-btn.album {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.action-btn:active {
  transform: scale(0.96);
}

.action-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.action-text {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
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
  font-weight: 600;
}

.uploading-hint {
  font-size: 14px;
  color: #64748b;
}
</style>
