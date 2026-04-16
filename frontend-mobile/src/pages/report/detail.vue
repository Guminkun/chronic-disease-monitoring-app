<template>
  <view class="page-container">
    <scroll-view scroll-y class="page-scroll" :scroll-top="scrollTop">
      <view class="image-section" v-if="report.image_url" @click="previewImage">
        <image 
          :src="report.image_url" 
          mode="aspectFill" 
          class="report-image"
        />
        <view class="image-overlay">
          <view class="image-hint">
            <text class="hint-icon">🔍</text>
            <text class="hint-text">点击查看大图</text>
          </view>
        </view>
      </view>

      <view class="image-placeholder" v-else>
        <text class="placeholder-icon">📄</text>
        <text class="placeholder-text">暂无报告图片</text>
      </view>

      <view class="tabs-wrap">
        <view class="tabs-header">
          <view 
            class="tab-item" 
            :class="{ active: activeTab === 'results' }" 
            @click="switchTab('results')"
          >
            <text class="tab-text">检查结果</text>
          </view>
          <view 
            class="tab-item" 
            :class="{ active: activeTab === 'info' }" 
            @click="switchTab('info')"
          >
            <text class="tab-text">基础信息</text>
          </view>
        </view>

        <view class="tab-content" v-show="activeTab === 'results'">
          <view v-if="isImagingReport">
            <view class="imaging-section">
              <view class="imaging-card">
                <view class="imaging-header">
                  <text class="imaging-title">检查所见</text>
                </view>
                <view class="imaging-content">
                  <text class="imaging-text">{{ imagingFindings }}</text>
                </view>
              </view>
              
              <view class="imaging-card">
                <view class="imaging-header">
                  <text class="imaging-title">诊断结果</text>
                </view>
                <view class="imaging-content diagnosis-content">
                  <text class="diagnosis-text">{{ imagingDiagnosis }}</text>
                </view>
              </view>
            </view>
          </view>
          <view v-else>
            <view class="results-card" v-if="hasMetrics">
              <scroll-view scroll-x class="table-scroll" :show-scrollbar="false">
                <view class="table-wrapper">
                  <view class="table-header">
                    <view class="th th-project">项目</view>
                    <view class="th">结果</view>
                    <view class="th">参考区间</view>
                    <view class="th">单位</view>
                    <view class="th">状态</view>
                    <view class="th">缩写</view>
                  </view>
                  <view 
                    class="table-row" 
                    v-for="(item, idx) in displayMetrics" 
                    :key="idx"
                    :class="{ 'row-abnormal': isAbnormal(item) }"
                  >
                    <view class="td td-project">{{ item.name || '-' }}</view>
                    <view class="td">
                      <text class="value-text" :class="{ 'text-abnormal': isAbnormal(item) }">
                        {{ item.value || '-' }}
                      </text>
                      <text v-if="isAbnormal(item)" class="abnormal-arrow">{{ item.abnormal_symbol || '↑' }}</text>
                    </view>
                    <view class="td">{{ item.reference_range || '-' }}</view>
                    <view class="td">{{ item.unit || '-' }}</view>
                    <view class="td">
                      <view class="status-tag" :class="getStatusClass(item)">
                        <text>{{ getStatusText(item) }}</text>
                      </view>
                    </view>
                    <view class="td">{{ item.code || '-' }}</view>
                  </view>
                </view>
              </scroll-view>
            </view>
            <view class="empty-card" v-else>
              <text class="empty-icon">📋</text>
              <text class="empty-text">暂无检查结果数据</text>
            </view>
          </view>
        </view>

        <view class="tab-content" v-show="activeTab === 'info'">
          <view class="info-card" v-if="hasBasicInfo">
            <view class="info-item" v-if="basicInfo.gender">
              <text class="info-label">性别</text>
              <text class="info-value">{{ basicInfo.gender }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.age">
              <text class="info-label">年龄</text>
              <text class="info-value">{{ basicInfo.age }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.project_package">
              <text class="info-label">项目套餐</text>
              <text class="info-value">{{ basicInfo.project_package }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.department">
              <text class="info-label">病区/科室</text>
              <text class="info-value">{{ basicInfo.department }}</text>
            </view>
            <view class="info-item" v-if="report.hospital_name">
              <text class="info-label">医疗机构</text>
              <text class="info-value">{{ report.hospital_name }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.sample_time">
              <text class="info-label">采样时间</text>
              <text class="info-value">{{ formatDateTime(basicInfo.sample_time) }}</text>
            </view>
            <view class="info-item" v-if="report.report_date">
              <text class="info-label">报告时间</text>
              <text class="info-value">{{ formatDate(report.report_date) }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.sample_type">
              <text class="info-label">样本种类</text>
              <text class="info-value">{{ basicInfo.sample_type }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.receive_time">
              <text class="info-label">接收时间</text>
              <text class="info-value">{{ formatDateTime(basicInfo.receive_time) }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.request_doctor">
              <text class="info-label">申请医生</text>
              <text class="info-value">{{ basicInfo.request_doctor }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.test_doctor">
              <text class="info-label">检验医生</text>
              <text class="info-value">{{ basicInfo.test_doctor }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.audit_doctor">
              <text class="info-label">审核医生</text>
              <text class="info-value">{{ basicInfo.audit_doctor }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.diagnosis">
              <text class="info-label">诊断</text>
              <text class="info-value">{{ basicInfo.diagnosis }}</text>
            </view>
            <view class="info-item" v-if="basicInfo.medical_record_no">
              <text class="info-label">病历号</text>
              <text class="info-value">{{ basicInfo.medical_record_no }}</text>
            </view>
          </view>
          <view class="empty-card" v-else>
            <text class="empty-icon">📋</text>
            <text class="empty-text">暂无基础信息</text>
          </view>
        </view>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <view class="loading-overlay" v-if="loading">
      <view class="loading-content">
        <view class="loading-spinner"></view>
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getReportDetail } from '@/api/report'

const report = ref<any>({})

const loading = ref(false)
const activeTab = ref<'results' | 'info'>('results')
const scrollTop = ref(0)

const displayMetrics = computed(() => {
  return report.value?.metrics || []
})

const hasMetrics = computed(() => {
  return displayMetrics.value.length > 0
})

const isImagingReport = computed(() => {
  const reportType = String(report.value?.report_type || '').toLowerCase()
  const category = report.value?.data?.category || ''
  
  if (reportType.includes('病历报告')) {
    return false
  }
  
  return reportType.includes('影像') || category === 'imaging'
})

const imagingFindings = computed(() => {
  if (!isImagingReport.value) return ''
  
  const findings = report.value?.data?.findings
  if (findings && findings.trim()) {
    return findings.trim()
  }
  
  return '暂无检查所见数据'
})

const imagingDiagnosis = computed(() => {
  if (!isImagingReport.value) return ''
  
  const diagnosis = report.value?.data?.diagnosis
  if (diagnosis && diagnosis.trim() && diagnosis !== '暂无') {
    return diagnosis.trim()
  }
  
  const diagnosisField = report.value?.data?.diagnosis
  if (diagnosisField && diagnosisField.trim()) {
    return diagnosisField.trim()
  }
  
  return '暂无诊断结果'
})

const basicInfo = computed(() => {
  const data = report.value?.data || {}
  return {
    gender: data.gender || data.patient_gender || null,
    age: data.age || data.patient_age || null,
    project_package: data.project_package || data.package_name || null,
    department: data.department || data.ward || data.patient_department || null,
    sample_time: data.sample_time || data.collection_time || null,
    sample_type: data.sample_type || data.specimen_type || null,
    receive_time: data.receive_time || data.received_time || null,
    request_doctor: data.request_doctor || data.applying_doctor || null,
    test_doctor: data.test_doctor || data.laboratory_doctor || null,
    audit_doctor: data.audit_doctor || data.review_doctor || null,
    diagnosis: data.diagnosis || data.clinical_diagnosis || null,
    medical_record_no: data.medical_record_no || data.patient_id || data.case_number || null
  }
})

const hasBasicInfo = computed(() => {
  const info = basicInfo.value
  return Object.values(info).some(v => v !== null && v !== undefined && v !== '')
})

const isAbnormal = (item: any) => {
  if (!item) return false
  if (item.abnormal_symbol === '↑' || item.abnormal_symbol === '↓') return true
  if (item.is_abnormal) return true
  return false
}

const getStatusClass = (item: any) => {
  if (isAbnormal(item)) return 'tag-abnormal'
  return 'tag-normal'
}

const getStatusText = (item: any) => {
  if (isAbnormal(item)) return '异常'
  return '正常'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

const fetchDetail = async (id: string) => {
  loading.value = true
  try {
    const res: any = await getReportDetail(id)
    report.value = res || {}
  } catch (e) {
    console.error('Fetch report detail error:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const switchTab = (tab: 'results' | 'info') => {
  activeTab.value = tab
}

const previewImage = () => {
  if (report.value?.image_url) {
    uni.previewImage({
      urls: [report.value.image_url]
    })
  }
}

onLoad((options) => {
  if (options?.id) {
    // 延迟加载数据，确保页面已渲染
    setTimeout(() => {
      fetchDetail(options.id)
    }, 100)
  } else {
    uni.showToast({ title: '参数错误', icon: 'none' })
    setTimeout(() => {
      uni.navigateBack({
        fail: () => {
          uni.switchTab({ url: '/pages/index/index' })
        }
      })
    }, 1500)
  }
})
</script>

<style>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}






.page-scroll {
  flex: 1;
}

.image-section {
  background: #ffffff;
  margin: 12px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
}

.report-image {
  width: 100%;
  height: 25vh;
  display: block;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent);
  padding: 16px 0 8px;
}

.image-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.hint-icon {
  font-size: 16px;
}

.hint-text {
  font-size: 13px;
  color: #ffffff;
  font-weight: 500;
}

.image-placeholder {
  background: #ffffff;
  margin: 12px;
  border-radius: 16px;
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}

.placeholder-text {
  font-size: 14px;
  color: #94a3b8;
}

.tabs-wrap {
  background: #ffffff;
  margin: 0 12px 12px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
}

.tab-item {
  flex: 1;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 48px;
  height: 3px;
  background: #3b82f6;
  border-radius: 2px;
}

.tab-text {
  font-size: 15px;
  font-weight: 600;
  color: #94a3b8;
}

.tab-item.active .tab-text {
  color: #3b82f6;
}

.tab-content {
  padding: 12px;
}

.results-card {
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

.table-scroll {
  width: 100%;
  white-space: nowrap;
}

.table-wrapper {
  display: inline-block;
  min-width: 100%;
}

.table-header {
  display: flex;
  background: #e2e8f0;
}

.th {
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  flex-shrink: 0;
  min-width: 80px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.th-project {
  min-width: 90px;
  max-width: 90px;
  position: sticky;
  left: 0;
  background: #e2e8f0;
  z-index: 10;
  text-align: center;
  border-right: 1px solid #cbd5e1;
  padding-right: 12px;
}

.table-row {
  display: flex;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row.row-abnormal {
  background: #fef2f2;
}

.td {
  padding: 14px 16px;
  font-size: 14px;
  color: #334155;
  flex-shrink: 0;
  min-width: 80px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  white-space: nowrap;
}

.td-project {
  min-width: 90px;
  max-width: 90px;
  position: sticky;
  left: 0;
  background: inherit;
  z-index: 10;
  text-align: center;
  justify-content: center;
  white-space: normal;
  word-wrap: break-word;
  word-break: break-all;
  line-height: 1.4;
  border-right: 1px solid #e2e8f0;
  padding-right: 12px;
  flex-shrink: 0;
}

.value-text {
  font-weight: 600;
}

.text-abnormal {
  color: #ef4444;
}

.abnormal-arrow {
  color: #ef4444;
  font-weight: 800;
  font-size: 16px;
  flex-shrink: 0;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  min-width: 48px;
}

.tag-normal {
  background: #dcfce7;
  color: #16a34a;
}

.tag-abnormal {
  background: #fee2e2;
  color: #dc2626;
}

.info-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 4px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #64748b;
  flex-shrink: 0;
  width: 80px;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
  text-align: right;
  flex: 1;
  margin-left: 12px;
  word-break: break-all;
}

.empty-card {
  padding: 48px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.empty-icon {
  font-size: 40px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  color: #94a3b8;
}

.bottom-space {
  height: 24px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
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
}

.imaging-section {
  padding: 0;
}

.imaging-card {
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
}

.imaging-card:last-child {
  margin-bottom: 0;
}

.imaging-header {
  height: 44px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  border-bottom: 1px solid #e2e8f0;
}

.imaging-title {
  font-size: 15px;
  font-weight: 700;
  color: #4f46e5;
}

.imaging-content {
  padding: 16px;
  min-height: 80px;
}

.imaging-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.diagnosis-content {
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
}

.diagnosis-text {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.6;
}


</style>
