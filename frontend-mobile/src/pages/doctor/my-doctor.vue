<template>
  <view class="page-container">
    <!-- Header Section -->
    <view class="header-section">
      <view class="title-row">
        <text class="page-title">我的医生</text>
        <button class="bind-btn" @click="goToBindDoctor">
          <text class="plus-icon">+</text> 绑定医生
        </button>
      </view>
      <text class="subtitle">管理您的医患关系</text>
    </view>

    <!-- Doctor List -->
    <view class="doctor-list">
      <view v-for="(doctor, index) in doctors" :key="index" class="doctor-card">
        <view class="card-header">
          <text class="doctor-name">{{ doctor.name }}</text>
        </view>
        
        <view class="info-row">
          <text class="info-text">{{ doctor.department }} • {{ doctor.hospital }}</text>
        </view>
        
        <view class="info-row">
          <text class="label">专长：</text>
          <text class="info-text">{{ doctor.specialty }}</text>
        </view>
        
        <view class="info-row">
          <text class="label">绑定时间：</text>
          <text class="info-text">{{ doctor.bindDate }}</text>
        </view>

        <view class="action-buttons">
          <button class="action-btn primary-btn" @click="sendMessage(doctor)">
            <text class="icon">💬</text> 发送消息
          </button>
          <button class="action-btn outline-btn" @click="contactDoctor(doctor)">
            <text class="icon">📞</text> 联系医生
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Doctor {
  id: number
  name: string
  department: string
  hospital: string
  specialty: string
  bindDate: string
}

const doctors = ref<Doctor[]>([
  {
    id: 1,
    name: '王医生',
    department: '心内科',
    hospital: '北京协和医院',
    specialty: '高血压、冠心病、心律失常',
    bindDate: '2025-06-15'
  },
  {
    id: 2,
    name: '李医生',
    department: '内分泌科',
    hospital: '北京同仁医院',
    specialty: '糖尿病、甲状腺疾病',
    bindDate: '2024-11-20'
  }
])

const goToBindDoctor = () => {
  uni.navigateTo({
    url: '/pages/doctor/bind-doctor'
  })
}

const sendMessage = (doctor: Doctor) => {
  uni.showToast({
    title: `向${doctor.name}发送消息`,
    icon: 'none'
  })
}

const contactDoctor = (doctor: Doctor) => {
  uni.makePhoneCall({
    phoneNumber: '13800000000' // Mock number
  })
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
  box-sizing: border-box;
}

.header-section {
  margin-bottom: 24px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: #1f2937;
}

.subtitle {
  font-size: 14px;
  color: #6b7280;
}

.bind-btn {
  background-color: #0056b3;
  color: white;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  display: flex;
  align-items: center;
  line-height: 1.5;
  margin: 0;
}

.plus-icon {
  margin-right: 4px;
  font-weight: bold;
}

.doctor-card {
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.card-header {
  margin-bottom: 12px;
}

.doctor-name {
  font-size: 18px;
  font-weight: bold;
  color: #111827;
}

.info-row {
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
}

.label {
  color: #6b7280;
  font-size: 14px;
  margin-right: 4px;
  flex-shrink: 0;
}

.info-text {
  color: #4b5563;
  font-size: 14px;
  line-height: 1.5;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  padding: 10px 0;
  border-radius: 8px;
  line-height: 1.5;
  margin: 0;
}

.primary-btn {
  background-color: #0056b3;
  color: white;
  border: none;
}

.primary-btn:active {
  background-color: #004494;
}

.outline-btn {
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.outline-btn:active {
  background-color: #f3f4f6;
}

.icon {
  margin-right: 6px;
  font-size: 16px;
}
</style>
