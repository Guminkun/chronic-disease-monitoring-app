<template>
  <view class="container">
    <!-- Navigation Bar -->
    <view class="nav-bar">
      <view class="back-btn" @click="goBack">
        <text class="icon-back">‹</text>
        <text>返回患者列表</text>
      </view>
      <view class="actions">
        <button class="btn-action green" @click="sendMessage">
          <text class="icon">💬</text>
          <text>发送消息</text>
        </button>
        <button class="btn-action white" @click="makeCall">
          <text class="icon">📞</text>
          <text>电话咨询</text>
        </button>
      </view>
    </view>

    <!-- Patient Info Card -->
    <view class="card patient-card">
      <view class="card-header">
        <view class="name-row">
          <text class="name">{{ patient.name }}</text>
          <view class="binding-status">
            <text class="icon-heart">💙</text>
            <text>已绑定</text>
          </view>
        </view>
        <text class="binding-time">绑定时间: {{ patient.bindingDate || '—' }}</text>
      </view>
      
      <text class="patient-demographics">
        {{ patient.age ? patient.age + '岁' : '年龄未知' }} {{ patient.gender || '性别未知' }} · {{ patient.phone || '—' }}
      </text>

      <view class="diagnosis-grid">
        <view class="diagnosis-item" v-for="(tag, index) in patient.tags" :key="index">
          <text class="diagnosis-label">诊断</text>
          <text class="diagnosis-value">{{ tag }}</text>
        </view>
        <view v-if="!patient.tags || patient.tags.length === 0" class="diagnosis-item empty">
          <text class="diagnosis-value">暂无诊断记录</text>
        </view>
      </view>
    </view>

    <!-- Tabs -->
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'vitals' }"
        @click="currentTab = 'vitals'"
      >
        <text>生命体征</text>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'meds' }"
        @click="currentTab = 'meds'"
      >
        <text>用药信息</text>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'reports' }"
        @click="currentTab = 'reports'"
      >
        <text>检查报告</text>
      </view>
    </view>

    <!-- Tab Content: Vital Signs -->
    <view v-if="currentTab === 'vitals'" class="tab-content">
      <view class="card chart-card">
        <text class="card-title">最近测量数据</text>
        <view class="readings-list" v-if="readings.length > 0">
          <view class="reading-item" v-for="(r, idx) in readings" :key="idx">
             <text class="r-type">{{ getReadingTypeName(r.type) }}</text>
             <text class="r-val">{{ r.value_1 }}{{ r.value_2 ? '/' + r.value_2 : '' }} {{ r.unit }}</text>
             <text class="r-date">{{ formatDate(r.recorded_at) }}</text>
          </view>
        </view>
        <view v-else class="empty-state">
           <text>暂无测量数据</text>
        </view>
      </view>
    </view>

    <!-- Tab Content: Medication Info -->
    <view v-if="currentTab === 'meds'" class="tab-content">
      <view v-if="medications.length > 0">
        <view class="card med-card" v-for="(med, index) in medications" :key="index">
          <view class="med-header">
            <text class="med-name">{{ med.name }}</text>
            <view class="status-badge" :class="med.isActive ? 'active' : 'inactive'">
              <text>{{ med.isActive ? '使用中' : '已停止' }}</text>
            </view>
          </view>
          <text class="med-instruction">医嘱: {{ med.instruction }}</text>
        </view>
      </view>
      <view v-else class="empty-state">
        <text>暂无用药提醒记录</text>
      </view>
    </view>

    <!-- Tab Content: Check Reports -->
    <view v-if="currentTab === 'reports'" class="tab-content">
      <view v-if="reports.length > 0">
        <view 
          class="card report-item" 
          v-for="(report, index) in reports" 
          :key="index"
          @click="openReportDetail(report)"
        >
          <view class="report-icon">
            <text>📅</text>
          </view>
          <view class="report-info">
            <text class="report-type">{{ report.type }}</text>
            <text class="report-date">{{ report.date }}</text>
          </view>
          <view class="report-status" :class="report.statusClass">
            <text>{{ report.status }}</text>
          </view>
        </view>
      </view>
      <view v-else class="empty-state">
        <text>暂无检查报告</text>
      </view>

      <view class="card clinical-note">
        <text class="card-title">临床备注</text>
        <view class="note-box">
          <text class="note-text">{{ clinicalNote }}</text>
        </view>
        <button class="btn-save" @click="saveNote">保存备注</button>
      </view>
    </view>

    <!-- Report Detail Modal -->
    <view v-if="showReportModal" class="modal-overlay" @click="closeReportDetail">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">检查报告详情</text>
          <text class="close-btn" @click="closeReportDetail">×</text>
        </view>
        
        <view class="modal-body" v-if="selectedReport">
          <view class="report-meta">
            <view>
              <text class="meta-label">检查类型</text>
              <text class="meta-value">{{ selectedReport.type }}</text>
            </view>
            <view>
              <text class="meta-label">检查日期</text>
              <text class="meta-value">{{ selectedReport.date }}</text>
            </view>
            <view v-if="selectedReport.hospital">
               <text class="meta-label">医院</text>
               <text class="meta-value">{{ selectedReport.hospital }}</text>
            </view>
          </view>

          <view class="report-result-section">
            <text class="section-title">检查结果</text>
            <view class="status-badge large" :class="selectedReport.statusClass">
              <text>{{ selectedReport.status }}</text>
            </view>
          </view>

          <view class="indicators-section" v-if="selectedReport.indicators && selectedReport.indicators.length">
            <text class="section-title">主要指标</text>
            <view class="indicator-row" v-for="(ind, idx) in selectedReport.indicators" :key="idx">
              <text class="ind-name">{{ ind.name }}</text>
              <text class="ind-value">{{ ind.value }}</text>
            </view>
          </view>

          <view class="advice-section" v-if="selectedReport.summary">
            <text class="section-title">报告总结</text>
            <text class="advice-text">{{ selectedReport.summary }}</text>
          </view>
        </view>

        <view class="modal-footer">
          <button class="btn-outline" @click="closeReportDetail">关闭</button>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getPatientDetail, getPatientDiseases, getPatientReports, getPatientReminders, getPatientReadings } from '@/api/doctor'

// --- State ---
const currentTab = ref('vitals') // vitals, meds, reports
const showReportModal = ref(false)
const selectedReport = ref<any>(null)
const clinicalNote = ref('患者血压控制不理想，建议增加血压监测频率。考虑调整抗高血压药物。')

const patient = ref<any>({
  id: '',
  name: '',
  age: '',
  gender: '',
  phone: '',
  bindingDate: '',
  tags: []
})

const medications = ref<any[]>([])
const reports = ref<any[]>([])
const readings = ref<any[]>([])

// --- Methods ---
onLoad(async (options: any) => {
  if (options.id) {
    patient.value.id = options.id
    if (options.name) patient.value.name = options.name
    await loadData(options.id)
  }
})

const loadData = async (id: string) => {
  try {
    uni.showLoading({ title: '加载中...' })
    const [p, d, r, rem, read]: any[] = await Promise.all([
      getPatientDetail(id),
      getPatientDiseases(id),
      getPatientReports(id),
      getPatientReminders(id),
      getPatientReadings(id)
    ])
    
    // Process Patient Info
    // Calculate age if DOB exists
    let age = '?'
    if (p.id_card && p.id_card.length === 18) {
       // Simple extract from ID card or use backend logic if available
       // Backend PatientResponse doesn't explicitly have DOB but ID card might have it or age field
       age = p.age || '?'
    } else {
       age = p.age || '?'
    }

    patient.value = {
      ...patient.value,
      ...p,
      age: age,
      tags: d.map((x: any) => x.name)
    }
    
    // Process Medications
    medications.value = rem.filter((x: any) => x.type === 'medication').map((x: any) => ({
      name: x.title,
      instruction: x.schedule_text,
      isActive: x.is_active
    }))
    
    // Process Reports
    reports.value = r.map((x: any) => {
       // indicators from data json
       let indicators: any[] = []
       if (x.data && typeof x.data === 'object') {
          indicators = Object.entries(x.data).map(([k, v]) => ({ name: k, value: String(v) }))
       }
       
       return {
         ...x,
         date: x.report_date,
         type: x.report_type,
         status: x.status === 'processed' ? '已处理' : '处理中', 
         statusClass: x.status === 'processed' ? 'status-normal' : 'status-warning',
         hospital: x.hospital_name,
         summary: x.summary,
         indicators
       }
    })

    // Process Readings
    readings.value = read

  } catch (e) {
    console.error(e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

const getReadingTypeName = (type: string) => {
  const map: Record<string, string> = {
    'blood_pressure': '血压',
    'blood_sugar': '血糖',
    'weight': '体重',
    'heart_rate': '心率'
  }
  return map[type] || type
}

const formatDate = (str: string) => {
  if (!str) return ''
  return str.split('T')[0]
}

const goBack = () => {
  uni.navigateBack()
}

const sendMessage = () => {
  uni.navigateTo({
    url: `/pages/chat/chat?id=${patient.value.id}&name=${patient.value.name}`
  })
}

const makeCall = () => {
  uni.makePhoneCall({
    phoneNumber: patient.value.phone
  })
}

const openReportDetail = (report: any) => {
  selectedReport.value = report
  showReportModal.value = true
}

const closeReportDetail = () => {
  showReportModal.value = false
}

const saveNote = () => {
  uni.showToast({ title: '备注已保存', icon: 'success' })
}

const downloadReport = () => {
  uni.showToast({ title: '开始下载...', icon: 'none' })
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 16px;
  box-sizing: border-box;
}

/* Nav Bar */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  color: #0284c7;
  font-size: 16px;
  font-weight: 500;
}
.icon-back {
  font-size: 24px;
  margin-right: 4px;
  line-height: 1;
}

.actions {
  display: flex;
  gap: 8px;
}
.btn-action {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  line-height: 1.2;
  border: none;
}
.btn-action.green {
  background-color: #dcfce7;
  color: #15803d;
}
.btn-action.white {
  background-color: #fff;
  color: #475569;
  border: 1px solid #e2e8f0;
}
.icon {
  font-size: 14px;
}

/* Patient Card */
.card {
  background-color: #fff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.name {
  font-size: 20px;
  font-weight: 600;
  color: #0f172a;
}
.binding-status {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: #dbeafe;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #1e40af;
}
.icon-heart {
  font-size: 10px;
}
.binding-time {
  font-size: 12px;
  color: #94a3b8;
}
.patient-demographics {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
  display: block;
}
.diagnosis-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.diagnosis-item {
  background-color: #f1f5f9;
  padding: 4px 10px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}
.diagnosis-item.empty {
  background-color: transparent;
  padding: 0;
}
.diagnosis-label {
  font-size: 10px;
  color: #94a3b8;
}
.diagnosis-value {
  font-size: 12px;
  font-weight: 500;
  color: #334155;
}

/* Tabs */
.tabs {
  display: flex;
  background-color: #fff;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
}
.tab-item {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 14px;
  color: #64748b;
  border-radius: 8px;
  transition: all 0.3s;
}
.tab-item.active {
  background-color: #eff6ff;
  color: #2563eb;
  font-weight: 600;
}

/* Tab Content */
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
  display: block;
}

/* Vitals */
.readings-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.reading-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}
.reading-item:last-child {
  border-bottom: none;
}
.r-type {
  font-size: 14px;
  color: #475569;
}
.r-val {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}
.r-date {
  font-size: 12px;
  color: #94a3b8;
}

/* Meds */
.med-card {
  margin-bottom: 12px;
}
.med-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.med-name {
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
}
.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
}
.status-badge.active {
  background-color: #dcfce7;
  color: #15803d;
}
.status-badge.inactive {
  background-color: #f1f5f9;
  color: #94a3b8;
}
.med-instruction {
  font-size: 13px;
  color: #64748b;
}

/* Reports */
.report-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}
.report-icon {
  width: 40px;
  height: 40px;
  background-color: #eff6ff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.report-info {
  flex: 1;
}
.report-type {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  display: block;
}
.report-date {
  font-size: 12px;
  color: #94a3b8;
}
.report-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 8px;
}
.status-normal {
  background-color: #dcfce7;
  color: #15803d;
}
.status-warning {
  background-color: #fef9c3;
  color: #854d0e;
}

.clinical-note {
  margin-top: 20px;
}
.note-box {
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #e2e8f0;
}
.note-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.5;
}
.btn-save {
  background-color: #2563eb;
  color: #fff;
  font-size: 14px;
  border-radius: 8px;
}

.empty-state {
  padding: 32px 0;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.modal-content {
  background-color: #fff;
  border-radius: 20px;
  width: 100%;
  max-width: 340px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}
.modal-header {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
}
.close-btn {
  font-size: 24px;
  color: #94a3b8;
  line-height: 1;
}
.modal-body {
  padding: 20px;
  overflow-y: auto;
}
.report-meta {
  background-color: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.meta-label {
  font-size: 12px;
  color: #64748b;
  margin-right: 8px;
}
.meta-value {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
  display: block;
}
.status-badge.large {
  display: inline-block;
  padding: 6px 12px;
  font-size: 14px;
}
.report-result-section, .indicators-section, .advice-section {
  margin-bottom: 20px;
}
.indicator-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #e2e8f0;
}
.ind-name {
  color: #64748b;
  font-size: 13px;
}
.ind-value {
  color: #0f172a;
  font-weight: 500;
  font-size: 13px;
}
.advice-text {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
}
.modal-footer {
  padding: 16px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
}
.btn-outline {
  background-color: #fff;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 8px;
}
</style>
