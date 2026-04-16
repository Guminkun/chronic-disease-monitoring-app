<template>
  <view class="container">
    <view class="section-title">我的医生</view>
    
    <!-- Doctor List -->
    <view v-if="doctors.length > 0" class="doctor-list">
      <view v-for="binding in doctors" :key="binding.id" class="doctor-card" @click="navigateToChat(binding.doctor)">
        <view class="doctor-info" v-if="binding.doctor">
          <text class="doctor-name">{{ binding.doctor.name }}</text>
          <text class="doctor-hospital">{{ binding.doctor.hospital }} - {{ binding.doctor.department }}</text>
        </view>
        <view class="right-actions">
          <view class="icon-chat">💬</view>
          <view class="status-tag active">
            <text>已绑定</text>
          </view>
        </view>
      </view>
    </view>
    
    <view v-else class="empty-state">
      <text class="empty-text">暂无绑定医生</text>
    </view>

    <!-- Bind New Doctor Section -->
    <view class="bind-section">
      <button class="primary-btn" @click="handleGenerateCode" :disabled="!!code">
        {{ code ? '绑定码已生成' : '绑定新医生' }}
      </button>
      
      <view v-if="code" class="code-display">
        <text class="code-label">请向医生出示以下验证码</text>
        <text class="code-value">{{ code }}</text>
        <text class="code-timer">有效期剩余: {{ timer }}秒</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { getMyDoctors, generateBindingCode } from '../../api/patient'

const doctors = ref<any[]>([])
const code = ref('')
const timer = ref(0)
let intervalId: any = null

const navigateToChat = (doctor: any) => {
  if (doctor && doctor.user_id) {
    uni.navigateTo({
      url: `/pages/chat/chat?id=${doctor.user_id}&name=${doctor.name}`
    })
  } else {
    uni.showToast({ title: '无法获取医生信息', icon: 'none' })
  }
}

const fetchDoctors = async () => {
  try {
    const res: any = await getMyDoctors()
    doctors.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (error) {
    console.error('Failed to fetch doctors', error)
  }
}

const handleGenerateCode = async () => {
  try {
    const res: any = await generateBindingCode()
    code.value = res?.code || ''
    timer.value = Number(res?.expires_in || 0)
    
    if (intervalId) clearInterval(intervalId)
    intervalId = setInterval(() => {
      if (timer.value > 0) {
        timer.value--
      } else {
        code.value = ''
        clearInterval(intervalId)
      }
    }, 1000)
  } catch (error) {
    uni.showToast({ title: '生成失败', icon: 'none' })
  }
}

onMounted(() => {
  fetchDoctors()
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}
.doctor-card {
  background: white;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.doctor-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}
.doctor-hospital {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}
.right-actions {
  display: flex;
  align-items: center;
}
.icon-chat {
  margin-right: 12px;
  font-size: 20px;
}
.status-tag {
  background-color: #e6f7ff;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.empty-state {
  text-align: center;
  padding: 30px;
  color: #999;
}
.bind-section {
  margin-top: 30px;
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}
.primary-btn {
  background-color: #1890ff;
  color: white;
  border-radius: 20px;
  font-size: 16px;
  width: 100%;
}
.code-display {
  margin-top: 20px;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px dashed #1890ff;
}
.code-label {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 10px;
}
.code-value {
  font-size: 32px;
  font-weight: bold;
  color: #1890ff;
  letter-spacing: 4px;
  display: block;
  margin-bottom: 10px;
}
.code-timer {
  font-size: 12px;
  color: #999;
}
</style>
