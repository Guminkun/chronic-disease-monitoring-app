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
          :range="reportTypes" 
          range-key="name"
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
      
      <!-- 始终挂载 EchartsComp，避免 v-show 隐藏时 canvas 尺寸为 0 -->
      <view class="echarts-dom" :style="{ display: hasEnoughData ? 'block' : 'none' }">
        <EchartsComp canvas-id="trend-chart" @init="onChartInit" />
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getTrends } from '@/api/report'
import { getReportTypes } from '@/api/report_type'
import * as echarts from 'echarts'
import EchartsComp from '@/components/EchartsComp.vue'

const loading = ref(false)
const allTrends = ref<any[]>([])
const metricIndex = ref(0)
const chartInstance = ref<any>(null)

// Report Types
const reportTypes = ref<any[]>([{ id: -1, name: '全部类型' }])
const reportTypeIndex = ref(0)

// Computed properties
const metricNames = computed(() => allTrends.value.map(t => t.metric_name))
const selectedMetric = computed(() => allTrends.value[metricIndex.value] || null)
const selectedMetricName = computed(() => selectedMetric.value?.metric_name || '')
const currentPoints = computed(() => selectedMetric.value?.points || [])
const currentUnit = computed(() => selectedMetric.value?.unit || '')
const hasEnoughData = computed(() => currentPoints.value.length >= 2)

const selectedReportTypeName = computed(() => {
  const type = reportTypes.value[reportTypeIndex.value]
  return type ? type.name : '全部类型'
})

// Lifecycle
onMounted(async () => {
  await fetchReportTypes()
  await fetchData()
})

const onChartInit = (chart: any) => {
  chartInstance.value = chart
  tryRender()
}

// 数据和图表实例都就绪后才渲染
const tryRender = () => {
  if (!chartInstance.value || !hasEnoughData.value) return
  renderChart()
}

onUnmounted(() => {
  chartInstance.value?.dispose()
})

// Methods
const fetchReportTypes = async () => {
  try {
    const res = await getReportTypes({})
    if (Array.isArray(res)) {
      // Filter distinct categories/names or just use raw list
      // For simplicity, we just use the names returned. 
      // Ideally backend should return distinct types used by this user, but here we list all available types
      reportTypes.value = [{ id: -1, name: '全部类型' }, ...res]
    }
  } catch (error) {
    console.error('Failed to fetch report types:', error)
  }
}

const fetchData = async () => {
  try {
    loading.value = true
    const type = reportTypes.value[reportTypeIndex.value]
    const typeParam = (type && type.id !== -1) ? type.name : undefined
    
    const res = await getTrends({ report_type: typeParam })
    // res should be an array of MetricTrendResponse
    if (Array.isArray(res)) {
      allTrends.value = res
      // Select first metric by default if available
      metricIndex.value = 0
      if (allTrends.value.length > 0) {
        initChart()
      } else {
        // Clear chart if no data
        if (chartInstance.value) {
          chartInstance.value.clear()
        }
      }
    }
  } catch (error) {
    console.error('Failed to fetch trends:', error)
    uni.showToast({ title: '获取数据失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const handleReportTypeChange = (e: any) => {
  reportTypeIndex.value = e.detail.value
  fetchData()
}

const handleMetricChange = (e: any) => {
  metricIndex.value = e.detail.value
  initChart()
}

const initChart = () => {
  tryRender()
}

const renderChart = () => {

  const dates = currentPoints.value.map((p: any) => p.date)
  const values = currentPoints.value.map((p: any) => p.value)
  
  const option = {
    title: {
      text: `${selectedMetricName.value} 趋势`,
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        formatter: (value: string) => {
            return value.substring(5) // MM-DD
        }
      }
    },
    yAxis: {
      type: 'value',
      name: currentUnit.value
    },
    series: [
      {
        name: selectedMetricName.value,
        type: 'line',
        data: values,
        smooth: true,
        markPoint: {
          data: [
            { type: 'max', name: 'Max' },
            { type: 'min', name: 'Min' }
          ]
        },
        lineStyle: {
          color: '#3b82f6',
          width: 3
        },
        itemStyle: {
          color: '#3b82f6'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ])
        }
      }
    ]
  }
  
  chartInstance.value.setOption(option)
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
  background-color: #f5f7fa;
  padding: 20px;
}

.header {
  margin-bottom: 20px;
  .title {
    font-size: 24px;
    font-weight: bold;
    color: #1e293b;
    display: block;
    margin-bottom: 4px;
  }
  .subtitle {
    font-size: 14px;
    color: #64748b;
  }
}

.filter-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  gap: 12px;
  
  .filter-item {
    flex: 1;
    min-width: 0; // Prevent flex item overflow
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
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  .echarts-dom {
    width: 100%;
    height: 300px;
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
    }
    
    .empty-subtext {
      font-size: 12px;
      margin-bottom: 16px;
    }
    
    .upload-btn {
      font-size: 14px;
      background-color: #3b82f6;
      color: white;
      border-radius: 20px;
      padding: 0 20px;
      line-height: 36px;
      border: none;
      
      &:active {
        background-color: #2563eb;
      }
    }
  }
}

.list-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  
  .list-header {
    display: flex;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid #f1f5f9;
    margin-bottom: 12px;
    font-size: 14px;
    color: #64748b;
    font-weight: 500;
    
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
    padding: 12px 0;
    border-bottom: 1px solid #f8fafc;
    
    &:last-child {
      border-bottom: none;
    }
    
    .col-date {
      flex: 1;
      text-align: center;
      color: #334155;
      font-size: 14px;
    }
    
    .col-value {
      flex: 1;
      text-align: center;
      color: #0f172a;
      font-size: 16px;
      font-weight: 600;
    }
    
    .col-status {
      flex: 1;
      display: flex;
      justify-content: center;
      
      .status-tag {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 10px;
        background-color: #ecfdf5;
        color: #059669;
        
        &.abnormal {
          background-color: #fef2f2;
          color: #dc2626;
        }
      }
    }
  }
}
</style>

