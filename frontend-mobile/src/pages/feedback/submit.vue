<template>
  <view class="container">
    <!-- 反馈内容输入 -->
    <view class="section">
      <view class="section-title">反馈内容</view>
      <textarea 
        class="content-input" 
        v-model="content" 
        placeholder="请详细描述您的问题或建议，我们将认真对待每一条反馈..."
        :maxlength="2000"
        auto-height
      />
      <view class="word-count">{{ content.length }}/2000</view>
    </view>

    <!-- 图片上传 -->
    <view class="section">
      <view class="section-title">上传图片（可选）</view>
      <view class="image-upload">
        <view class="image-list">
          <view class="image-item" v-for="(img, index) in imageList" :key="index">
            <image :src="img" mode="aspectFill" @click="previewImage(index)" />
            <view class="delete-btn" @click="removeImage(index)">×</view>
          </view>
          <view class="upload-btn" v-if="imageList.length < 4" @click="chooseImage">
            <text class="plus">+</text>
            <text class="text">添加图片</text>
          </view>
        </view>
        <view class="tip">最多上传4张图片</view>
      </view>
    </view>

    <!-- 联系方式 -->
    <view class="section">
      <view class="section-title">联系方式（可选）</view>
      <input 
        class="contact-input" 
        v-model="contact" 
        placeholder="请输入手机号或邮箱，方便我们回复您"
        :maxlength="100"
      />
    </view>

    <!-- 提交按钮 -->
    <view class="submit-section">
      <button class="btn-submit" :disabled="!canSubmit || submitting" @click="handleSubmit">
        {{ submitting ? '提交中...' : '提交反馈' }}
      </button>
    </view>

    <!-- 历史反馈入口 -->
    <view class="history-link" @click="goToHistory">
      <text>查看我的反馈记录</text>
      <text class="arrow">></text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed } from 'vue'
import { submitFeedback } from '@/api/feedback'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const content = ref('')
const imageList = ref<string[]>([])
const contact = ref('')
const submitting = ref(false)

const canSubmit = computed(() => {
  return content.value.trim().length > 0
})

// 选择图片
const chooseImage = () => {
  uni.chooseImage({
    count: 4 - imageList.value.length,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      // 这里暂时使用本地路径，实际项目中需要上传到服务器
      imageList.value = [...imageList.value, ...res.tempFilePaths]
    }
  })
}

// 预览图片
const previewImage = (index: number) => {
  uni.previewImage({
    urls: imageList.value,
    current: index
  })
}

// 删除图片
const removeImage = (index: number) => {
  imageList.value.splice(index, 1)
}

// 提交反馈
const handleSubmit = async () => {
  if (!userStore.token) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    safeNavigate({ url: '/pages/login/login' })
    return
  }

  if (!content.value.trim()) {
    uni.showToast({ title: '请输入反馈内容', icon: 'none' })
    return
  }

  submitting.value = true
  
  try {
    // 实际项目中需要先上传图片获取URL
    // 这里暂时传递空数组
    await submitFeedback({
      content: content.value.trim(),
      images: imageList.value.length > 0 ? imageList.value : undefined,
      contact: contact.value.trim() || undefined
    })
    
    uni.showToast({ title: '提交成功', icon: 'success' })
    
    // 清空表单
    content.value = ''
    imageList.value = []
    contact.value = ''
    
    // 延迟跳转到历史记录页
    setTimeout(() => {
      safeNavigate({ url: '/pages/feedback/history' })
    }, 1500)
  } catch (error) {
    console.error('提交反馈失败:', error)
  } finally {
    submitting.value = false
  }
}

// 查看历史反馈
const goToHistory = () => {
  if (!userStore.token) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    safeNavigate({ url: '/pages/login/login' })
    return
  }
  safeNavigate({ url: '/pages/feedback/history' })
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 16px;
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden;
}

.section {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-sizing: border-box;
  width: 100%;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.content-input {
  width: 100%;
  min-height: 150px;
  font-size: 15px;
  color: #334155;
  line-height: 1.6;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-sizing: border-box;
}

.word-count {
  text-align: right;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.image-upload {
  margin-top: 8px;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.image-item {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.image-item image {
  width: 100%;
  height: 100%;
}

.delete-btn {
  position: absolute;
  top: 0;
  right: 0;
  width: 24px;
  height: 24px;
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 0 0 8px;
}

.upload-btn {
  width: 80px;
  height: 80px;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f8fafc;
  flex-shrink: 0;
  box-sizing: border-box;
}

.upload-btn .plus {
  font-size: 28px;
  color: #94a3b8;
  line-height: 1;
}

.upload-btn .text {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.contact-input {
  width: 100%;
  height: 44px;
  font-size: 15px;
  color: #334155;
  padding: 0 12px;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-sizing: border-box;
}

.submit-section {
  margin-top: 24px;
  width: 100%;
  box-sizing: border-box;
}

.btn-submit {
  width: 100%;
  height: 48px;
  background-color: #3b82f6;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  box-sizing: border-box;
}

.btn-submit[disabled] {
  background-color: #94a3b8;
}

.history-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin-top: 24px;
  background-color: #ffffff;
  border-radius: 12px;
  box-sizing: border-box;
  width: 100%;
}

.history-link text:first-child {
  font-size: 15px;
  color: #3b82f6;
}

.history-link .arrow {
  color: #cbd5e1;
  font-size: 14px;
}
</style>
