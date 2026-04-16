<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">数据概览</h2>
        <p class="text-text-muted mt-1">欢迎回来，查看系统运营数据</p>
      </div>
      <div class="flex items-center gap-3">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索..." 
          :prefix-icon="Search"
          class="w-64 custom-input"
          size="large"
        />
        <el-button circle :icon="Bell" size="large" class="custom-icon-btn" />
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
      <!-- Total Users -->
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-primary-100 text-primary-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><User /></el-icon>
          </div>
          <span class="text-xs font-semibold text-green-600 bg-green-100 px-2.5 py-1 rounded-full">+12%</span>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ stats.total_users }}</h3>
        <p class="text-sm text-text-muted">总用户数</p>
      </div>

      <!-- Active Users -->
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-blue-100 text-blue-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><UserFilled /></el-icon>
          </div>
          <span class="text-xs font-semibold text-green-600 bg-green-100 px-2.5 py-1 rounded-full">+8%</span>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ stats.active_users }}</h3>
        <p class="text-sm text-text-muted">活跃用户</p>
      </div>

      <!-- Today Revisits -->
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-amber-100 text-amber-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><Calendar /></el-icon>
          </div>
          <span class="text-xs font-semibold text-green-600 bg-green-100 px-2.5 py-1 rounded-full">+3</span>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ stats.today_revisits }}</h3>
        <p class="text-sm text-text-muted">今日复诊</p>
      </div>

      <!-- Pending Reports -->
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-rose-100 text-rose-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><Document /></el-icon>
          </div>
          <span class="text-xs font-semibold text-red-600 bg-red-100 px-2.5 py-1 rounded-full">-2</span>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ stats.pending_reports }}</h3>
        <p class="text-sm text-text-muted">待处理报告</p>
      </div>

      <!-- New Users Month -->
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-green-100 text-green-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><TrendCharts /></el-icon>
          </div>
          <span class="text-xs font-semibold text-green-600 bg-green-100 px-2.5 py-1 rounded-full">+15%</span>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ stats.new_users_month }}</h3>
        <p class="text-sm text-text-muted">本月新增</p>
      </div>
    </div>

    <!-- Middle Section: Recent Users & Upcoming Revisits -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Recent Users -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-6">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-xl bg-primary-100 text-primary-600">
              <el-icon class="text-xl"><User /></el-icon>
            </div>
            <div>
              <h3 class="text-lg font-bold text-text-primary">最近用户</h3>
              <p class="text-xs text-text-muted">新注册的用户</p>
            </div>
          </div>
          <el-button type="primary" link class="text-primary-600" @click="$router.push('/admin/users')">
            查看全部
            <el-icon class="ml-1"><ArrowRight /></el-icon>
          </el-button>
        </div>
        
        <div class="space-y-3">
          <div v-for="user in recentUsers" :key="user.id" class="flex items-center justify-between p-4 rounded-xl hover:bg-secondary-50 transition-colors border border-secondary-100">
            <div class="flex items-center gap-3">
              <el-avatar :size="44" class="bg-gradient-to-br from-primary-500 to-primary-600 text-white font-bold text-lg">
                {{ user.name.charAt(0) }}
              </el-avatar>
              <div>
                <p class="font-medium text-text-primary">{{ user.name }}</p>
                <p class="text-xs text-text-muted">{{ user.phone }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <span v-for="d in user.diseases.slice(0, 2)" :key="d" class="px-2.5 py-1 text-xs rounded-lg bg-secondary-100 text-text-secondary font-medium">
                {{ d }}
              </span>
            </div>
          </div>
        </div>
        
        <div v-if="recentUsers.length === 0" class="py-12 text-center text-text-muted">
          <el-icon class="text-4xl mb-2"><User /></el-icon>
          <p>暂无用户数据</p>
        </div>
      </div>

      <!-- Upcoming Revisits -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-6">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-xl bg-amber-100 text-amber-600">
              <el-icon class="text-xl"><Calendar /></el-icon>
            </div>
            <div>
              <h3 class="text-lg font-bold text-text-primary">待处理复诊</h3>
              <p class="text-xs text-text-muted">需要跟进的复诊预约</p>
            </div>
          </div>
          <el-button type="primary" link class="text-primary-600">
            查看全部
            <el-icon class="ml-1"><ArrowRight /></el-icon>
          </el-button>
        </div>

        <div class="space-y-3">
          <div v-for="visit in upcomingRevisits" :key="visit.id" class="flex items-center justify-between p-4 rounded-xl border-l-4 border-amber-400 bg-amber-50/50 border border-amber-100">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 font-bold">
                {{ visit.patient_name.charAt(0) }}
              </div>
              <div>
                <p class="font-medium text-text-primary">{{ visit.patient_name }}</p>
                <p class="text-xs text-text-muted">{{ visit.disease_name }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-bold text-amber-600">{{ visit.date }}</p>
              <p class="text-xs text-text-muted">复诊日期</p>
            </div>
          </div>
        </div>

        <div v-if="upcomingRevisits.length === 0" class="py-12 text-center text-text-muted">
          <el-icon class="text-4xl mb-2"><Calendar /></el-icon>
          <p>暂无待处理复诊</p>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="content-card">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-xl bg-purple-100 text-purple-600">
            <el-icon class="text-xl"><TrendCharts /></el-icon>
          </div>
          <div>
            <h3 class="text-lg font-bold text-text-primary">数据趋势</h3>
            <p class="text-xs text-text-muted">用户活跃度统计</p>
          </div>
        </div>
        <div class="flex gap-2">
          <el-radio-group v-model="trendPeriod" size="default" class="custom-radio-group">
            <el-radio-button label="7">7天</el-radio-button>
            <el-radio-button label="30">30天</el-radio-button>
            <el-radio-button label="90">90天</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <div id="trendChart" class="w-full h-80"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { User, UserFilled, Calendar, Document, TrendCharts, Search, Bell, ArrowRight } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getOverview, getTrends } from '../../api/dashboard'

const searchQuery = ref('')
const trendPeriod = ref('30')
const stats = ref({
  total_users: 0,
  active_users: 0,
  today_revisits: 0,
  pending_reports: 0,
  new_users_month: 0,
  active_med_plans: 0
})
const recentUsers = ref<any[]>([])
const upcomingRevisits = ref<any[]>([])

let chartInstance: echarts.ECharts | null = null

const initChart = (data: any[]) => {
  const chartDom = document.getElementById('trendChart')
  if (!chartDom) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartDom)
  
  const option = {
    grid: { top: 20, right: 20, bottom: 30, left: 50, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E2E8F0',
      borderWidth: 1,
      textStyle: { color: '#1E293B' },
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date),
      axisLine: { lineStyle: { color: '#E2E8F0' } },
      axisLabel: { color: '#64748B', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { type: 'dashed', color: '#E2E8F0' } },
      axisLabel: { color: '#64748B', fontSize: 12 }
    },
    series: [{
      data: data.map(item => item.value),
      type: 'bar',
      barWidth: '50%',
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#3B82F6' },
          { offset: 1, color: '#60A5FA' }
        ]),
        borderRadius: [6, 6, 0, 0]
      }
    }]
  }
  
  chartInstance.setOption(option)
}

const fetchData = async () => {
  try {
    const res: any = await getOverview()
    stats.value = res.stats
    recentUsers.value = res.recent_users
    upcomingRevisits.value = res.upcoming_revisits
    
    await fetchTrendData()
  } catch (e) {
    console.error(e)
  }
}

const fetchTrendData = async () => {
  try {
    const res: any = await getTrends(Number(trendPeriod.value))
    initChart(res)
  } catch (e) {
    console.error(e)
  }
}

watch(trendPeriod, () => {
  fetchTrendData()
})

onMounted(() => {
  fetchData()
  window.addEventListener('resize', () => chartInstance?.resize())
})
</script>

<style scoped>
.dashboard-container {
  /* Container styles */
}

.stat-card {
  background-color: #fff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #E2E8F0;
  transition: all 0.3s;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
  border-color: #CBD5E1;
}

.content-card {
  background-color: #fff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #E2E8F0;
}

:deep(.custom-input .el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #E2E8F0;
  padding: 4px 12px;
}
:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6;
}
:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

:deep(.custom-icon-btn) {
  background-color: #fff;
  border-color: #E2E8F0;
  color: #64748B;
}
:deep(.custom-icon-btn:hover) {
  background-color: #F1F5F9;
  border-color: #CBD5E1;
  color: #3B82F6;
}

:deep(.custom-radio-group .el-radio-button__inner) {
  background-color: #fff;
  border-color: #E2E8F0;
  color: #64748B;
  font-weight: 500;
  padding: 8px 16px;
}
:deep(.custom-radio-group .el-radio-button:first-child .el-radio-button__inner) {
  border-left-color: #E2E8F0;
  border-radius: 8px 0 0 8px;
}
:deep(.custom-radio-group .el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 8px 8px 0;
}
:deep(.custom-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #3B82F6;
  border-color: #3B82F6;
  color: white;
  box-shadow: -1px 0 0 0 #3B82F6;
}
</style>
