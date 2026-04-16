<template>
  <view class="page-container">
    <PageHeader title="病历详情" />

    <scroll-view scroll-y class="page-scroll" v-if="!loading">
      <view class="image-section" v-if="record.image_url" @click="previewImage">
        <image 
          :src="record.image_url" 
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

      <view class="info-section">
        <view class="section-card" v-if="basicFields.length > 0">
          <view class="section-header">
            <text class="section-title">基本信息</text>
          </view>
          <view class="section-body">
            <view v-for="field in basicFields" :key="field.key" class="info-item">
              <text class="info-label">{{ field.label }}</text>
              <text class="info-value">{{ field.value }}</text>
            </view>
          </view>
        </view>

        <view class="section-card" v-if="medicalFields.length > 0">
          <view class="section-header">
            <text class="section-title">病历内容</text>
          </view>
          <view class="section-body">
            <view v-for="field in medicalFields" :key="field.key" class="content-item">
              <text class="content-label">{{ field.label }}</text>
              <text class="content-value">{{ field.value }}</text>
            </view>
          </view>
        </view>

        <view class="section-card" v-if="Object.keys(record).length === 0">
          <view class="empty-card">
            <text class="empty-icon">📋</text>
            <text class="empty-text">暂无病历数据</text>
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

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getMedicalRecordDetail } from '@/api/medical-record'

const record = ref<any>({})
const loading = ref(false)

const FIELD_LABELS: Record<string, string> = {
  patient_name: '姓名',
  gender: '性别',
  age: '年龄',
  hospital: '医院',
  department: '科室',
  report_type: '诊断',
  report_date: '就诊日期',
  chief_complaint: '主诉',
  present_illness: '现病史',
  past_history: '既往史',
  personal_history: '个人史',
  family_history: '家族史'
}

const BASIC_FIELD_KEYS = ['patient_name', 'gender', 'age', 'hospital', 'department', 'report_type', 'report_date']
const MEDICAL_FIELD_KEYS = ['chief_complaint', 'present_illness', 'past_history', 'personal_history', 'family_history']

const basicFields = computed(() => {
  const data = record.value?.data || {}
  const fields: any[] = []
  
  BASIC_FIELD_KEYS.forEach(key => {
    const value = data[key] || record.value[key]
    if (value && String(value).trim()) {
      fields.push({
        key,
        label: FIELD_LABELS[key] || key,
        value: String(value).trim()
      })
    }
  })
  
  return fields
})

const medicalFields = computed(() => {
  const data = record.value?.data || {}
  const fields: any[] = []
  
  MEDICAL_FIELD_KEYS.forEach(key => {
    const value = data[key]
    if (value && String(value).trim()) {
      fields.push({
        key,
        label: FIELD_LABELS[key] || key,
        value: String(value).trim()
      })
    }
  })
  
  return fields
})

const loadRecord = async (id: string) => {
  loading.value = true
  try {
    const res: any = await getMedicalRecordDetail(id)
    record.value = res || {}
  } catch (err) {
    console.error('Load medical record error:', err)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  if (options?.id) {
    loadRecord(options.id)
  }
})
</script>

<style>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  display: flex;
  flex-direction: column;
}






.page-scroll {
  flex: 1;
}

.image-section {
  position: relative;
  height: 25vh;
  background: #f1f5f9;
}

.report-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.5), transparent);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 12px;
}

.image-hint {
  display: flex;
  align-items: center;
  gap: 6px;
}

.hint-icon {
  font-size: 16px;
  color: #ffffff;
}

.hint-text {
  font-size: 13px;
  color: #ffffff;
  font-weight: 500;
}

.info-section {
  padding: 16px;
}

.section-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid #f1f5f9;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.section-body {
  padding: 12px 16px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f8fafc;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
  text-align: right;
  flex: 1;
  margin-left: 16px;
}

.content-item {
  padding: 12px 0;
  border-bottom: 1px solid #f8fafc;
}

.content-item:last-child {
  border-bottom: none;
}

.content-label {
  display: block;
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 8px;
}

.content-value {
  display: block;
  font-size: 14px;
  color: #334155;
  line-height: 1.6;
}

.empty-card {
  padding: 48px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
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
  background: rgba(255, 255, 255, 0.95);
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
</style>
