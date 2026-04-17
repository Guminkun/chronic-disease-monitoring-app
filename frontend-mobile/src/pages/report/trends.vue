<template>
  <view class="container">
    <view class="header">
      <text class="title">健康指标趋势</text>
      <text class="subtitle">基于已上传的检查报告数据生成</text>
    </view>
    
    <!-- 筛选区域 -->
    <view class="filter-card">
      <view class="filter-item">
        <view class="filter-label">报告类型</view>
        <picker 
          mode="selector"
          :range="REPORT_SUBCATEGORIES"
          :value="reportTypeIndex" 
          @change="handleReportTypeChange"
        >
          <view class="picker-view">
            <text class="picker-text">{{ selectedReportTypeName }}</text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
      </view>

      <view class="filter-item">
        <view class="filter-label">当前指标</view>
        <picker 
          mode="selector"
          v-if="metricNames.length > 0" 
          :range="metricNames" 
          :value="metricIndex" 
          @change="handleMetricChange"
        >
          <view class="picker-view">
            <text class="picker-text">{{ selectedMetricName }}</text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
        <view v-else class="picker-view disabled">
          <text>暂无可用指标数据</text>
        </view>
      </view>
    </view>
    
    <!-- 图表区域 -->
    <view class="chart-card">
      <view v-if="loading" class="loading-container">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="!hasEnoughData" class="empty-container">
        <text class="empty-text">需要至少2份包含该指标的报告</text>
        <text class="empty-subtext">当前记录数: {{ currentPoints.length }}</text>
        <button class="upload-btn" @click="goToUpload">上传新报告</button>
      </view>
      
      <view v-else class="chart-wrapper">
        <TrendChart 
          :title="selectedMetricName + ' 趋势'"
          :data="chartData"
          :unit="currentUnit"
        />
      </view>
    </view>
    
    <!-- 数据列表 -->
    <view class="list-card" v-if="hasEnoughData">
      <view class="list-header">
        <text class="col-date">日期</text>
        <text class="col-value">数值</text>
        <text class="col-status">状态</text>
      </view>
      <view class="list-item" v-for="(item, index) in currentPoints" :key="index">
        <text class="col-date">{{ formatDate(item.date) }}</text>
        <text class="col-value">{{ item.value }}</text>
        <view class="col-status">
          <view class="status-tag" :class="{ abnormal: item.is_abnormal }">
            {{ item.is_abnormal ? '异常' : '正常' }}
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getTrends } from '@/api/report'
import { useMemberStore } from '@/stores/member'
import TrendChart from '@/components/TrendChart.vue'

const memberStore = useMemberStore()

const loading = ref(false)
const allTrends = ref<any[]>([])
const metricIndex = ref(0)

const REPORT_SUBCATEGORIES = [
  '全部类型',
  '血常规', '尿常规', '肝功能', '肾功能', '血糖检测', '血脂检测',
  '电解质', '甲状腺功能', '凝血功能', '心肌酶谱', '肿瘤标志物', '乙肝五项',
  'CT检查', 'MRI检查', 'X线检查', '超声检查', '心电图', '胃镜检查', '肠镜检查'
]

const reportTypeIndex = ref(0)

const metricNames = computed(() => allTrends.value.map(t => t.metric_name))
const selectedMetric = computed(() => allTrends.value[metricIndex.value] || null)
const selectedMetricName = computed(() => selectedMetric.value?.metric_name || '')
const currentPoints = computed(() => selectedMetric.value?.points || [])
const currentUnit = computed(() => selectedMetric.value?.unit || '')
const hasEnoughData = computed(() => currentPoints.value.length >= 2)

const selectedReportTypeName = computed(() => {
  return REPORT_SUBCATEGORIES[reportTypeIndex.value] || '全部类型'
})

const chartData = computed(() => {
  return currentPoints.value.map((p: any) => ({
    date: typeof p.date === 'string' ? p.date : String(p.date),
    value: p.value
  }))
})

onMounted(() => {})

onShow(async () => {
  await fetchData()
})

const fetchData = async () => {
  try {
    loading.value = true
    const typeName = REPORT_SUBCATEGORIES[reportTypeIndex.value]
    const typeParam = typeName === '全部类型' ? undefined : typeName
    
    const memberId = memberStore.currentMember?.id
    const res = await getTrends({ 
      report_type: typeParam,
      member_id: memberId
    })
    if (Array.isArray(res)) {
      allTrends.value = res
      metricIndex.value = 0
    }
  } catch (error) {
    console.error('Failed to fetch trends:', error)
    uni.showToast({ title: '获取数据失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const handleReportTypeChange = (e: any) => {
  const value = Number(e.detail.value)
  reportTypeIndex.value = isNaN(value) ? 0 : value
  fetchData()
}

const handleMetricChange = (e: any) => {
  const value = Number(e.detail.value)
  metricIndex.value = isNaN(value) ? 0 : value
}

const goToUpload = () => {
  uni.navigateTo({ url: '/pages/report/upload' })
}

const formatDate = (dateStr: string) => {
  return dateStr
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 16px;
  box-sizing: border-box;
}

.header {
  margin-bottom: 24px;
  padding: 0 4px;
  .title {
    font-size: 26px;
    font-weight: 700;
    color: #1e293b;
    display: block;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
  }
  .subtitle {
    font-size: 14px;
    color: #64748b;
    font-weight: 400;
  }
}

.filter-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  display: flex;
  gap: 16px;
  
  .filter-item {
    flex: 1;
    min-width: 0;
  }
  
  .filter-label {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
  }
  
  .picker-view {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f8fafc;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    
    &.disabled {
      color: #94a3b8;
    }
    
    .picker-text {
      font-size: 14px;
      font-weight: 500;
      color: #334155;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    
    .picker-arrow {
      font-size: 12px;
      color: #94a3b8;
      margin-left: 4px;
    }
  }
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-sizing: border-box;
  overflow: hidden;
  
  .chart-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    overflow: hidden;
  }
  
  .loading-container, .empty-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #94a3b8;
    
    .empty-text {
      font-size: 16px;
      margin-bottom: 8px;
      font-weight: 500;
    }
    
    .empty-subtext {
      font-size: 13px;
      margin-bottom: 16px;
      color: #94a3b8;
    }
    
    .upload-btn {
      font-size: 14px;
      background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
      color: white;
      border-radius: 24px;
      padding: 0 24px;
      line-height: 40px;
      border: none;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
      
      &:active {
        transform: scale(0.98);
      }
    }
  }
}

.list-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
  
  .list-header {
    display: flex;
    justify-content: space-between;
    padding-bottom: 16px;
    border-bottom: 2px solid #f1f5f9;
    margin-bottom: 12px;
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    
    .col-date,
    .col-value,
    .col-status {
      flex: 1;
      text-align: center;
    }
  }
  
  .list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid #f8fafc;
    transition: background 0.2s;
    
    &:last-child {
      border-bottom: none;
    }
    
    .col-date {
      flex: 1;
      text-align: center;
      color: #475569;
      font-size: 14px;
      font-weight: 500;
    }
    
    .col-value {
      flex: 1;
      text-align: center;
      color: #1e293b;
      font-size: 15px;
      font-weight: 600;
    }
    
    .col-status {
      flex: 1;
      display: flex;
      justify-content: center;
    }
  }
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: #ecfdf5;
  color: #059669;
  
  &.abnormal {
    background: #fef2f2;
    color: #dc2626;
  }
}
</style>

