<template>
  <view class="container">
    <!-- Header -->
    <view class="header-card">
      <view class="doctor-info">
        <view class="welcome-row">
          <text class="welcome-text">欢迎，{{ doctorInfo.name }}</text>
        </view>
        <text class="dept-text">{{ doctorInfo.department }} · {{ doctorInfo.hospital }}</text>
      </view>
      <view class="patient-count-badge">
        <text class="count-num">{{ stats.totalPatients }}</text>
        <text class="count-label">绑定患者</text>
      </view>
    </view>

    <!-- Stats Grid -->
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-label">总患者数</text>
        <text class="stat-value black">{{ stats.totalPatients }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">本周新增</text>
        <text class="stat-value blue">{{ stats.newThisWeek }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">需关注患者</text>
        <view class="value-row">
          <text class="stat-value red">{{ stats.needAttention }}</text>
          <text class="icon-alert">!</text>
        </view>
      </view>
      <view class="stat-card">
        <text class="stat-label">待处理消息</text>
        <view class="value-row">
          <text class="stat-value green">{{ stats.pendingMessages }}</text>
          <text class="icon-clock">🕒</text>
        </view>
      </view>
    </view>

    <!-- Tabs -->
    <view class="tabs-container">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 0 }"
        @click="currentTab = 0"
      >
        <text class="tab-icon">👥</text>
        <text class="tab-text">我的患者</text>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 1 }"
        @click="currentTab = 1"
      >
        <text class="tab-icon">💬</text>
        <text class="tab-text">医患沟通</text>
      </view>
    </view>

    <!-- Search & Add -->
    <view class="action-bar">
      <view class="search-box">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input" 
          placeholder="搜索患者姓名、电话或身份证号..." 
          placeholder-style="color: #94a3b8"
          v-model="searchQuery"
        />
      </view>
      <button class="btn-add" @click="navigateToAddPatient">
        <text>+ 添加患者</text>
      </button>
    </view>

    <!-- Patient List -->
    <view class="patient-list">
      <view 
        v-for="(patient, index) in filteredPatients" 
        :key="index" 
        class="patient-card"
        @click="viewPatientDetail(patient)"
      >
        <view class="card-top">
          <view class="patient-basic">
            <text class="p-name">{{ patient.name }}</text>
            <text class="p-info">{{ patient.age }}岁 {{ patient.gender }}</text>
            <view v-if="patient.needAttention" class="tag-attention">
              <text>! 需关注</text>
            </view>
          </view>
          <text class="arrow-right">></text>
        </view>

        <view class="metrics-row">
          <view class="metric-item">
            <text class="m-label">血压</text>
            <text class="m-value">{{ patient.bloodPressure || '---' }}</text>
          </view>
          <view class="metric-item">
            <text class="m-label">血糖</text>
            <text class="m-value">{{ patient.bloodSugar || '---' }}</text>
          </view>
        </view>

        <view class="tags-row">
          <view 
            v-for="(tag, tIdx) in patient.tags" 
            :key="tIdx" 
            class="disease-tag"
            :class="getTagClass(tag)"
          >
            {{ tag }}
          </view>
        </view>

        <view class="card-footer">
          <text class="update-time">最后更新: {{ patient.lastUpdate }}</text>
          <view class="btn-chat" @click.stop="navigateToChat(patient)">
            <text class="icon-chat">💬</text>
            <text>聊天</text>
          </view>
        </view>
      </view>
    </view>

  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getMyPatients } from '../../api/doctor'

const navigateToAddPatient = () => {
  uni.navigateTo({
    url: '/pages/doctor/add-patient'
  })
}

const navigateToChat = (patient: Patient) => {
  if (patient.userId) {
    uni.navigateTo({
      url: `/pages/chat/chat?id=${patient.userId}&name=${patient.name}`
    })
  } else {
    uni.showToast({ title: '无法获取患者ID', icon: 'none' })
  }
}

const currentTab = ref(0)
const searchQuery = ref('')

const doctorInfo = ref({
  name: '王医生',
  department: '心内科',
  hospital: '北京协和医院'
})

const stats = ref({
  totalPatients: 0,
  newThisWeek: 0,
  needAttention: 0,
  pendingMessages: 0
})

interface Patient {
  id: string
  userId: string
  name: string
  age: number
  gender: string
  bloodPressure: string
  bloodSugar: string
  tags: string[]
  lastUpdate: string
  needAttention: boolean
}

const patients = ref<Patient[]>([])

const fetchPatients = async () => {
  try {
    const res: any = await getMyPatients()
    // Map BindingResponse to Patient view model
    patients.value = (Array.isArray(res) ? res : (res?.data || [])).map((binding: any) => {
      const p = binding.patient || {}
      return {
        id: p.id || binding.patient_id,
        userId: p.user_id, // Map user_id for chat
        name: p.name || 'Unknown',
        age: p.age || 0,
        gender: p.gender === 'male' ? '男' : (p.gender === 'female' ? '女' : '未知'),
        bloodPressure: '---', // Placeholder as API doesn't return this yet
        bloodSugar: '---',    // Placeholder
        tags: [],             // Placeholder
        lastUpdate: new Date(binding.created_at).toLocaleDateString(),
        needAttention: false
      }
    })
    stats.value.totalPatients = patients.value.length
  } catch (error) {
    console.error('Failed to fetch patients', error)
  }
}

onMounted(() => {
  fetchPatients()
})

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value
  return patients.value.filter(p => p.name.includes(searchQuery.value))
})

const getTagClass = (tag: string) => {
  // Simple logic to color tags differently if needed
  // For now just returning default class
  return ''
}

// Duplicate function removed

const viewPatientDetail = (patient: Patient) => {
  uni.navigateTo({
    url: `/pages/doctor/patient-detail?id=${patient.id}&name=${patient.name}`
  })
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
  padding: 16px;
  box-sizing: border-box;
}

/* Header Card */
.header-card {
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  border: 1px solid #bae6fd;
}

.doctor-info {
  display: flex;
  flex-direction: column;
}

.welcome-text {
  font-size: 20px;
  font-weight: bold;
  color: #0f172a;
  margin-bottom: 4px;
}

.dept-text {
  font-size: 14px;
  color: #64748b;
}

.patient-count-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.count-num {
  font-size: 24px;
  font-weight: bold;
  color: #0284c7;
}

.count-label {
  font-size: 12px;
  color: #64748b;
}

/* Stats Grid */
.stats-grid {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 10px;
}

.stat-card {
  flex: 1;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.stat-value.black { color: #0f172a; }
.stat-value.blue { color: #0284c7; }
.stat-value.red { color: #ef4444; }
.stat-value.green { color: #22c55e; }

.value-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-alert {
  color: #ef4444;
  font-size: 14px;
  border: 1px solid #ef4444;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  text-align: center;
  line-height: 14px;
}

.icon-clock {
  font-size: 14px;
}

/* Tabs */
.tabs-container {
  display: flex;
  background-color: #e2e8f0;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 20px;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  border-radius: 6px;
  gap: 6px;
}

.tab-item.active {
  background-color: #ffffff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.tab-text {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.tab-item.active .tab-text {
  color: #0f172a;
}

/* Action Bar */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.search-box {
  flex: 1;
  background-color: #ffffff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  padding: 10px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.search-icon {
  margin-right: 8px;
  color: #94a3b8;
}

.search-input {
  flex: 1;
  font-size: 14px;
}

.btn-add {
  background-image: linear-gradient(135deg, var(--primary-start), var(--primary-end));
  color: #ffffff;
  font-size: 14px;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  line-height: 1.5;
}

/* Patient List */
.patient-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.patient-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.patient-basic {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.p-name {
  font-size: 18px;
  font-weight: bold;
  color: #0f172a;
}

.p-info {
  font-size: 14px;
  color: #64748b;
}

.tag-attention {
  background-color: #fecaca;
  color: #ef4444;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.arrow-right {
  color: #cbd5e1;
  font-size: 18px;
}

.metrics-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  width: 45%;
}

.m-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.m-value {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.disease-tag {
  background-color: #e2e8f0;
  color: #475569;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.card-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.update-time {
  font-size: 12px;
  color: #94a3b8;
}

.btn-chat {
  display: flex;
  align-items: center;
  background-color: var(--surface-muted);
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  color: var(--primary-start);
  font-size: 12px;
}

.icon-chat {
  margin-right: 4px;
}
</style>
