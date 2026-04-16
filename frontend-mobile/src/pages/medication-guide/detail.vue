<template>
  <view class="page">
    <scroll-view scroll-y class="detail-scroll" v-if="medication">
      <view class="info-card">
        <view class="card-header">
          <view class="drug-icon">
            <text>💊</text>
          </view>
          <view class="drug-title">
            <text class="drug-name">{{ medication.generic_name || medication.name }}</text>
            <text v-if="medication.trade_name" class="drug-trade">{{ medication.trade_name }}</text>
          </view>
        </view>
        
        <view class="info-grid">
          <view v-if="medication.therapeutic_system_category" class="info-item">
            <text class="info-label">治疗系统</text>
            <text class="info-value">{{ medication.therapeutic_system_category }}</text>
          </view>
          <view v-if="medication.therapeutic_system_subcategory" class="info-item">
            <text class="info-label">二级分类</text>
            <text class="info-value">{{ medication.therapeutic_system_subcategory }}</text>
          </view>
          <view v-if="medication.specification" class="info-item">
            <text class="info-label">规格</text>
            <text class="info-value">{{ medication.specification }}</text>
          </view>
          <view v-if="medication.manufacturer" class="info-item full">
            <text class="info-label">生产企业</text>
            <text class="info-value">{{ medication.manufacturer }}</text>
          </view>
          <view v-if="medication.approval_number" class="info-item full">
            <text class="info-label">批准文号</text>
            <text class="info-value">{{ medication.approval_number }}</text>
          </view>
        </view>
      </view>

      <view v-if="medication.indications" class="info-card">
        <view class="section-header">
          <view class="section-icon green">
            <text>🎯</text>
          </view>
          <text class="section-title">适应症</text>
        </view>
        <view class="section-content">
          <text>{{ medication.indications }}</text>
        </view>
      </view>

      <view v-if="medication.usage_dosage" class="info-card">
        <view class="section-header">
          <view class="section-icon blue">
            <text>📋</text>
          </view>
          <text class="section-title">用法用量</text>
        </view>
        <view class="section-content highlight">
          <text>{{ medication.usage_dosage }}</text>
        </view>
      </view>

      <view v-if="medication.adverse_reactions" class="info-card">
        <view class="section-header">
          <view class="section-icon orange">
            <text>⚠️</text>
          </view>
          <text class="section-title">不良反应</text>
        </view>
        <view class="section-content warning">
          <text>{{ medication.adverse_reactions }}</text>
        </view>
      </view>

      <view v-if="medication.contraindications" class="info-card">
        <view class="section-header">
          <view class="section-icon red">
            <text>🚫</text>
          </view>
          <text class="section-title">禁忌</text>
        </view>
        <view class="section-content danger">
          <text>{{ medication.contraindications }}</text>
        </view>
      </view>

      <view v-if="medication.precautions" class="info-card">
        <view class="section-header">
          <view class="section-icon purple">
            <text>💡</text>
          </view>
          <text class="section-title">注意事项</text>
        </view>
        <view class="section-content">
          <text>{{ medication.precautions }}</text>
        </view>
      </view>

      <view v-if="hasSpecialPopulation" class="info-card">
        <view class="section-header">
          <view class="section-icon pink">
            <text>👥</text>
          </view>
          <text class="section-title">特殊人群用药</text>
        </view>
        <view class="special-list">
          <view v-if="medication.pregnancy_lactation" class="special-item">
            <text class="special-label">孕妇及哺乳期妇女</text>
            <text class="special-value">{{ medication.pregnancy_lactation }}</text>
          </view>
          <view v-if="medication.pediatric_use" class="special-item">
            <text class="special-label">儿童用药</text>
            <text class="special-value">{{ medication.pediatric_use }}</text>
          </view>
          <view v-if="medication.geriatric_use" class="special-item">
            <text class="special-label">老人用药</text>
            <text class="special-value">{{ medication.geriatric_use }}</text>
          </view>
        </view>
      </view>

      <view v-if="medication.storage || medication.expiry_period" class="info-card">
        <view class="section-header">
          <view class="section-icon gray">
            <text>📦</text>
          </view>
          <text class="section-title">贮藏与有效期</text>
        </view>
        <view class="storage-grid">
          <view v-if="medication.storage" class="storage-item">
            <text class="storage-label">贮藏条件</text>
            <text class="storage-value">{{ medication.storage }}</text>
          </view>
          <view v-if="medication.expiry_period" class="storage-item">
            <text class="storage-label">有效期</text>
            <text class="storage-value">{{ medication.expiry_period }}</text>
          </view>
        </view>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>

    <view v-if="!medication" class="loading-state">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, computed, onMounted } from 'vue'
import { getMedicationDetail, type MedicationDictItem } from '@/api/medication_dict'

const medication = ref<MedicationDictItem | null>(null)

const hasSpecialPopulation = computed(() => {
  if (!medication.value) return false
  return !!(
    medication.value.pregnancy_lactation || 
    medication.value.pediatric_use || 
    medication.value.geriatric_use
  )
})

const goBack = () => uni.navigateBack()

const loadMedication = async (id: number) => {
  try {
    medication.value = await getMedicationDetail(id)
  } catch (e) {
    console.error('Failed to load medication:', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || {}
  const id = parseInt(options.id || '0')
  
  if (id) {
    loadMedication(id)
  }
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: #f8fafc;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.detail-scroll {
  flex: 1;
  padding: 24rpx;
  box-sizing: border-box;
  width: 100%;
}

.info-card {
  background-color: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 24rpx;
  margin-bottom: 24rpx;
  padding-bottom: 24rpx;
  border-bottom: 2rpx solid #f1f5f9;
  box-sizing: border-box;
  width: 100%;
}

.drug-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 24rpx;
  background-color: #e0f2fe;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.drug-icon text {
  font-size: 48rpx;
}

.drug-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.drug-name {
  font-size: 40rpx;
  font-weight: 700;
  color: #0f172a;
  display: block;
  line-height: 1.3;
  word-break: break-word;
}

.drug-trade {
  font-size: 28rpx;
  color: #64748b;
  margin-top: 8rpx;
  display: block;
  word-break: break-word;
}

.info-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 24rpx;
  box-sizing: border-box;
  width: 100%;
}

.info-item {
  width: calc(50% - 12rpx);
  box-sizing: border-box;
  overflow: hidden;
}

.info-item.full {
  width: 100%;
}

.info-label {
  font-size: 24rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 8rpx;
}

.info-value {
  font-size: 28rpx;
  color: #334155;
  font-weight: 500;
  display: block;
  word-break: break-all;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 24rpx;
  box-sizing: border-box;
}

.section-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-icon text {
  font-size: 32rpx;
}

.section-icon.green { background-color: #dcfce7; }
.section-icon.blue { background-color: #dbeafe; }
.section-icon.orange { background-color: #ffedd5; }
.section-icon.red { background-color: #fee2e2; }
.section-icon.purple { background-color: #f3e8ff; }
.section-icon.pink { background-color: #fce7f3; }
.section-icon.gray { background-color: #f1f5f9; }

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #0f172a;
}

.section-content {
  background-color: #f8fafc;
  border-radius: 24rpx;
  padding: 28rpx;
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
}

.section-content text {
  font-size: 28rpx;
  color: #334155;
  line-height: 1.7;
  word-break: break-all;
  display: block;
  width: 100%;
}

.section-content.highlight {
  background-color: #eff6ff;
}

.section-content.warning {
  background-color: #fff7ed;
}

.section-content.danger {
  background-color: #fef2f2;
}

.special-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  box-sizing: border-box;
  width: 100%;
}

.special-item {
  background-color: #f8fafc;
  border-radius: 24rpx;
  padding: 24rpx;
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
}

.special-label {
  font-size: 24rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 8rpx;
}

.special-value {
  font-size: 28rpx;
  color: #334155;
  line-height: 1.5;
  word-break: break-all;
  display: block;
}

.storage-grid {
  display: flex;
  gap: 48rpx;
  box-sizing: border-box;
  width: 100%;
}

.storage-item {
  flex: 1;
  box-sizing: border-box;
  overflow: hidden;
}

.storage-label {
  font-size: 24rpx;
  color: #94a3b8;
  display: block;
  margin-bottom: 8rpx;
}

.storage-value {
  font-size: 28rpx;
  color: #334155;
  word-break: break-all;
  display: block;
}

.bottom-space {
  height: 80rpx;
}

.loading-state {
  padding: 160rpx 0;
  text-align: center;
}

.loading-state text {
  font-size: 28rpx;
  color: #64748b;
}
</style>
