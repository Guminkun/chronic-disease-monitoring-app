<template>
  <view class="edit-member-page">
    <scroll-view scroll-y class="scroll-container">
      <view class="form-container">
        <!-- 头像上传 -->
        <view class="avatar-section">
          <!-- #ifdef MP-WEIXIN -->
          <button class="avatar-btn" open-type="chooseAvatar" @chooseavatar="onChooseAvatar" :key="avatarKey">
            <image 
              v-if="formData.avatar_url" 
              :src="formData.avatar_url" 
              class="avatar-image"
              mode="aspectFill"
              :key="formData.avatar_url"
            />
            <view v-else class="avatar-placeholder">
              <text class="plus-icon">+</text>
              <text class="avatar-text">上传头像</text>
            </view>
          </button>
          <!-- #endif -->
          <!-- #ifndef MP-WEIXIN -->
          <view class="avatar-btn" @click="chooseImage">
            <image 
              v-if="formData.avatar_url" 
              :src="formData.avatar_url" 
              class="avatar-image"
              mode="aspectFill"
            />
            <view v-else class="avatar-placeholder">
              <text class="plus-icon">+</text>
              <text class="avatar-text">上传头像</text>
            </view>
          </view>
          <!-- #endif -->
        </view>
        
        <view class="form-section">
          <view class="section-title">
            <text class="required-mark">*</text>
            <text>基本信息</text>
          </view>
          
          <view class="form-item">
            <text class="label"><text class="required-mark">*</text>昵称</text>
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
          
          <view class="form-item">
            <text class="label"><text class="required-mark">*</text>关系</text>
            <picker
              v-if="!isCustomRelation"
              mode="selector"
              :range="relationOptions"
              :value="relationIndex"
              @change="onRelationChange"
            >
              <view class="picker">
                <text :class="{ placeholder: !formData.relation }">
                  {{ formData.relation || '请选择关系' }}
                </text>
                <text class="arrow">›</text>
              </view>
            </picker>
            <view v-else class="custom-relation-wrap">
              <input
                v-model="formData.relation"
                class="input"
                placeholder="请输入关系"
                maxlength="20"
              />
              <view class="reset-btn" @click="resetRelation">
                <text>重选</text>
              </view>
            </view>
          </view>
        </view>

        <view class="form-section">
          <view class="section-header">
            <text class="section-title">档案信息</text>
          </view>
          
          <view class="form-item">
            <text class="label">年龄</text>
            <input
              v-model.number="formData.age"
              type="number"
              class="input"
              placeholder="请输入年龄"
            />
          </view>
          
          <view class="form-item">
            <text class="label">性别</text>
            <picker
              mode="selector"
              :range="genderLabels"
              :value="genderIndex"
              @change="onGenderChange"
            >
              <view class="picker">
                <text :class="{ placeholder: !formData.gender }">
                  {{ formData.gender ? genderLabels[genderOptions.indexOf(formData.gender)] : '请选择性别' }}
                </text>
                <text class="arrow">›</text>
              </view>
            </picker>
          </view>
          
          <view class="form-item">
            <text class="label">身高 (cm)</text>
            <input
              v-model.number="formData.height"
              type="digit"
              class="input"
              placeholder="请输入身高"
            />
          </view>
          
          <view class="form-item">
            <text class="label">体重 (kg)</text>
            <input
              v-model.number="formData.weight"
              type="digit"
              class="input"
              placeholder="请输入体重"
            />
          </view>
          
          <view class="form-item">
            <text class="label">血型</text>
            <picker
              mode="selector"
              :range="bloodTypeOptions"
              :value="bloodTypeIndex"
              @change="onBloodTypeChange"
            >
              <view class="picker">
                <text :class="{ placeholder: !formData.blood_type }">
                  {{ formData.blood_type || '请选择血型' }}
                </text>
                <text class="arrow">›</text>
              </view>
            </picker>
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">生活习惯</text>
            <textarea
              v-model="formData.lifestyle"
              class="textarea"
              placeholder="请输入生活习惯（如：吸烟、饮酒等）"
              maxlength="200"
            />
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">过敏史</text>
            <textarea
              v-model="formData.allergy_history"
              class="textarea"
              placeholder="请输入过敏史"
              maxlength="200"
            />
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">既往病史</text>
            <textarea
              v-model="formData.past_history"
              class="textarea"
              placeholder="请输入既往病史"
              maxlength="200"
            />
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">家族史</text>
            <textarea
              v-model="formData.family_history"
              class="textarea"
              placeholder="请输入家族病史"
              maxlength="200"
            />
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">手术史</text>
            <textarea
              v-model="formData.surgery_history"
              class="textarea"
              placeholder="请输入手术史"
              maxlength="200"
            />
          </view>
          
          <view class="form-item textarea-item">
            <text class="label">其他补充</text>
            <textarea
              v-model="formData.other_notes"
              class="textarea"
              placeholder="请输入其他补充信息"
              maxlength="300"
            />
          </view>
        </view>

        <view class="button-container">
          <view class="save-button" @click="handleSave">
            <text>保存</text>
          </view>
        </view>
        
        <view class="bottom-space"></view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'

const goBack = () => {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useMemberStore } from '@/stores/member'
import { useUserStore } from '@/stores/user'
import { uploadAvatar } from '@/api/member'
import type { MemberFormData } from '@/api/member'

const memberStore = useMemberStore()
const userStore = useUserStore()

const memberId = ref('')
const isCustomRelation = ref(false)
const avatarUploading = ref(false)
const avatarKey = ref(0)
const formData = ref<MemberFormData>({
  nickname: '',
  relation: '',
  avatar_url: '',
  age: '',
  gender: '',
  height: '',
  weight: '',
  blood_type: '',
  lifestyle: '',
  allergy_history: '',
  past_history: '',
  family_history: '',
  surgery_history: '',
  other_notes: ''
})

const relationOptions = [
  '自己',
  '父亲',
  '母亲',
  '丈夫',
  '妻子',
  '儿子',
  '女儿',
  '爷爷',
  '奶奶',
  '外公',
  '外婆',
  '自定义'
]

const genderOptions = ['male', 'female']
const genderLabels = ['男', '女']
const bloodTypeOptions = ['A型', 'B型', 'AB型', 'O型', '不详']

const relationIndex = computed(() => {
  const idx = relationOptions.indexOf(formData.value.relation)
  return idx >= 0 ? idx : 0
})

const genderIndex = computed(() => {
  return genderOptions.indexOf(formData.value.gender || '')
})

const bloodTypeIndex = computed(() => {
  return bloodTypeOptions.indexOf(formData.value.blood_type || '')
})

onLoad((options: any) => {
  if (options.id) {
    memberId.value = options.id
    loadMemberData()
  }
})

const loadMemberData = async () => {
  const member = memberStore.members.find(m => m.id === memberId.value)
  if (member) {
    const isPresetRelation = relationOptions.includes(member.relation)
    isCustomRelation.value = !isPresetRelation
    formData.value = {
      nickname: member.nickname,
      relation: member.relation,
      avatar_url: member.avatar_url || '',
      age: member.age || '',
      gender: member.gender || '',
      height: member.height || '',
      weight: member.weight || '',
      blood_type: member.blood_type || '',
      lifestyle: member.lifestyle || '',
      allergy_history: member.allergy_history || '',
      past_history: member.past_history || '',
      family_history: member.family_history || '',
      surgery_history: member.surgery_history || '',
      other_notes: member.other_notes || ''
    }
  }
}

const onChooseAvatar = async (e: any) => {
  const avatarUrl = e.detail.avatarUrl
  if (!avatarUrl) return
  
  avatarUploading.value = true
  uni.showLoading({ title: '上传中...' })
  
  try {
    const result = await uploadAvatar(avatarUrl)
    formData.value.avatar_url = result.url
    avatarKey.value++
    uni.showToast({ title: '头像上传成功', icon: 'success' })
  } catch (error) {
    console.error('头像上传失败:', error)
    uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
  } finally {
    avatarUploading.value = false
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
      avatarUploading.value = true
      uni.showLoading({ title: '上传中...' })
      try {
        const result = await uploadAvatar(tempFilePath)
        formData.value.avatar_url = result.url
        uni.showToast({ title: '头像上传成功', icon: 'success' })
      } catch (error) {
        console.error('头像上传失败:', error)
        uni.showToast({ title: '头像上传失败，请重试', icon: 'none' })
      } finally {
        avatarUploading.value = false
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

const onRelationChange = (e: any) => {
  const index = e.detail.value
  const selected = relationOptions[index]
  if (selected === '自定义') {
    isCustomRelation.value = true
    formData.value.relation = ''
  } else {
    isCustomRelation.value = false
    formData.value.relation = selected
  }
}

const resetRelation = () => {
  isCustomRelation.value = false
  formData.value.relation = ''
}

const onGenderChange = (e: any) => {
  const index = e.detail.value
  formData.value.gender = genderOptions[index]
}

const onBloodTypeChange = (e: any) => {
  const index = e.detail.value
  formData.value.blood_type = bloodTypeOptions[index]
}

const handleSave = async () => {
  if (!userStore.token) {
    uni.showToast({
      title: '请先登录',
      icon: 'none'
    })
    setTimeout(() => {
      safeNavigate({ url: '/pages/login/login' })
    }, 1500)
    return
  }
  
  if (!formData.value.nickname.trim()) {
    uni.showToast({
      title: '请输入昵称',
      icon: 'none'
    })
    return
  }
  
  if (!formData.value.relation || !formData.value.relation.trim()) {
    uni.showToast({
      title: isCustomRelation.value ? '请输入关系' : '请选择关系',
      icon: 'none'
    })
    return
  }
  
  const submitData: any = {
    nickname: formData.value.nickname.trim(),
    relation: formData.value.relation.trim()
  }
  
  if (formData.value.avatar_url) {
    submitData.avatar_url = formData.value.avatar_url
  }
  
  if (formData.value.age !== '' && formData.value.age !== null && formData.value.age !== undefined) {
    submitData.age = formData.value.age
  }
  if (formData.value.gender) {
    submitData.gender = formData.value.gender
  }
  if (formData.value.height !== '' && formData.value.height !== null && formData.value.height !== undefined) {
    submitData.height = formData.value.height
  }
  if (formData.value.weight !== '' && formData.value.weight !== null && formData.value.weight !== undefined) {
    submitData.weight = formData.value.weight
  }
  if (formData.value.blood_type) {
    submitData.blood_type = formData.value.blood_type
  }
  if (formData.value.lifestyle) {
    submitData.lifestyle = formData.value.lifestyle
  }
  if (formData.value.allergy_history) {
    submitData.allergy_history = formData.value.allergy_history
  }
  if (formData.value.past_history) {
    submitData.past_history = formData.value.past_history
  }
  if (formData.value.family_history) {
    submitData.family_history = formData.value.family_history
  }
  if (formData.value.surgery_history) {
    submitData.surgery_history = formData.value.surgery_history
  }
  if (formData.value.other_notes) {
    submitData.other_notes = formData.value.other_notes
  }
  
  const updatedMember = await memberStore.editMember(memberId.value, submitData)
  
  if (updatedMember) {
    await memberStore.loadMembers()
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  }
}
</script>

<style lang="scss" scoped>
.edit-member-page {
  min-height: 100vh;
  background: #f0f4ff;
}

.scroll-container {
  height: 100vh;
}

.form-container {
  padding: 16px;
  box-sizing: border-box;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  
  .avatar-btn {
    width: 100px;
    height: 100px;
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
    width: 100px;
    height: 100px;
    border-radius: 50%;
  }
  
  .avatar-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background-color: #f1f5f9;
    border: 2px dashed #cbd5e1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    
    .plus-icon {
      font-size: 32px;
      color: #94a3b8;
    }
    
    .avatar-text {
      font-size: 12px;
      color: #94a3b8;
      margin-top: 4px;
    }
  }
}

.form-section {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px rgba(100, 120, 200, 0.06);
  box-sizing: border-box;
  overflow: hidden;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.required-mark {
  color: #ef4444;
  font-size: 16px;
}

.form-item {
  margin-bottom: 16px;
  box-sizing: border-box;
}

.form-item:last-child {
  margin-bottom: 0;
}

.label {
  display: block;
  font-size: 14px;
  color: #475569;
  margin-bottom: 8px;
  font-weight: 500;
}

.input {
  width: 100%;
  height: 44px;
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 0 14px;
  font-size: 15px;
  color: #1e293b;
  box-sizing: border-box;
}

.input:focus {
  border-color: #0ea5e9;
  background: #ffffff;
}

.picker {
  width: 100%;
  height: 44px;
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.picker text {
  font-size: 15px;
  color: #1e293b;
}

.picker .placeholder {
  color: #94a3b8;
}

.picker .arrow {
  font-size: 18px;
  color: #cbd5e1;
}

.custom-relation-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
}

.custom-relation-wrap .input {
  flex: 1;
  min-width: 0;
}

.reset-btn {
  background: #f1f5f9;
  border-radius: 10px;
  padding: 8px 14px;
  flex-shrink: 0;
}

.reset-btn text {
  font-size: 13px;
  color: #64748b;
}

.textarea-item .textarea {
  width: 100%;
  min-height: 80px;
  background: #f8faff;
  border: 1.5px solid #e8eeff;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 15px;
  color: #1e293b;
  line-height: 1.5;
  box-sizing: border-box;
}

.button-container {
  padding: 16px 0;
}

.save-button {
  background: linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%);
  border-radius: 16px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.3);
  transition: all 0.3s;
}

.save-button:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.save-button text {
  font-size: 16px;
  color: white;
  font-weight: 600;
}

.bottom-space {
  height: 40px;
}
</style>
