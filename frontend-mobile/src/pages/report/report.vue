<template>
  <view class="page-container">
    <scroll-view scroll-y class="report-scroll" :show-scrollbar="false">
      <view class="folders-container">
        <view 
          v-for="category in categories" 
          :key="category.key" 
          class="folder-card"
          :class="{ 'folder-expanded': category.expanded }"
        >
          <view class="folder-header" @click="toggleCategory(category.key)">
            <view class="folder-icon-wrapper" :class="category.key">
              <text class="folder-icon">{{ category.icon }}</text>
            </view>
            <view class="folder-info">
              <text class="folder-name">{{ category.label }}</text>
              <text class="folder-count">{{ category.totalCount }} 份</text>
            </view>
            <view class="folder-action">
              <text class="folder-arrow" :class="{ rotated: category.expanded }">›</text>
            </view>
          </view>

          <view v-show="category.expanded" class="folder-content">
            <view 
              v-for="subType in category.subTypes" 
              :key="subType.type" 
              class="subfolder-item"
              @click="toggleSubType(category.key, subType.type)"
            >
              <view class="subfolder-header">
                <view class="subfolder-badge" :class="category.key">
                  <text class="badge-count">{{ subType.reports.length }}</text>
                </view>
                <text class="subfolder-name">{{ subType.name }}</text>
                <text class="subfolder-arrow" :class="{ rotated: subType.expanded }">›</text>
              </view>

              <view v-show="subType.expanded" class="subfolder-reports">
                <view 
                  v-for="report in subType.reports" 
                  :key="report.id"
                  class="report-item"
                  :class="{ 'item-selected': selectedIds.includes(report.id) }"
                  @click="handleItemClick(report)"
                  @longpress="openItemMenu(report)"
                >
                  <view v-if="isSelectMode" class="select-checkbox" @click.stop="toggleSelect(report.id)">
                    <view class="checkbox-inner" :class="{ checked: selectedIds.includes(report.id) }">
                      <text v-if="selectedIds.includes(report.id)" class="check-icon">✓</text>
                    </view>
                  </view>
                  <view class="report-thumb">
                    <image 
                      v-if="report.image_url" 
                      :src="report.image_url" 
                      mode="aspectFill" 
                      class="thumb-image"
                    />
                    <view v-else class="thumb-placeholder">
                      <text class="placeholder-icon">📄</text>
                    </view>
                  </view>
                  <view class="report-meta">
                    <text class="report-date">{{ formatDateOnly(report.report_date || report.created_at) }}</text>
                    <text class="report-type">{{ subType.name }}</text>
                  </view>
                </view>
              </view>
            </view>

            <view v-if="category.subTypes.length === 0" class="empty-folder">
              <text class="empty-folder-text">暂无报告</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="loading" class="loading-state">
        <view class="loading-spinner"></view>
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="error" class="error-state" @click="fetchReports">
        <text class="error-icon">⚠️</text>
        <text class="error-text">加载失败，点击重试</text>
      </view>

      <view v-else-if="totalCount === 0" class="empty-state">
        <view class="empty-illustration">
          <text class="empty-icon">📋</text>
        </view>
        <text class="empty-title">还没有检查报告</text>
        <text class="empty-desc">点击右上角按钮上传您的第一份报告</text>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <view v-if="showOptions" class="modal-overlay" @click="hideUploadOptions">
      <view class="modal-sheet" @click.stop>
        <view class="modal-handle"></view>
        <view class="modal-header">
          <text class="modal-title">上传报告</text>
        </view>
        <view class="modal-body">
          <view class="upload-option" @click="chooseFromCamera">
            <view class="option-icon-wrapper camera">
              <text class="option-icon">📷</text>
            </view>
            <view class="option-info">
              <text class="option-label">拍照上传</text>
              <text class="option-desc">使用相机拍摄报告</text>
            </view>
          </view>
          <view class="upload-option" @click="chooseFromAlbum">
            <view class="option-icon-wrapper album">
              <text class="option-icon">🖼️</text>
            </view>
            <view class="option-info">
              <text class="option-label">从相册选择</text>
              <text class="option-desc">选择已有的报告图片</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 批量操作栏 -->
    <view v-if="isSelectMode" class="batch-action-bar">
      <view class="select-all-btn" @click="toggleSelectAll">
        <view class="checkbox-inner" :class="{ checked: isAllSelected }">
          <text v-if="isAllSelected" class="check-icon">✓</text>
        </view>
        <text class="select-all-text">全选</text>
      </view>
      <view class="batch-actions">
        <view class="action-btn delete-btn" @click="confirmBatchDelete">
          <text class="action-text">删除 ({{ selectedIds.length }})</text>
        </view>
        <view class="action-btn cancel-btn" @click="cancelSelectMode">
          <text class="action-text">取消</text>
        </view>
      </view>
    </view>

    <!-- 底部悬浮添加按钮 -->
    <view v-if="!isSelectMode" class="floating-add-btn" @click="showUploadOptions">
      <text class="add-text">添加报告</text>
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
import { onShow } from '@dcloudio/uni-app'
import { getMyReports, deleteReport as apiDeleteReport, autoClassifyReport, batchDeleteReports } from '@/api/report'
import { useMemberStore } from '@/stores/member'
import { safeNavigate } from '@/utils/navigate'

const memberStore = useMemberStore()

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({
        url: '/pages/index/index'
      })
    }
  })
}

const reports = ref<any[]>([])
const loading = ref(false)
const error = ref(false)
const showOptions = ref(false)
const uploading = ref(false)
const uploadProgress = ref('')
const uploadHint = ref('')
const isSelectMode = ref(false)
const selectedIds = ref<string[]>([])

const expandedCategories = ref<Record<string, boolean>>({
  'lab': false,
  'imaging': false
})

const expandedSubTypes = ref<Record<string, boolean>>({})

const REPORT_TYPE_RULES = [
  { keywords: ['血常规', '白细胞', '红细胞', '血小板', '血红蛋白'], name: '血常规' },
  { keywords: ['尿常规', '尿液', '尿蛋白'], name: '尿常规' },
  { keywords: ['肝功能', '谷丙', '谷草', '转氨酶', '胆红素'], name: '肝功能' },
  { keywords: ['肾功能', '肌酐', '尿素', '尿酸'], name: '肾功能' },
  { keywords: ['血糖', '葡萄糖', '糖化血红蛋白'], name: '血糖检测' },
  { keywords: ['血脂', '胆固醇', '甘油三酯', '低密度', '高密度'], name: '血脂检测' },
  { keywords: ['电解质', '钾', '钠', '氯', '钙'], name: '电解质' },
  { keywords: ['甲状腺', 'TSH', 'T3', 'T4', 'FT3', 'FT4'], name: '甲状腺功能' },
  { keywords: ['凝血', '凝血酶原', 'APTT', 'INR'], name: '凝血功能' },
  { keywords: ['心肌酶', '肌酸激酶', 'CK-MB', '肌红蛋白'], name: '心肌酶谱' },
  { keywords: ['肿瘤标志物', 'AFP', 'CEA', 'CA125', 'CA199', 'PSA'], name: '肿瘤标志物' },
  { keywords: ['乙肝', 'HBsAg', 'HBsAb', 'HBeAg'], name: '乙肝五项' },
  { keywords: ['CT', 'CT检查', '断层'], name: 'CT检查' },
  { keywords: ['MRI', '核磁', '磁共振'], name: 'MRI检查' },
  { keywords: ['X光', 'X线', '胸片', 'X射线'], name: 'X线检查' },
  { keywords: ['超声', 'B超', '彩超', '超声检查'], name: '超声检查' },
  { keywords: ['心电图', 'ECG', '心电'], name: '心电图' },
  { keywords: ['胃镜', '胃镜检查'], name: '胃镜检查' },
  { keywords: ['肠镜', '肠镜检查', '结肠镜'], name: '肠镜检查' },
]

const detectReportType = (report: any): string => {
  const text = [
    report.report_type,
    report.summary,
    JSON.stringify(report.data || {})
  ].join(' ').toLowerCase()

  for (const rule of REPORT_TYPE_RULES) {
    if (rule.keywords.some(kw => text.includes(kw.toLowerCase()))) {
      return rule.name
    }
  }

  return '其他检查'
}

const categorizeReport = (report: any): { category: string, typeName: string } => {
  const typeName = detectReportType(report)
  
  const imagingTypes = ['CT检查', 'MRI检查', 'X线检查', '超声检查', '心电图', '胃镜检查', '肠镜检查']
  
  if (imagingTypes.includes(typeName)) {
    return { category: 'imaging', typeName }
  }
  
  return { category: 'lab', typeName }
}

const categories = computed(() => {
  const categoryMap: Record<string, any> = {
    lab: {
      key: 'lab',
      label: '化验单',
      icon: '🧪',
      expanded: expandedCategories.value.lab,
      subTypes: {},
      totalCount: 0
    },
    imaging: {
      key: 'imaging',
      label: '影像报告',
      icon: '📷',
      expanded: expandedCategories.value.imaging,
      subTypes: {},
      totalCount: 0
    }
  }

  reports.value.forEach(report => {
    const { category, typeName } = categorizeReport(report)
    
    if (!categoryMap[category].subTypes[typeName]) {
      categoryMap[category].subTypes[typeName] = {
        type: typeName,
        name: typeName,
        reports: [],
        expanded: expandedSubTypes.value[`${category}_${typeName}`] ?? false
      }
    }
    
    categoryMap[category].subTypes[typeName].reports.push(report)
    categoryMap[category].totalCount++
  })

  return Object.values(categoryMap)
    .filter((cat: any) => cat.totalCount > 0)
    .map((cat: any) => ({
      ...cat,
      subTypes: Object.values(cat.subTypes).sort((a: any, b: any) => 
        b.reports.length - a.reports.length
      )
    }))
})

const totalCount = computed(() => reports.value.length)

const isAllSelected = computed(() => {
  return reports.value.length > 0 && selectedIds.value.length === reports.value.length
})

const formatDateOnly = (timeStr: string) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const fetchReports = async () => {
  loading.value = true
  error.value = false
  try {
    const memberId = memberStore.currentMember?.id
    const params: any = { type: 'check' }
    if (memberId) {
      params.member_id = memberId
    }
    const res: any = await getMyReports(params)
    reports.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (err) {
    console.error('Fetch reports error:', err)
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
  uploadProgress.value = '正在上传并识别报告类型…'
  uploadHint.value = `共 ${filePaths.length} 张`

  const memberId = memberStore.currentMember?.id || ''
  let successCount = 0
  let failCount = 0

  try {
    for (let i = 0; i < filePaths.length; i++) {
      uploadHint.value = `正在处理第 ${i + 1}/${filePaths.length} 张`
      
      try {
        const formData: any = {}
        if (memberId) {
          formData.member_id = memberId
        }

        const res: any = await autoClassifyReport(filePaths[i], formData)
        
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
      uni.showToast({ title: `成功上传 ${successCount} 张报告`, icon: 'success' })
    } else if (successCount > 0 && failCount > 0) {
      uni.showToast({ title: `成功 ${successCount} 张，失败 ${failCount} 张`, icon: 'none' })
    } else {
      uni.showToast({ title: '上传失败，请重试', icon: 'none' })
    }

    setTimeout(() => {
      fetchReports()
    }, 500)

  } catch (err) {
    uploading.value = false
    uni.showToast({ title: '上传失败，请重试', icon: 'none' })
  }
}

const toggleCategory = (key: string) => {
  expandedCategories.value[key] = !expandedCategories.value[key]
}

const toggleSubType = (categoryKey: string, subTypeKey: string) => {
  const key = `${categoryKey}_${subTypeKey}`
  expandedSubTypes.value[key] = !expandedSubTypes.value[key]
}

const handleItemClick = (report: any) => {
  if (isSelectMode.value) {
    toggleSelect(report.id)
  } else {
    openDetail(report)
  }
}

const toggleSelect = (id: string) => {
  const index = selectedIds.value.indexOf(id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = reports.value.map(r => r.id)
  }
}

const enterSelectMode = () => {
  isSelectMode.value = true
  selectedIds.value = []
}

const cancelSelectMode = () => {
  isSelectMode.value = false
  selectedIds.value = []
}

const confirmBatchDelete = () => {
  if (selectedIds.value.length === 0) {
    uni.showToast({ title: '请选择要删除的报告', icon: 'none' })
    return
  }

  uni.showModal({
    title: '确认删除',
    content: `确定要删除选中的 ${selectedIds.value.length} 份报告吗？删除后不可恢复。`,
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '删除中...' })
        try {
          await batchDeleteReports(selectedIds.value)
          reports.value = reports.value.filter(r => !selectedIds.value.includes(r.id))
          uni.showToast({ title: '删除成功', icon: 'success' })
          cancelSelectMode()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        } finally {
          uni.hideLoading()
        }
      }
    }
  })
}

const openDetail = (report: any) => {
  if (!report?.id) return
  uni.navigateTo({
    url: `/pages/report/detail?id=${report.id}`
  })
}

const deleteOne = (report: any) => {
  uni.showModal({
    title: '确认删除',
    content: '删除后不可恢复，是否继续？',
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '删除中...' })
        try {
          await apiDeleteReport(report.id)
          reports.value = reports.value.filter(r => r.id !== report.id)
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

const openItemMenu = (report: any) => {
  if (isSelectMode.value) return
  
  uni.showActionSheet({
    itemList: ['删除', '批量管理'],
    success: (res) => {
      if (res.tapIndex === 0) deleteOne(report)
      else if (res.tapIndex === 1) enterSelectMode()
    }
  })
}

onShow(() => {
  fetchReports()
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
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08), 0 12rpx 40rpx rgba(0, 0, 0, 0.12), 0 0 0 1rpx rgba(0, 0, 0, 0.06);
  border: 1rpx solid rgba(120, 130, 150, 0.18);
  transition: all 0.3s ease;
  position: relative;
  margin-top: 4px;
}

.folder-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2rpx;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 1), rgba(255, 255, 255, 0.6));
}

.folder-card.folder-expanded {
  box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.10), 0 16rpx 48rpx rgba(0, 0, 0, 0.14), 0 0 0 1rpx rgba(0, 0, 0, 0.08);
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

.folder-icon-wrapper.lab {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.folder-icon-wrapper.imaging {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
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
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.subfolder-item {
  background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
  border-radius: 16px;
  overflow: hidden;
  border: 1rpx solid rgba(148, 163, 184, 0.08);
}

.subfolder-header {
  height: 56px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.subfolder-badge {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.subfolder-badge.lab {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.subfolder-badge.imaging {
  background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
}

.badge-count {
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
}

.subfolder-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
}

.subfolder-arrow {
  font-size: 18px;
  color: #94a3b8;
  transform: rotate(90deg);
  transition: transform 0.3s ease;
}

.subfolder-arrow.rotated {
  transform: rotate(270deg);
}

.subfolder-reports {
  padding: 0 12px 12px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.report-item {
  background: linear-gradient(180deg, #FFFFFF 0%, #FAFBFC 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06), 0 8rpx 24rpx rgba(0, 0, 0, 0.10);
  border: 1rpx solid rgba(120, 130, 150, 0.15);
  position: relative;
}

.report-item.item-selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.select-checkbox {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 10;
}

.checkbox-inner {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-inner.checked {
  border-color: #3b82f6;
  background: #3b82f6;
}

.check-icon {
  color: #ffffff;
  font-size: 12px;
  font-weight: 700;
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

.report-date {
  font-size: 11px;
  color: #1e293b;
  font-weight: 600;
}

.report-type {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 500;
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
  border-top-color: #3b82f6;
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

.batch-action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 64px;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  padding-bottom: 20px;
  z-index: 100;
}

.select-all-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.select-all-text {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn {
  background: #ef4444;
}

.delete-btn .action-text {
  color: #ffffff;
}

.cancel-btn {
  background: #f1f5f9;
}

.cancel-btn .action-text {
  color: #64748b;
}

.action-text {
  font-size: 14px;
  font-weight: 600;
}
</style>
