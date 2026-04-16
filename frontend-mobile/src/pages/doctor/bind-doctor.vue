<template>
  <view class="page-container">
    <!-- Generate Binding Code Section -->
    <view class="section-card">
      <view class="section-header center-align">
        <text class="section-title">生成绑定码</text>
      </view>
      
      <text class="description-text">医生可以通过扫描二维码或输入验证码与您建立绑定</text>
      
      <!-- Mock QR Code -->
      <view class="qr-container">
        <view class="qr-box">
          <text class="qr-label">模拟 QR 码</text>
          <text class="qr-code-large">{{ bindingCode }}</text>
        </view>
      </view>
      
      <view class="code-info">
        <text class="info-line">医生扫描码或输入验证码：<text class="highlight-code">{{ bindingCode }}</text></text>
        <text class="info-line">有效期：24小时</text>
      </view>
      
      <button class="regenerate-btn" @click="regenerateCode">重新生成</button>
    </view>

    <!-- Bound Doctors Section -->
    <view class="section-card">
      <view class="section-header">
        <text class="section-title">已绑定的医生</text>
      </view>
      
      <text class="count-text">共 {{ doctors.length }} 位医生</text>
      
      <view v-for="(doctor, index) in doctors" :key="index" class="compact-doctor-card">
        <view class="card-top">
          <view class="doctor-info">
            <text class="name">{{ doctor.name }}</text>
            <text class="hospital-info">{{ doctor.department }} • {{ doctor.hospital }}</text>
            <text class="specialty-text">{{ doctor.specialty }}</text>
          </view>
          <view class="remove-action" @click="removeDoctor(index)">
            <text class="remove-icon">🗑️</text>
            <text class="remove-text">移除</text>
          </view>
        </view>
        
        <view class="card-actions">
          <button class="small-btn primary" @click="chatWithDoctor(doctor)">
            <text class="btn-icon">💬</text> 沟通
          </button>
          <button class="small-btn outline" @click="callDoctor(doctor)">
            <text class="btn-icon">📞</text> 拨号
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const bindingCode = ref('A8K9X')

const doctors = ref([
  {
    id: 1,
    name: '王医生',
    department: '心内科',
    hospital: '北京协和医院',
    specialty: '高血压、冠心病'
  }
])

const regenerateCode = () => {
  // Generate a random 5-char code for demo
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let result = ''
  for (let i = 0; i < 5; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  bindingCode.value = result
  uni.showToast({ title: '已刷新验证码', icon: 'none' })
}

const removeDoctor = (index: number) => {
  uni.showModal({
    title: '确认移除',
    content: '确定要解除与该医生的绑定吗？',
    success: (res) => {
      if (res.confirm) {
        doctors.value.splice(index, 1)
        uni.showToast({ title: '已移除', icon: 'success' })
      }
    }
  })
}

const chatWithDoctor = (doctor: any) => {
  uni.showToast({ title: `与${doctor.name}沟通`, icon: 'none' })
}

const callDoctor = (doctor: any) => {
  uni.makePhoneCall({ phoneNumber: '13800000000' })
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e5e7eb;
}

.section-header {
  margin-bottom: 16px;
}

.center-align {
  text-align: center;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #111827;
}

.description-text {
  font-size: 14px;
  color: #6b7280;
  text-align: center;
  margin-bottom: 24px;
  display: block;
}

/* QR Code Area */
.qr-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.qr-box {
  width: 200px;
  height: 200px;
  border: 4px solid #0056b3;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
}

.qr-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
}

.qr-code-large {
  font-size: 32px;
  font-weight: bold;
  color: #0056b3;
  letter-spacing: 2px;
}

.code-info {
  text-align: center;
  margin-bottom: 24px;
}

.info-line {
  display: block;
  font-size: 14px;
  color: #4b5563;
  margin-bottom: 4px;
}

.highlight-code {
  font-weight: bold;
  color: #111827;
}

.regenerate-btn {
  background-color: white;
  border: 1px solid #d1d5db;
  color: #374151;
  font-size: 14px;
  border-radius: 8px;
  padding: 10px 0;
}

.regenerate-btn:active {
  background-color: #f3f4f6;
}

/* Bound Doctors List */
.count-text {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 16px;
  display: block;
}

.compact-doctor-card {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.doctor-info {
  flex: 1;
}

.name {
  font-size: 16px;
  font-weight: bold;
  color: #111827;
  display: block;
  margin-bottom: 4px;
}

.hospital-info {
  font-size: 12px;
  color: #6b7280;
  display: block;
  margin-bottom: 8px;
}

.specialty-text {
  font-size: 12px;
  color: #9ca3af;
  display: block;
}

.remove-action {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background-color: white;
  border: 1px solid #fee2e2;
  border-radius: 4px;
}

.remove-action:active {
  background-color: #fef2f2;
}

.remove-icon {
  font-size: 12px;
  margin-right: 4px;
}

.remove-text {
  font-size: 12px;
  color: #ef4444;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.small-btn {
  flex: 1;
  font-size: 13px;
  padding: 8px 0;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1.4;
  margin: 0;
}

.btn-icon {
  margin-right: 4px;
  font-size: 14px;
}

.small-btn.primary {
  background-color: #0056b3;
  color: white;
  border: none;
}

.small-btn.primary:active {
  background-color: #004494;
}

.small-btn.outline {
  background-color: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.small-btn.outline:active {
  background-color: #f3f4f6;
}
</style>
