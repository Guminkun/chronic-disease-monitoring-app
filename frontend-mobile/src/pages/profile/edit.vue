<template>
  <view class="edit-profile-page">
    <PageHeader title="修改个人信息" />
    
    <scroll-view scroll-y class="scroll-container">
      <view class="form-container">
        <!-- 头像 -->
        <view class="avatar-section">
          <text class="section-label">头像</text>
          <view class="avatar-upload">
            <!-- #ifdef MP-WEIXIN -->
            <button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar" :key="avatarKey">
              <image 
                v-if="formData.avatar" 
                :src="formData.avatar + '?t=' + Date.now()" 
                class="avatar-image"
                mode="aspectFill"
                :key="formData.avatar"
              />
              <view v-else class="avatar-placeholder">
                <text class="plus-icon">+</text>
              </view>
            </button>
            <!-- #endif -->
            <!-- #ifndef MP-WEIXIN -->
            <view class="avatar-btn" @click="chooseImage">
              <image 
                v-if="formData.avatar" 
                :src="formData.avatar" 
                class="avatar-image"
                mode="aspectFill"
              />
              <view v-else class="avatar-placeholder">
                <text class="plus-icon">+</text>
              </view>
            </view>
            <!-- #endif -->
          </view>
        </view>
        
        <!-- 昵称 -->
        <view class="form-item">
          <text class="label">昵称</text>
          <!-- #ifdef MP-WEIXIN -->
          <input
            v-model="formData.nickname"
            type="nickname"
            class="input"
            placeholder="点击获取微信昵称"
            @blur="onNicknameChange"
          />
          <!-- #endif -->
          <!-- #ifndef MP-WEIXIN -->
          <input
            v-model="formData.nickname"
            class="input"
            placeholder="请输入昵称"
            maxlength="20"
          />
          <!-- #endif -->
        </view>
        
        <!-- 使用微信信息按钮 -->
        <!-- #ifdef MP-WEIXIN -->
        <view class="wechat-sync-section">
          <button class="sync-btn" @click="getWechatUserProfile">
            <text class="sync-icon">📱</text>
            <text>使用微信头像和昵称</text>
          </button>
        </view>
        <!-- #endif -->
      </view>
    </scroll-view>
    
    <view class="footer-bar">
      <button class="btn-cancel" @click="goBack">取消</button>
      <button class="btn-save" @click="handleSave">保存</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { updateWechatProfile } from '@/api/auth'
import { uploadAvatar } from '@/api/upload'

const userStore = useUserStore()

const formData = ref({
  avatar: '',
  nickname: ''
})

const uploading = ref(false)
const avatarKey = ref(0)

onMounted(async () => {
  await userStore.fetchUserInfo()
  formData.value.avatar = userStore.user?.wechat_avatar || ''
  formData.value.nickname = userStore.user?.wechat_nickname || userStore.user?.name || ''
})

const onChooseAvatar = async (e: any) => {
  const avatarUrl = e.detail.avatarUrl
  if (!avatarUrl) return
  
  uploading.value = true
  uni.showLoading({ title: '上传中...' })
  
  try {
    const result = await uploadAvatar(avatarUrl)
    formData.value.avatar = result.url
    avatarKey.value++
    uni.showToast({ title: '头像上传成功', icon: 'success' })
  } catch (error) {
    console.error('头像上传失败:', error)
    uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
  } finally {
    uploading.value = false
    uni.hideLoading()
  }
}

const chooseImage = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      const tempFilePath = res.tempFilePaths[0]
      uploading.value = true
      uni.showLoading({ title: '上传中...' })
      try {
        const result = await uploadAvatar(tempFilePath)
        formData.value.avatar = result.url
        avatarKey.value++
        uni.showToast({ title: '头像上传成功', icon: 'success' })
      } catch (error) {
        console.error('头像上传失败:', error)
        uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
      } finally {
        uploading.value = false
        uni.hideLoading()
      }
    }
  })
}

const onNicknameChange = (e: any) => {
  if (e.detail.value) {
    formData.value.nickname = e.detail.value
  }
}

const getWechatUserProfile = () => {
  uni.getUserProfile({
    desc: '用于完善用户资料',
    success: async (res) => {
      formData.value.nickname = res.userInfo.nickName
      
      uploading.value = true
      uni.showLoading({ title: '上传头像中...' })
      try {
        const result = await uploadAvatar(res.userInfo.avatarUrl)
        formData.value.avatar = result.url
        avatarKey.value++
        uni.showToast({ title: '获取成功', icon: 'success' })
      } catch (error) {
        console.error('头像上传失败:', error)
        uni.showToast({ title: '头像上传失败', icon: 'none' })
      } finally {
        uploading.value = false
        uni.hideLoading()
      }
    },
    fail: () => {
      uni.showToast({ title: '获取失败', icon: 'none' })
    }
  })
}

const handleSave = async () => {
  try {
    uni.showLoading({ title: '保存中' })
    
    await updateWechatProfile({
      nickname: formData.value.nickname,
      avatar: formData.value.avatar
    })
    
    await userStore.fetchUserInfo()
    
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 800)
  } catch (e: any) {
    uni.showToast({ title: e.detail || '保存失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

const goBack = () => {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.edit-profile-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.scroll-container {
  flex: 1;
  padding: 16px;
}

.form-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 20px;
  
  .section-label {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 16px;
  }
  
  .avatar-upload {
    .avatar-btn {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: none;
      border: none;
      padding: 0;
      overflow: hidden;
      
      &::after {
        border: none;
      }
    }
    
    .avatar-image {
      width: 80px;
      height: 80px;
      border-radius: 50%;
    }
    
    .avatar-placeholder {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background-color: #f1f5f9;
      border: 2px dashed #cbd5e1;
      display: flex;
      align-items: center;
      justify-content: center;
      
      .plus-icon {
        font-size: 32px;
        color: #94a3b8;
      }
    }
  }
}

.form-item {
  margin-bottom: 20px;
  
  .label {
    display: block;
    font-size: 14px;
    color: #64748b;
    margin-bottom: 8px;
  }
  
  .input {
    width: 100%;
    height: 44px;
    background-color: #f8fafc;
    border-radius: 8px;
    padding: 0 16px;
    font-size: 16px;
  }
}

.wechat-sync-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
  
  .sync-btn {
    width: 100%;
    height: 44px;
    background: linear-gradient(135deg, #07C160 0%, #06AD56 100%);
    border-radius: 22px;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-size: 16px;
    
    .sync-icon {
      margin-right: 8px;
    }
  }
}

.footer-bar {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: #ffffff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  
  .btn-cancel, .btn-save {
    flex: 1;
    height: 44px;
    border-radius: 22px;
    font-size: 16px;
    border: none;
  }
  
  .btn-cancel {
    background-color: #f1f5f9;
    color: #64748b;
  }
  
  .btn-save {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: #ffffff;
  }
}
</style>
