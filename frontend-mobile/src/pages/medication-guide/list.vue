<template>
  <view class="page">
    <scroll-view scroll-y class="list" v-if="medications.length > 0">
      <view 
        v-for="med in medications" 
        :key="med.id" 
        class="item"
        @click="goToDetail(med)"
      >
        <view class="info">
          <text class="name">{{ med.generic_name || med.name }}</text>
          <text v-if="med.trade_name" class="sub">{{ med.trade_name }}</text>
          <text v-if="med.manufacturer" class="company">{{ med.manufacturer }}</text>
        </view>
        <text class="arrow">›</text>
      </view>
      <view v-if="hasMore" class="more" @click="loadMore">
        <text>点击加载更多</text>
      </view>
    </scroll-view>

    <view v-else class="empty">
      <text>暂无药品</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { safeNavigate } from '@/utils/navigate'
import { ref, onMounted } from 'vue'
import { searchMedicationDict, type MedicationDictItem } from '@/api/medication_dict'

const category = ref('')
const medications = ref<MedicationDictItem[]>([])
const loading = ref(false)
const hasMore = ref(false)
const currentSkip = ref(0)
const pageSize = 20

const goBack = () => uni.navigateBack()

const goToDetail = (med: MedicationDictItem) => {
  uni.navigateTo({ url: `/pages/medication-guide/detail?id=${med.id}` })
}

const loadMedications = async (reset = false) => {
  if (reset) {
    currentSkip.value = 0
    medications.value = []
  }
  loading.value = true
  try {
    const res = await searchMedicationDict({
      q: '',
      category: category.value || undefined,
      skip: currentSkip.value,
      limit: pageSize
    })
    const items = res.items || []
    if (reset) medications.value = items
    else medications.value.push(...items)
    hasMore.value = items.length === pageSize
    currentSkip.value += pageSize
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (hasMore.value && !loading.value) loadMedications()
}

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  category.value = decodeURIComponent(currentPage.options?.category || '')
  if (category.value) loadMedications(true)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.list {
  flex: 1;
  padding: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  width: 100%;
  box-sizing: border-box;
}

.info {
  flex: 1;
  min-width: 0;
  margin-right: 16rpx;
}

.name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
}

.sub {
  font-size: 26rpx;
  color: #666;
  margin-top: 4rpx;
  display: block;
}

.company {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow {
  font-size: 36rpx;
  color: #ccc;
  flex-shrink: 0;
  margin-left: 16rpx;
}

.more {
  padding: 32rpx;
  text-align: center;
}

.more text {
  font-size: 28rpx;
  color: #999;
}

.empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty text {
  font-size: 30rpx;
  color: #999;
}
</style>
