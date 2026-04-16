<template>
  <view class="page-container">
    <!-- 内容区域 -->
    <scroll-view scroll-y class="page-content">
      <!-- 空状态 -->
      <view v-if="diseases.length === 0" class="empty-state">
        <view class="empty-icon">
          <text>📋</text>
        </view>
        <text class="empty-title">暂无慢性病记录</text>
        <text class="empty-desc">点击下方"添加慢病"按钮添加</text>
      </view>

      <!-- 疾病列表 -->
      <view v-else class="disease-list">
        <view 
          v-for="item in diseases" 
          :key="item.id" 
          class="disease-card"
        >
          <!-- 卡片头部 -->
          <view class="card-header">
            <view class="disease-icon">
              <text>{{ getDiseaseIcon(item.name) }}</text>
            </view>
            <view class="disease-info">
              <text class="disease-name">{{ item.name }}</text>
              <view class="diagnosis-date">
                <text class="date-label">确诊日期</text>
                <text class="date-value">{{ item.diagnosis_date || '未设置' }}</text>
              </view>
            </view>
          </view>

          <!-- 卡片详情 -->
          <view class="card-details" v-if="item.hospital || item.notes">
            <view class="detail-row" v-if="item.hospital">
              <text class="detail-label">确诊医院</text>
              <text class="detail-value">{{ item.hospital }}</text>
            </view>
            <view class="detail-row" v-if="item.notes">
              <text class="detail-label">备注</text>
              <text class="detail-value">{{ item.notes }}</text>
            </view>
          </view>

          <!-- 卡片操作 -->
          <view class="card-actions">
            <view class="action-btn edit" @click.stop="openEdit(item)">
              <text class="btn-text">编辑</text>
            </view>
            <view class="action-btn delete" @click.stop="handleDelete(item)">
              <text class="btn-text">删除</text>
            </view>
          </view>
        </view>
      </view>

      <view class="page-bottom" />
    </scroll-view>

    <!-- 添加/编辑弹窗 -->
    <view v-if="showModal" class="modal-mask" @click="closeEdit">
      <view class="modal-sheet" @click.stop>
        <!-- 弹窗头部 -->
        <view class="sheet-header">
          <view class="sheet-handle" />
          <view class="sheet-title-row">
            <text class="sheet-title">{{ isEditing ? '编辑慢性病' : '添加慢性病' }}</text>
            <view class="sheet-close" @click="closeEdit">
              <text>✕</text>
            </view>
          </view>
        </view>

        <!-- 表单内容 -->
        <scroll-view scroll-y class="sheet-body">
          <!-- 疾病名称 -->
          <view class="form-section">
            <text class="section-label">慢性病名称 *</text>
            <view class="input-field" @click="openSearch">
              <text class="field-value" :class="{ placeholder: !form.name }">
                {{ form.name || '点击选择或输入疾病名称' }}
              </text>
              <text class="field-arrow">›</text>
            </view>
            <!-- 快捷标签 -->
            <view class="quick-select">
              <text class="quick-label">快捷选择</text>
              <view class="quick-tags">
                <view 
                  v-for="tag in commonDiseases" 
                  :key="tag" 
                  class="quick-tag"
                  :class="{ selected: form.name === tag }"
                  @click="form.name = tag"
                >
                  <text>{{ tag }}</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 确诊日期 -->
          <view class="form-section">
            <text class="section-label">确诊日期</text>
            <picker mode="date" :value="form.diagnosis_date" @change="onDateChange">
              <view class="input-field">
                <text class="field-value" :class="{ placeholder: !form.diagnosis_date }">
                  {{ form.diagnosis_date || '请选择日期' }}
                </text>
                <text class="field-icon">📅</text>
              </view>
            </picker>
          </view>

          <!-- 确诊医院 -->
          <view class="form-section">
            <text class="section-label">确诊医院</text>
            <view class="input-field" @click="openHospitalSearch">
              <text class="field-value" :class="{ placeholder: !form.hospital }">
                {{ form.hospital || '点击选择或输入医院名称' }}
              </text>
              <text class="field-arrow">›</text>
            </view>
          </view>

          <!-- 备注 -->
          <view class="form-section">
            <text class="section-label">备注信息</text>
            <view class="textarea-field">
              <textarea 
                class="field-textarea" 
                v-model="form.notes" 
                placeholder="请输入相关备注信息"
                placeholder-class="field-placeholder"
              />
            </view>
          </view>
        </scroll-view>

        <!-- 弹窗底部 -->
        <view class="sheet-footer">
          <view class="footer-btn cancel" @click="closeEdit">
            <text>取消</text>
          </view>
          <view class="footer-btn confirm" @click="saveEdit">
            <text>{{ isEditing ? '保存修改' : '确认添加' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 搜索弹窗 -->
    <view v-if="showSearch" class="modal-mask" @click="showSearch = false">
      <view class="search-sheet" @click.stop>
        <view class="search-header">
          <input 
            class="search-input" 
            v-model="searchQuery" 
            placeholder="输入诊断名称或疾病名称"
            focus
          />
          <text class="search-cancel" @click="showSearch = false">取消</text>
        </view>

        <scroll-view scroll-y class="search-content">
          <!-- 加载中 -->
          <view v-if="dictLoading" class="search-loading">
            <text>搜索中...</text>
          </view>

          <!-- 搜索结果 -->
          <view v-else>
            <view 
              v-for="item in displayDictRows" 
              :key="item.id"
              class="search-item"
              @click="selectDisease(item)"
            >
              <view class="item-main">
                <text class="item-name">{{ item.diagnosis_name || item.subcategory_name || item.name }}</text>
                <text class="item-code" v-if="item.diagnosis_code || item.code">
                  {{ item.diagnosis_code || item.code }}
                </text>
              </view>
              <text class="item-category" v-if="item.chapter_name">{{ item.chapter_name }}</text>
            </view>

            <!-- 自定义添加 -->
            <view v-if="searchQuery.trim() && displayDictRows.length === 0" class="custom-add">
              <text class="custom-hint">未找到"{{ searchQuery.trim() }}"</text>
              <view class="custom-btn" @click="selectCustomDisease">
                <text>+ 使用"{{ searchQuery.trim() }}"</text>
              </view>
            </view>

            <!-- 空提示 -->
            <view v-if="!searchQuery.trim()" class="search-empty">
              <text>请输入诊断名称或疾病名称搜索</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 医院搜索弹窗 -->
    <view v-if="showHospitalSearch" class="modal-mask" @click="showHospitalSearch = false">
      <view class="search-sheet" @click.stop>
        <view class="search-header">
          <input 
            class="search-input" 
            v-model="hospitalSearchQuery" 
            placeholder="输入医院名称搜索"
            focus
          />
          <text class="search-cancel" @click="showHospitalSearch = false">取消</text>
        </view>

        <scroll-view scroll-y class="search-content">
          <!-- 加载中 -->
          <view v-if="hospitalLoading" class="search-loading">
            <text>搜索中...</text>
          </view>

          <!-- 搜索结果 -->
          <view v-else>
            <view 
              v-for="item in hospitalResults" 
              :key="item.id"
              class="hospital-item"
              @click="selectHospital(item)"
            >
              <view class="hospital-main">
                <text class="hospital-name">{{ item.name }}</text>
                <text class="hospital-level" v-if="item.level">{{ item.level }}</text>
              </view>
              <view class="hospital-info" v-if="item.city || item.address">
                <text class="hospital-location">
                  <text v-if="item.city">{{ item.city }}</text>
                  <text v-if="item.city && item.address"> · </text>
                  <text v-if="item.address">{{ item.address }}</text>
                </text>
              </view>
            </view>

            <!-- 自定义添加 -->
            <view v-if="hospitalSearchQuery.trim() && hospitalResults.length === 0" class="custom-add">
              <text class="custom-hint">未找到"{{ hospitalSearchQuery.trim() }}"</text>
              <view class="custom-btn" @click="selectCustomHospital">
                <text>+ 使用"{{ hospitalSearchQuery.trim() }}"</text>
              </view>
            </view>

            <!-- 空提示 -->
            <view v-if="!hospitalSearchQuery.trim()" class="search-empty">
              <text>请输入医院名称搜索</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 底部悬浮添加按钮 -->
    <view v-if="!showModal && !showSearch && !showHospitalSearch" class="floating-add-btn" @click="openEdit()">
      <text class="add-text">添加慢病</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed, reactive, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getPatientDiseases, addPatientDisease, updatePatientDisease, deletePatientDisease } from '@/api/patient'
import { useUserStore } from '@/stores/user'
import { searchDiseases, type DiseaseDict } from '@/api/disease'
import { getHospitals, type Hospital } from '@/api/hospital'

const userStore = useUserStore()
const diseases = ref<any[]>([])
const showModal = ref(false)
const showSearch = ref(false)
const showHospitalSearch = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const dictLoading = ref(false)
const dictResults = ref<DiseaseDict[]>([])
const dictFetched = ref(false)
const initialDictResults = ref<DiseaseDict[]>([])

// 医院搜索相关
const hospitalSearchQuery = ref('')
const hospitalLoading = ref(false)
const hospitalResults = ref<Hospital[]>([])

const commonDiseases = ['2型糖尿病', '1型糖尿病', '高血压', '高脂血症', '冠心病', '慢性肾病']

const form = reactive({
  id: undefined as number | undefined,
  name: '',
  diagnosis_date: '',
  hospital: '',
  notes: ''
})

const goBack = () => {
  uni.navigateBack()
}

const loadDiseases = async () => {
  if (!userStore.token) return
  try {
    const res = await getPatientDiseases()
    diseases.value = res as any
  } catch (e) {
    console.error(e)
  }
}

const openEdit = (item?: any) => {
  if (item) {
    isEditing.value = true
    form.id = item.id
    form.name = item.name
    form.diagnosis_date = item.diagnosis_date
    form.hospital = item.hospital
    form.notes = item.notes
  } else {
    isEditing.value = false
    form.id = undefined
    form.name = ''
    const today = new Date()
    form.diagnosis_date = today.toISOString().split('T')[0]
    form.hospital = ''
    form.notes = ''
  }
  showModal.value = true
}

const closeEdit = () => {
  showModal.value = false
}

const saveEdit = async () => {
  if (!form.name) {
    uni.showToast({ title: '请选择疾病名称', icon: 'none' })
    return
  }
  
  try {
    const payload = {
      name: form.name,
      diagnosis_date: form.diagnosis_date,
      hospital: form.hospital,
      notes: form.notes
    }

    if (isEditing.value && form.id) {
      await updatePatientDisease(form.id, payload)
      uni.showToast({ title: '更新成功' })
    } else {
      await addPatientDisease(payload)
      uni.showToast({ title: '添加成功' })
    }
    closeEdit()
    loadDiseases()
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

const handleDelete = (item: any) => {
  uni.showModal({
    title: '确认删除',
    content: `确定要删除 ${item.name} 吗？`,
    success: async (res) => {
      if (res.confirm) {
        try {
          await deletePatientDisease(item.id)
          uni.showToast({ title: '删除成功' })
          loadDiseases()
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

const openSearch = () => {
  searchQuery.value = ''
  dictResults.value = initialDictResults.value
  dictFetched.value = initialDictResults.value.length > 0
  showSearch.value = true

  if (!dictFetched.value) {
    fetchDiseaseDict('')
  }
}

const selectDisease = (item: DiseaseDict) => {
  form.name = item.diagnosis_name || item.subcategory_name || item.name
  showSearch.value = false
}

const selectCustomDisease = () => {
  form.name = searchQuery.value.trim()
  showSearch.value = false
}

// 医院搜索
const openHospitalSearch = () => {
  hospitalSearchQuery.value = ''
  hospitalResults.value = []
  showHospitalSearch.value = true
}

const selectHospital = (item: Hospital) => {
  form.hospital = item.name
  showHospitalSearch.value = false
}

const selectCustomHospital = () => {
  form.hospital = hospitalSearchQuery.value.trim()
  showHospitalSearch.value = false
}

let hospitalSearchTimer: ReturnType<typeof setTimeout> | undefined

const fetchHospitals = async (q: string) => {
  hospitalLoading.value = true
  try {
    const keyword = (q || '').trim()
    const res: any = await getHospitals({ q: keyword || undefined })
    hospitalResults.value = Array.isArray(res) ? res : []
  } catch {
    hospitalResults.value = []
  } finally {
    hospitalLoading.value = false
  }
}

watch(
  () => hospitalSearchQuery.value,
  (q) => {
    const keyword = (q || '').trim()
    if (hospitalSearchTimer) {
      clearTimeout(hospitalSearchTimer)
    }
    hospitalSearchTimer = setTimeout(() => {
      fetchHospitals(keyword)
    }, 300)
  }
)

const displayDictRows = computed(() => {
  if (!dictFetched.value && !searchQuery.value) return []
  return dictResults.value
})

let searchTimer: ReturnType<typeof setTimeout> | undefined

const fetchDiseaseDict = async (q: string) => {
  dictLoading.value = true
  try {
    const keyword = (q || '').trim()
    const res: any = await searchDiseases({ q: keyword || undefined, skip: 0, limit: 50 })
    const items = Array.isArray(res) ? res : (res?.items || [])
    dictResults.value = items
    if (!keyword) {
      initialDictResults.value = dictResults.value
    }
  } catch {
    dictResults.value = []
  } finally {
    dictFetched.value = true
    dictLoading.value = false
  }
}

watch(
  () => searchQuery.value,
  (q) => {
    const keyword = (q || '').trim()
    if (searchTimer) {
      clearTimeout(searchTimer)
    }
    searchTimer = setTimeout(() => {
      if (!keyword) {
        dictResults.value = initialDictResults.value
        dictFetched.value = true
        return
      }
      fetchDiseaseDict(keyword)
    }, 250)
  }
)

const onDateChange = (e: any) => {
  form.diagnosis_date = e.detail.value
}

const getDiseaseIcon = (name: string) => {
  if (!name) return '📋'
  if (name.includes('糖尿病')) return '🩺'
  if (name.includes('高血压')) return '❤️'
  if (name.includes('高脂')) return '💊'
  if (name.includes('冠心')) return '💗'
  if (name.includes('肾')) return '🫘'
  return '📋'
}

onShow(() => {
  loadDiseases()
})
</script>

<style lang="scss">
/* 页面容器 */
.page-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 80px;
}

/* 底部悬浮添加按钮 */
.floating-add-btn {
  position: fixed;
  left: 50%;
  bottom: 32px;
  transform: translateX(-50%);
  min-width: 120px;
  height: 48px;
  padding: 0 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  z-index: 100;
  transition: all 0.3s ease;
}

.floating-add-btn:active {
  transform: translateX(-50%) scale(0.95);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

.floating-add-btn .add-text {
  font-size: 16px;
  color: #ffffff;
  font-weight: 600;
  letter-spacing: 1px;
}

.page-content {
  flex: 1;
  padding: 16px;
  box-sizing: border-box;
  overflow-x: hidden;
}

.page-bottom {
  height: 32px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 32px;
  box-sizing: border-box;
  width: 100%;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  text-align: center;
}

.empty-desc {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
}

/* 疾病列表 */
.disease-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  box-sizing: border-box;
}

/* 疾病卡片 */
.disease-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-sizing: border-box;
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 12px;
  box-sizing: border-box;
  width: 100%;
}

.disease-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.disease-info {
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.disease-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  display: block;
  margin-bottom: 4px;
  word-break: break-all;
}

.diagnosis-date {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.date-label {
  font-size: 12px;
  color: #9ca3af;
}

.date-value {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

/* 卡片详情 */
.card-details {
  padding: 0 16px 12px;
  border-top: 1px solid #f3f4f6;
  margin-top: 4px;
  padding-top: 12px;
  box-sizing: border-box;
  width: 100%;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
  width: 100%;
  box-sizing: border-box;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 12px;
  color: #9ca3af;
  min-width: 56px;
  flex-shrink: 0;
}

.detail-value {
  font-size: 13px;
  color: #4b5563;
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

/* 卡片操作 */
.card-actions {
  display: flex;
  border-top: 1px solid #f3f4f6;
  width: 100%;
  box-sizing: border-box;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  gap: 4px;
  box-sizing: border-box;
  min-width: 0;
}

.action-btn.edit {
  color: #374151;
  border-right: 1px solid #f3f4f6;
}

.action-btn.delete {
  color: #ef4444;
}

.btn-text {
  font-size: 14px;
  font-weight: 500;
}

/* 弹窗遮罩 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 100;
  display: flex;
  align-items: flex-end;
}

/* 弹窗内容 */
.modal-sheet {
  width: 100%;
  max-height: 85vh;
  background: #ffffff;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  padding-bottom: env(safe-area-inset-bottom);
}

.sheet-header {
  padding: 12px 16px 16px;
  box-sizing: border-box;
}

.sheet-handle {
  width: 36px;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  margin: 0 auto 12px;
}

.sheet-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sheet-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.sheet-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sheet-close text {
  font-size: 14px;
  color: #6b7280;
}

/* 表单内容 */
.sheet-body {
  flex: 1;
  padding: 0 16px;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.form-section {
  margin-bottom: 20px;
  width: 100%;
  box-sizing: border-box;
}

.section-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 8px;
}

.input-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-sizing: border-box;
  width: 100%;
}

.input-field.input-editable {
  padding: 0 12px;
}

.field-value {
  font-size: 15px;
  color: #111827;
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.field-value.placeholder {
  color: #9ca3af;
}

.field-arrow {
  font-size: 18px;
  color: #9ca3af;
  flex-shrink: 0;
}

.field-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.field-input {
  flex: 1;
  height: 44px;
  font-size: 15px;
  min-width: 0;
}

.field-placeholder {
  color: #9ca3af;
}

.textarea-field {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-sizing: border-box;
  width: 100%;
}

.field-textarea {
  width: 100%;
  height: 80px;
  font-size: 15px;
  box-sizing: border-box;
}

/* 快捷选择 */
.quick-select {
  margin-top: 12px;
  width: 100%;
  box-sizing: border-box;
}

.quick-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 8px;
  display: block;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
  box-sizing: border-box;
}

.quick-tag {
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  flex-shrink: 0;
  max-width: 100%;
  box-sizing: border-box;
}

.quick-tag.selected {
  background: #e0e7ff;
  color: #4338ca;
}

/* 弹窗底部 */
.sheet-footer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #f3f4f6;
  box-sizing: border-box;
  width: 100%;
}

.footer-btn {
  flex: 1;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 500;
  box-sizing: border-box;
  min-width: 0;
}

.footer-btn.cancel {
  background: #f3f4f6;
  color: #374151;
}

.footer-btn.confirm {
  background: #374151;
  color: #ffffff;
}

/* 搜索弹窗 */
.search-sheet {
  width: 100%;
  height: 70vh;
  background: #ffffff;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  padding-bottom: env(safe-area-inset-bottom);
}

.search-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  box-sizing: border-box;
  width: 100%;
}

.search-input {
  flex: 1;
  height: 36px;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 14px;
  box-sizing: border-box;
  min-width: 0;
}

.search-cancel {
  font-size: 14px;
  color: #6b7280;
  flex-shrink: 0;
}

.search-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.search-loading {
  padding: 32px 16px;
  text-align: center;
  font-size: 14px;
  color: #6b7280;
  box-sizing: border-box;
}

.search-empty {
  padding: 32px 16px;
  text-align: center;
  font-size: 14px;
  color: #9ca3af;
  box-sizing: border-box;
}

.search-item {
  padding: 14px 16px;
  border-bottom: 1px solid #f3f4f6;
  box-sizing: border-box;
  width: 100%;
}

.item-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  gap: 8px;
}

.item-name {
  font-size: 15px;
  font-weight: 500;
  color: #111827;
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.item-code {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.item-category {
  font-size: 12px;
  color: #9ca3af;
  word-break: break-all;
}

/* 自定义添加 */
.custom-add {
  padding: 24px 16px;
  text-align: center;
  box-sizing: border-box;
  width: 100%;
}

.custom-hint {
  font-size: 13px;
  color: #6b7280;
  display: block;
  margin-bottom: 12px;
  word-break: break-all;
}

.custom-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f3f4f6;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  box-sizing: border-box;
  max-width: 100%;
}

/* 医院搜索结果 */
.hospital-item {
  padding: 14px 16px;
  border-bottom: 1px solid #f3f4f6;
  box-sizing: border-box;
  width: 100%;
}

.hospital-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.hospital-name {
  font-size: 15px;
  font-weight: 500;
  color: #111827;
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.hospital-level {
  font-size: 11px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.hospital-info {
  margin-top: 4px;
}

.hospital-location {
  font-size: 12px;
  color: #9ca3af;
}
</style>
