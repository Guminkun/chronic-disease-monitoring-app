<template>
  <view class="page-container">
    <scroll-view scroll-y class="report-scroll" :show-scrollbar="false">
      <view class="folders-container">
        <view class="folder-card">
          <view class="folder-header" @click="toggleFolder">
            <view class="folder-icon-wrapper medical">
              <text class="folder-icon">📋</text>
            </view>
            <view class="folder-info">
              <text class="folder-name">病历报告</text>
              <text class="folder-count">{{ totalCount }} 份</text>
            </view>
            <view class="folder-action">
              <text class="folder-arrow" :class="{ rotated: folderExpanded }">›</text>
            </view>
          </view>

          <view v-show="folderExpanded" class="folder-content">
            <view class="report-grid">
              <view 
                v-for="record in records" 
                :key="record.id"
                class="report-item"
                @click="openDetail(record)"
                @longpress="openItemMenu(record)"
              >
                <view class="report-thumb">
                  <image 
                    v-if="record.image_url" 
                    :src="record.image_url" 
                    mode="aspectFill" 
                    class="thumb-image"
                  />
                  <view v-else class="thumb-placeholder">
                    <text class="placeholder-icon">📄</text>
                  </view>
                </view>
                <view class="report-meta">
                  <text class="report-title">{{ record.title || '病历报告' }}</text>
                  <text class="report-date">{{ formatDate(record.report_date || record.created_at) }}</text>
                </view>
              </view>
            </view>

            <view v-if="records.length === 0" class="empty-folder">
              <text class="empty-folder-text">暂无病历报告</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="error" class="error-state" @click="fetchRecords">
        <text class="error-icon">⚠️</text>
        <text class="error-text">加载失败，点击重试</text>
      </view>

      <view v-else-if="totalCount === 0" class="empty-state">
        <view class="empty-illustration">
          <text class="empty-icon">📋</text>
        </view>
        <text class="empty-title">还没有病历报告</text>
        <text class="empty-desc">点击右上角按钮上传您的第一份病历</text>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <view v-if="showOptions" class="modal-overlay" @click="hideUploadOptions">
      <view class="modal-sheet" @click.stop>
        <view class="modal-handle"></view>
        <view class="modal-header">
          <text class="modal-title">上传病历报告</text>
        </view>
        <view class="modal-body">
          <view class="upload-option" @click="chooseFromCamera">
            <view class="option-icon-wrapper camera">
              <text class="option-icon">📷</text>
            </view>
            <view class="option-info">
              <text class="option-label">拍照上传</text>
              <text class="option-desc">使用相机拍摄病历</text>
            </view>
          </view>
          <view class="upload-option" @click="chooseFromAlbum">
            <view class="option-icon-wrapper album">
              <text class="option-icon">🖼️</text>
            </view>
            <view class="option-info">
              <text class="option-label">从相册选择</text>
              <text class="option-desc">选择已有的病历图片</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部悬浮添加按钮 -->
    <view class="floating-add-btn" @click="showUploadOptions">
      <text class="add-text">添加病历</text>
    </view>

    <view v-if="uploading" class="uploading-overlay">
      <view class="uploading-card">
        <view class="uploading-spinner"></view>
        <text class="uploading-title">{{ uploadProgress }}</text>
        <text class="uploading-hint">{{ uploadHint }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getMedicalRecords, deleteMedicalRecord, uploadMedicalRecord } from '@/api/medical-record'
import { useMemberStore } from '@/stores/member'
import { onShow } from '@dcloudio/uni-app'
import { safeNavigate } from '@/utils/navigate'

const memberStore = useMemberStore()

const records = ref<any[]>([])
const loading = ref(false)
const error = ref(false)
const showOptions = ref(false)
const uploading = ref(false)
const uploadProgress = ref('')
const uploadHint = ref('')
const folderExpanded = ref(true)

const totalCount = computed(() => records.value.length)

const formatDate = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const fetchRecords = async () => {
  loading.value = true
  error.value = false
  try {
    const memberId = memberStore.currentMember?.id
    const res: any = await getMedicalRecords(memberId)
    records.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (err) {
    console.error('Fetch medical records error:', err)
    error.value = true
  } finally {
    loading.value = false
  }
}

const showUploadOptions = () => {
  showOptions.value = true
}

const hideUploadOptions = () => {
  showOptions.value = false
}

const chooseFromCamera = () => {
  hideUploadOptions()
  uni.chooseImage({
    count: 9,
    sourceType: ['camera'],
    success: (res) => {
      handleUploadFiles(res.tempFilePaths)
    }
  })
}

const chooseFromAlbum = () => {
  hideUploadOptions()
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
  uploadProgress.value = '正在上传并识别病历…'
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
      uni.showToast({ title: `成功上传 ${successCount} 份病历`, icon: 'success' })
    } else if (successCount > 0 && failCount > 0) {
      uni.showToast({ title: `成功 ${successCount} 份，失败 ${failCount} 份`, icon: 'none' })
    } else {
      uni.showToast({ title: '上传失败，请重试', icon: 'none' })
    }

    setTimeout(() => {
      fetchRecords()
    }, 500)

  } catch (err) {
    uploading.value = false
    uni.showToast({ title: '上传失败，请重试', icon: 'none' })
  }
}

const toggleFolder = () => {
  folderExpanded.value = !folderExpanded.value
}

const openDetail = (record: any) => {
  if (!record?.id) return
  uni.navigateTo({
    url: `/pages/medical-record/detail?id=${record.id}`
  })
}

const deleteOne = (record: any) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后不可恢复，是否继续？',
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '删除中...' })
        try {
          await deleteMedicalRecord(record.id)
          records.value = records.value.filter(r => r.id !== record.id)
          uni.showToast({ title: '删除成功', icon: 'success' })
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        } finally {
          uni.hideLoading()
        }
      }
    }
  })
}

const openItemMenu = (record: any) => {
  uni.showActionSheet({
    itemList: ['删除'],
    success: (res) => {
      if (res.tapIndex === 0) deleteOne(record)
    }
  })
}

onShow(() => {
  fetchRecords()
})
</script>

<style>
.page-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  padding-bottom: 80px;
}

/* 底部悬浮添加按钮 */
.floating-add-btn {
  position: fixed;
  left: 50%;
  bottom: 32px;
  transform: translateX(-50%);
  min-width: 120px;
  height: 48px;
  padding: 0 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  z-index: 100;
  transition: all 0.3s ease;
}

.floating-add-btn:active {
  transform: translateX(-50%) scale(0.95);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

.floating-add-btn .add-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
  letter-spacing: 1px;
}

.report-scroll {
  flex: 1;
  padding: 16px;
  box-sizing: border-box;
}

.folders-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 8px;
}

.folder-card {
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.folder-header {
  height: 80px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: #ffffff;
}

.folder-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.folder-icon-wrapper.medical {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.folder-icon {
  font-size: 28px;
  line-height: 1;
}

.folder-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.folder-name {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: 0.2px;
}

.folder-count {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.folder-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.folder-arrow {
  font-size: 20px;
  color: #94a3b8;
  transform: rotate(90deg);
  transition: transform 0.3s ease;
}

.folder-arrow.rotated {
  transform: rotate(270deg);
}

.folder-content {
  padding: 0 16px 16px;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.report-item {
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.report-thumb {
  width: 100%;
  aspect-ratio: 1;
  position: relative;
  background: #f1f5f9;
}

.thumb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
}

.placeholder-icon {
  font-size: 28px;
  opacity: 0.6;
}

.report-meta {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.report-title {
  font-size: 11px;
  color: #1e293b;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.report-date {
  font-size: 10px;
  color: #94a3b8;
}

.empty-folder {
  padding: 32px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-folder-text {
  font-size: 14px;
  color: #94a3b8;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 12px;
}

.loading-spinner,
.uploading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.error-icon,
.empty-icon {
  font-size: 48px;
  opacity: 0.8;
}

.error-text,
.empty-title {
  font-size: 15px;
  color: #475569;
  font-weight: 600;
}

.empty-desc {
  font-size: 13px;
  color: #94a3b8;
}

.bottom-space {
  height: 32px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.modal-sheet {
  width: 100%;
  background: #ffffff;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  padding-bottom: 34px;
}

.modal-handle {
  width: 36px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin: 12px auto 20px;
}

.modal-header {
  padding: 0 24px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  font-size: 18px;
  color: #0f172a;
  font-weight: 700;
}

.modal-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-option {
  height: 72px;
  padding: 0 16px;
  background: #f8fafc;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-option:active {
  background: #f1f5f9;
}

.option-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.option-icon-wrapper.camera {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.option-icon-wrapper.album {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
}

.option-icon {
  font-size: 24px;
  line-height: 1;
}

.option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-label {
  font-size: 16px;
  color: #0f172a;
  font-weight: 600;
}

.option-desc {
  font-size: 13px;
  color: #64748b;
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

.uploading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
}

.uploading-title {
  font-size: 17px;
  color: #0f172a;
  font-weight: 600;
}

.uploading-hint {
  font-size: 14px;
  color: #64748b;
}
</style>
