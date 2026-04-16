<template>
  <view class="add-member-page">
    <scroll-view scroll-y class="scroll-container">
      <view class="form-container">
        <view class="form-section">
          <view class="section-title">
            <text class="required-mark">*</text>
            <text>基本信息</text>
          </view>
          
          <view class="avatar-section">
            <view class="avatar-upload" @click="chooseAvatar">
              <image 
                v-if="formData.avatar_url" 
                :src="formData.avatar_url" 
                class="avatar-preview" 
                mode="aspectFill"
              />
              <view v-else class="avatar-placeholder-add">
                <text class="avatar-add-icon">+</text>
                <text class="avatar-add-text">添加头像</text>
              </view>
            </view>
          </view>
          
          <view class="form-item">
            <text class="label"><text class="required-mark">*</text>昵称</text>
            <input
              v-model="formData.nickname"
              class="input"
              placeholder="请输入昵称"
              maxlength="20"
            />
          </view>
          
          <view class="form-item">
            <text class="label"><text class="required-mark">*</text>关系</text>
            <picker
              v-if="!isCustomRelation"
              mode="selector"
              :range="relationOptions"
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

        <view v-if="!showExtended" class="extend-btn" @click="showExtended = true">
          <text class="extend-icon">▼</text>
          <text class="extend-text">继续完善档案</text>
        </view>

        <view v-if="showExtended" class="form-section extended">
          <view class="section-header">
            <text class="section-title">档案信息</text>
            <text class="optional-mark">（选填）</text>
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

import { ref, computed } from 'vue'
import { useMemberStore } from '@/stores/member'
import { useUserStore } from '@/stores/user'
import { uploadAvatar } from '@/api/member'
import type { MemberFormData } from '@/api/member'

const memberStore = useMemberStore()
const userStore = useUserStore()

const showExtended = ref(false)
const isCustomRelation = ref(false)
const avatarUploading = ref(false)

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

const chooseAvatar = () => {
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
        uni.showToast({ title: '头像上传失败', icon: 'none' })
      } finally {
        avatarUploading.value = false
        uni.hideLoading()
      }
    },
    fail: () => {
      uni.showToast({ title: '取消选择', icon: 'none' })
    }
  })
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
  
  const newMember = await memberStore.addMember(submitData)
  
  if (newMember) {
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  }
}
</script>

<style scoped>
.add-member-page {
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

.optional-mark {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 400;
}

.required-mark {
  color: #ef4444;
  font-size: 16px;
}

.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-upload {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px dashed #7dd3fc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-preview {
  width: 100%;
  height: 100%;
}

.avatar-placeholder-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.avatar-add-icon {
  font-size: 28px;
  color: #0ea5e9;
  font-weight: 300;
}

.avatar-add-text {
  font-size: 12px;
  color: #0ea5e9;
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

.extend-btn {
  background: #ffffff;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 12px rgba(100, 120, 200, 0.06);
  transition: all 0.3s;
  box-sizing: border-box;
}

.extend-btn:active {
  transform: scale(0.98);
  background: #f8faff;
}

.extend-icon {
  font-size: 14px;
  color: #0ea5e9;
}

.extend-text {
  font-size: 15px;
  color: #0ea5e9;
  font-weight: 600;
}

.form-section.extended {
  border-top: 3px solid #0ea5e9;
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
