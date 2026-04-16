<template>
  <view class="page-container">
    <!-- Top Upload Card -->
    <view class="upload-card">
      <view class="upload-header">
        <view class="upload-icon-wrapper">
          <text class="upload-icon">↑</text>
        </view>
        <text class="upload-title">添加病历记录</text>
        <text class="upload-subtitle">上传病历图片，支持JPG、PNG等格式，最大10MB</text>
      </view>

      <view class="form-group">
        <view class="form-row">
          <view class="form-col">
            <text class="label">关联疾病 <text class="required">*</text></text>
            <view class="input-box dropdown" @click="openSearchModal('disease')">
              <text :class="selectedDisease ? 'text-black' : 'text-gray'">
                {{ selectedDisease ? selectedDisease.name : '选择关联疾病' }}
              </text>
              <text class="arrow">▼</text>
            </view>
          </view>
        </view>

        <view class="form-row">
          <view class="form-col">
            <text class="label">就诊医院</text>
            <view class="input-box dropdown" @click="openSearchModal('hospital')">
              <text :class="selectedHospital ? 'text-black' : 'text-gray'">
                {{ selectedHospital ? selectedHospital.name : '选择医院' }}
              </text>
              <text class="arrow">▼</text>
            </view>
          </view>
        </view>

        <view class="form-row">
          <view class="form-col">
            <text class="label">就诊日期</text>
            <picker mode="date" :value="visitDate" @change="onDateChange">
              <view class="input-box dropdown">
                <text :class="visitDate ? 'text-black' : 'text-gray'">
                  {{ visitDate || '选择日期' }}
                </text>
                <text class="arrow">▼</text>
              </view>
            </picker>
          </view>
        </view>
        
        <view class="form-row full-width">
          <view class="form-col">
            <text class="label">选择文件</text>
            <view class="input-box file-input" @click="chooseFile">
              <text :class="fileName ? 'text-black' : 'text-gray'">{{ fileName || '选择文件 未选择文件' }}</text>
              <text v-if="fileName" class="clear-btn" @click.stop="clearFile">×</text>
            </view>
          </view>
        </view>

        <button class="upload-btn" @click="submitReport">
          <text class="upload-btn-icon">↑</text> 上传病历
        </button>
      </view>
    </view>

    <!-- Parsed Result Preview -->
    <view v-if="parsedResult" class="parsed-result-container">
      <view class="result-header">
        <text class="result-title">解析结果确认</text>
        <text class="result-subtitle">请确认以下信息无误后提交</text>
      </view>

      <view class="report-card preview-card">
        <view class="card-header">
          <view class="header-left">
            <view class="file-icon">
              <text>📋</text>
            </view>
            <view class="header-info">
              <text class="report-name">{{ selectedDisease?.name || '病历记录' }}</text>
              <text class="report-meta">📅 {{ parsedResult.report_date }} · 🏥 {{ parsedResult.hospital_name || '未知医院' }}</text>
            </view>
          </view>
          <view class="status-badge status-normal">
            病历
          </view>
        </view>

        <view class="metrics-container" v-if="parsedResult.metrics && parsedResult.metrics.length > 0">
          <view class="metrics-header">
            <text class="mh name">指标名称</text>
            <text class="mh value">数值</text>
            <text class="mh unit">单位</text>
            <text class="mh range">参考范围</text>
            <text class="mh action"></text>
          </view>
          <view v-for="(metric, mIndex) in parsedResult.metrics" :key="mIndex" class="metric-row">
            <input class="mi name" v-model="metric.name" placeholder="名称" />
            <input class="mi value" v-model="metric.value" placeholder="数值" />
            <input class="mi unit" v-model="metric.unit" placeholder="单位" />
            <input class="mi range" v-model="metric.reference_range" placeholder="参考范围" />
            <button class="row-del" @click="removeMetricRow(Number(mIndex))">删除</button>
          </view>
          <view class="metrics-actions">
            <button class="row-add" @click="addMetricRow">新增一行</button>
          </view>
        </view>

        <view class="summary-box" v-if="parsedResult.summary">
          <text class="summary-label">病历摘要：</text>
          <view class="summary-content" v-html="formattedSummary"></view>
        </view>

        <view v-if="parsedResult.image_url" class="imaging-image-wrap">
          <text class="summary-label">病历图片：</text>
          <image class="imaging-image" :src="parsedResult.image_url" mode="widthFix" @click="previewImage(parsedResult.image_url)" />
        </view>
      </view>

      <view class="action-footer">
        <button class="confirm-btn" @click="confirmSubmit">确认提交</button>
        <button class="cancel-btn" @click="cancelParse">重新上传</button>
      </view>
    </view>

    <!-- Disease Search Modal -->
    <view v-if="showDiseaseModal" class="modal-overlay" @click="closeDiseaseModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择关联疾病</text>
          <text class="close-icon" @click="closeDiseaseModal">×</text>
        </view>
        <view class="search-bar">
          <input 
            class="search-input" 
            v-model="diseaseSearchQuery" 
            placeholder="搜索疾病（如：高血压、糖尿病）"
            @input="onDiseaseSearchInput"
            confirm-type="search"
          />
        </view>
        <scroll-view scroll-y class="result-list">
          <view 
            v-for="item in filteredDiseases" 
            :key="item.id" 
            class="result-item"
            @click="selectDisease(item)"
          >
            <view class="item-main">
              <text class="item-name">{{ item.name }}</text>
              <text class="item-category" v-if="item.status">{{ item.status }}</text>
            </view>
          </view>
          <view v-if="filteredDiseases.length === 0 && !diseaseLoading" class="no-results">
            <text v-if="patientDiseases.length === 0">暂无慢性病记录，请先在"慢性病管理"中添加</text>
            <text v-else>未找到相关疾病，请尝试其他关键词</text>
          </view>
          <view v-if="patientDiseases.length === 0" class="no-data-action">
            <button class="btn-go-add" @click="goToDiseaseManage">去添加慢性病</button>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- Hospital Search Modal -->
    <view v-if="showHospitalModal" class="modal-overlay" @click="closeHospitalModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择医院</text>
          <text class="close-icon" @click="closeHospitalModal">×</text>
        </view>
        <view class="search-bar">
          <input 
            class="search-input" 
            v-model="hospitalSearchQuery" 
            placeholder="搜索医院（如：协和、同仁）"
            @input="onHospitalSearchInput"
            confirm-type="search"
          />
        </view>
        <scroll-view scroll-y class="result-list">
          <view 
            v-for="item in hospitalResults" 
            :key="item.id" 
            class="result-item"
            @click="selectHospital(item)"
          >
            <view class="item-main">
              <text class="item-name">{{ item.name }}</text>
              <text class="item-category" v-if="item.level">{{ item.level }}</text>
            </view>
          </view>
          <view v-if="hospitalResults.length === 0 && !hospitalLoading" class="no-results">
            <text>未找到相关医院，请尝试其他关键词</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed, onMounted } from 'vue'
import { parseReport, uploadReport } from '@/api/report'
import { getDiseases, getPatientProfile } from '@/api/patient'
import { getHospitals } from '@/api/hospital'

// State
const selectedDisease = ref<any>(null)
const selectedHospital = ref<any>(null)
const visitDate = ref('')
const fileName = ref('')
const tempFilePath = ref('')
const parsedResult = ref<any>(null)

// Patient diseases
const patientDiseases = ref<any[]>([])

// Disease Modal State
const showDiseaseModal = ref(false)
const diseaseSearchQuery = ref('')
const diseaseLoading = ref(false)

// Hospital Modal State
const showHospitalModal = ref(false)
const hospitalSearchQuery = ref('')
const hospitalResults = ref<any[]>([])
const hospitalLoading = ref(false)

let hospitalSearchTimer: any = null

// Computed
const filteredDiseases = computed(() => {
  if (!diseaseSearchQuery.value.trim()) {
    return patientDiseases.value
  }
  const keyword = diseaseSearchQuery.value.toLowerCase().trim()
  return patientDiseases.value.filter(d =>
    d.name?.toLowerCase().includes(keyword)
  )
})

const formattedSummary = computed(() => {
  const src = parsedResult.value?.summary || ''
  return src
    .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?>[\s\S]*?<\/style>/gi, '')
    .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, '')
    .replace(/\sstyle\s*=\s*(['"]).*?\1/gi, '')
})

// Methods
onMounted(async () => {
  try {
    const res: any = await getDiseases()
    patientDiseases.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('Failed to fetch diseases', e)
  }
})

const openSearchModal = (type: 'disease' | 'hospital') => {
  if (type === 'disease') {
    showDiseaseModal.value = true
    diseaseSearchQuery.value = ''
  } else {
    showHospitalModal.value = true
    hospitalSearchQuery.value = ''
    fetchHospitals()
  }
}

const closeDiseaseModal = () => {
  showDiseaseModal.value = false
}

const closeHospitalModal = () => {
  showHospitalModal.value = false
}

const onDiseaseSearchInput = () => {
  // Filter is computed
}

const onHospitalSearchInput = () => {
  if (hospitalSearchTimer) clearTimeout(hospitalSearchTimer)
  hospitalSearchTimer = setTimeout(() => {
    fetchHospitals()
  }, 300)
}

const fetchHospitals = async () => {
  hospitalLoading.value = true
  try {
    const res: any = await getHospitals({ q: hospitalSearchQuery.value })
    hospitalResults.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error(e)
    hospitalResults.value = []
  } finally {
    hospitalLoading.value = false
  }
}

const selectDisease = (item: any) => {
  selectedDisease.value = item
  closeDiseaseModal()
}

const selectHospital = (item: any) => {
  selectedHospital.value = item
  closeHospitalModal()
}

const onDateChange = (e: any) => {
  visitDate.value = e.detail.value
}

const chooseFile = () => {
  uni.chooseImage({
    count: 1,
    success: (res) => {
      fileName.value = res.tempFilePaths[0].split('/').pop() || 'image.jpg'
      tempFilePath.value = res.tempFilePaths[0]
    }
  })
}

const clearFile = () => {
  fileName.value = ''
  tempFilePath.value = ''
  parsedResult.value = null
}

const previewImage = (url: string) => {
  if (!url) return
  uni.previewImage({
    urls: [url]
  })
}

const submitReport = () => {
  if (!selectedDisease.value) {
    uni.showToast({ title: '请选择关联疾病', icon: 'none' })
    return
  }
  if (!tempFilePath.value) {
    uni.showToast({ title: '请选择文件', icon: 'none' })
    return
  }

  uni.showLoading({ title: '正在解析...' })

  const formData: any = {
    patient_disease_id: String(selectedDisease.value.id)
  }
  if (selectedHospital.value) {
    formData.hospital_id = String(selectedHospital.value.id)
  }

  parseReport(tempFilePath.value, formData)
    .then((res: any) => {
      uni.hideLoading()
      parsedResult.value = res

      // Normalize metrics
      const arr = Array.isArray(parsedResult.value.metrics) ? parsedResult.value.metrics : []
      parsedResult.value.metrics = arr.map((m: any) => ({
        name: m?.name || '',
        code: m?.code || '',
        value: m?.value || '',
        unit: m?.unit || '',
        reference_range: m?.range || m?.reference_range || '',
        is_abnormal: !!m?.abnormal || !!m?.is_abnormal || !!m?.abnormal_symbol,
        abnormal_symbol: m?.abnormal_symbol || ''
      }))

      if (!parsedResult.value.hospital_name && selectedHospital.value) {
        parsedResult.value.hospital_name = selectedHospital.value.name
      }
      if (!parsedResult.value.report_date) {
        parsedResult.value.report_date = visitDate.value || new Date().toISOString().split('T')[0]
      }
    })
    .catch((err) => {
      uni.hideLoading()
      const msg = err?.message?.includes('超时') ? 'OCR服务超时，请稍后重试' : (err?.message || '解析失败')
      uni.showToast({ title: msg, icon: 'none' })
    })
}

const addMetricRow = () => {
  if (!parsedResult.value) return
  if (!parsedResult.value.metrics) {
    parsedResult.value.metrics = []
  }
  parsedResult.value.metrics.push({
    name: '',
    code: '',
    value: '',
    unit: '',
    reference_range: '',
    is_abnormal: false,
    abnormal_symbol: ''
  })
}

const removeMetricRow = (index: number) => {
  if (!parsedResult.value?.metrics) return
  parsedResult.value.metrics.splice(index, 1)
}

const confirmSubmit = async () => {
  if (!selectedDisease.value) {
    uni.showToast({ title: '请选择关联疾病', icon: 'none' })
    return
  }

  uni.showLoading({ title: '提交中...' })

  try {
    const me: any = await getPatientProfile()

    const metrics = Array.isArray(parsedResult.value?.metrics) ? parsedResult.value.metrics : []
    const cleanedMetrics = metrics
      .map((m: any) => ({
        name: String(m.name || '').trim(),
        code: String(m.code || '').trim(),
        value: String(m.value || '').trim(),
        unit: String(m.unit || '').trim(),
        reference_range: String(m.reference_range || '').trim(),
        is_abnormal: !!m.is_abnormal,
        abnormal_symbol: String(m.abnormal_symbol || '').trim()
      }))
      .filter((m: any) => m.name || m.value)

    await uploadReport({
      patient_id: me.id,
      hospital_name: parsedResult.value.hospital_name || selectedHospital.value?.name || '',
      report_date: parsedResult.value.report_date,
      report_type: '病历',
      image_url: parsedResult.value.image_url,
      file_name: parsedResult.value.file_name,
      summary: parsedResult.value.summary,
      patient_disease_id: selectedDisease.value.id,
      data: { metrics: cleanedMetrics },
      metrics: cleanedMetrics
    })

    uni.hideLoading()
    uni.showToast({ title: '提交成功' })
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/medical-record/list'
      })
    }, 1200)
  } catch (e) {
    console.error('Submit error:', e)
    uni.hideLoading()
    uni.showToast({ title: '提交失败，请重试', icon: 'none' })
  }
}

const cancelParse = () => {
  parsedResult.value = null
}

const goToDiseaseManage = () => {
  closeDiseaseModal()
  safeNavigate({ url: '/pages/disease/manage' })
}
</script>

<style>
.page-container {
  padding: 20px;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.upload-card {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.upload-header {
  text-align: center;
  margin-bottom: 32px;
}

.upload-icon-wrapper {
  width: 64px;
  height: 64px;
  background-color: #eff6ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.upload-icon {
  font-size: 32px;
  color: #3b82f6;
  font-weight: bold;
}

.upload-title {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8px;
}

.upload-subtitle {
  display: block;
  font-size: 14px;
  color: #9ca3af;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row.full-width {
  width: 100%;
}

.form-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
}

.required {
  color: #ef4444;
}

.input-box {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.text-gray {
  color: #9ca3af;
  font-size: 14px;
}

.text-black {
  color: #111827;
  font-size: 14px;
}

.arrow {
  color: #9ca3af;
  font-size: 12px;
}

.clear-btn {
  color: #ef4444;
  font-size: 20px;
  padding: 4px;
}

.upload-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-radius: 12px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  margin-top: 12px;
  border: none;
}

.upload-btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* Parsed Result Styles */
.parsed-result-container {
  animation: fadeIn 0.3s ease;
}

.result-header {
  margin-bottom: 16px;
  padding-left: 4px;
}

.result-title {
  display: block;
  font-size: 18px;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 4px;
}

.result-subtitle {
  font-size: 13px;
  color: #6b7280;
}

.report-card.preview-card {
  background-color: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.header-left {
  display: flex;
  gap: 12px;
}

.file-icon {
  width: 40px;
  height: 40px;
  background-color: #eff6ff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.report-name {
  font-size: 16px;
  font-weight: bold;
  color: #111827;
}

.report-meta {
  font-size: 12px;
  color: #6b7280;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-normal {
  background-color: #ecfdf5;
  color: #059669;
}

.metrics-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metrics-header {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1fr 2fr 64px;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.metrics-header .mh {
  font-size: 12px;
  color: #6b7280;
}

.metric-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1fr 2fr 64px;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed #f3f4f6;
}

.metric-row:last-child {
  border-bottom: none;
}

.mi {
  background-color: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
}

.row-del {
  background: #fff;
  color: #ef4444;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  font-size: 13px;
}

.row-add {
  background: #10b981;
  color: #fff;
  border-radius: 12px;
  height: 40px;
  font-size: 14px;
}

.metrics-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.summary-box {
  margin-top: 16px;
  background-color: #f9fafb;
  padding: 12px;
  border-radius: 8px;
}

.summary-label {
  font-size: 13px;
  font-weight: bold;
  color: #374151;
  display: block;
  margin-bottom: 4px;
}

.summary-content {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
}

.summary-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 8px 0;
}

.summary-content td, .summary-content th {
  border: 1px solid #e2e8f0;
  padding: 6px 8px;
  text-align: left;
  word-break: break-word;
}

.imaging-image-wrap {
  margin-top: 12px;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
}

.imaging-image {
  width: 100%;
  border-radius: 12px;
}

.action-footer {
  display: flex;
  gap: 16px;
}

.confirm-btn {
  flex: 2;
  background-color: #3b82f6;
  color: white;
  border-radius: 25px;
  font-size: 15px;
}

.cancel-btn {
  flex: 1;
  background-color: #fff;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 25px;
  font-size: 15px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  width: 100%;
  background-color: white;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 20px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: #111827;
}

.close-icon {
  font-size: 24px;
  color: #9ca3af;
  padding: 4px;
}

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  background-color: #f3f4f6;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

.result-list {
  max-height: 300px;
  min-height: 200px;
}

.result-item {
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-item:active {
  background-color: #f9fafb;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-size: 16px;
  color: #1f2937;
}

.item-category {
  font-size: 12px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  align-self: flex-start;
}

.no-results {
  padding: 20px 0;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}

.no-data-action {
  padding: 16px 0;
  text-align: center;
}

.btn-go-add {
  background: #3b82f6;
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  padding: 10px 24px;
}
</style>
