<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">我的患者</h2>
        <p class="text-text-muted mt-1">管理您绑定的患者信息</p>
      </div>
      <el-button type="primary" class="btn-primary" :icon="RefreshRight" @click="fetchPatients">刷新列表</el-button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-primary-100 text-primary-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><User /></el-icon>
          </div>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ patients.length }}</h3>
        <p class="text-sm text-text-muted">总患者数</p>
      </div>
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-green-100 text-green-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><CircleCheck /></el-icon>
          </div>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ activeCount }}</h3>
        <p class="text-sm text-text-muted">活跃患者</p>
      </div>
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-amber-100 text-amber-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><Calendar /></el-icon>
          </div>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ todayAppointments }}</h3>
        <p class="text-sm text-text-muted">今日复诊</p>
      </div>
      <div class="stat-card group">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 rounded-xl bg-rose-100 text-rose-600 group-hover:scale-110 transition-transform">
            <el-icon class="text-2xl"><Bell /></el-icon>
          </div>
        </div>
        <h3 class="text-3xl font-bold text-text-primary mb-1">{{ alertsCount }}</h3>
        <p class="text-sm text-text-muted">健康预警</p>
      </div>
    </div>

    <!-- Patient List -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <div class="p-5 border-b border-secondary-100 flex justify-between items-center">
        <h3 class="text-lg font-bold text-text-primary">患者列表</h3>
        <el-input
          v-model="searchQuery"
          placeholder="搜索患者姓名..."
          :prefix-icon="Search"
          class="w-64 custom-input"
          size="large"
          clearable
        />
      </div>
      
      <el-table 
        :data="filteredPatients" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        v-loading="loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
      >
        <el-table-column label="患者信息" min-width="200">
          <template #default="scope">
            <div class="flex items-center gap-3">
              <el-avatar :size="42" class="bg-gradient-to-br from-primary-500 to-primary-600 text-white font-bold text-lg">
                {{ scope.row.patient?.name?.charAt(0) || '?' }}
              </el-avatar>
              <div>
                <p class="font-medium text-text-primary">{{ scope.row.patient?.name }}</p>
                <p class="text-xs text-text-muted">{{ scope.row.patient?.user?.phone || '无手机号' }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="性别/年龄" width="120">
          <template #default="scope">
            <span class="text-text-secondary">{{ formatGender(scope.row.patient?.gender) }} / {{ scope.row.patient?.age || '-' }}岁</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                scope.row.status === 'active' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600'
              ]"
            >
              {{ scope.row.status === 'active' ? '活跃' : '暂停' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="绑定时间" width="140">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ formatDate(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button type="primary" link class="text-primary-600" @click="handleViewDetail(scope.row)">
              <el-icon class="mr-1"><View /></el-icon>
              详情
            </el-button>
            <el-button type="primary" link class="text-primary-600" @click="handleViewHealthData(scope.row)">
              <el-icon class="mr-1"><TrendCharts /></el-icon>
              健康数据
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Patient Detail Dialog -->
    <el-dialog v-model="detailVisible" title="患者详细档案" width="600px" class="custom-dialog">
      <el-descriptions :column="2" border class="custom-descriptions">
        <el-descriptions-item label="姓名">{{ currentPatient?.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">
          <span class="px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
            {{ currentPatient?.gender === 'male' ? '男' : '女' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentPatient?.age }}岁</el-descriptions-item>
        <el-descriptions-item label="身份证号">{{ currentPatient?.id_card || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="既往病史" :span="2">
          <div v-if="!isEditing" class="text-text-secondary">{{ currentPatient?.medical_history || '无记录' }}</div>
          <el-input v-else v-model="editForm.medical_history" type="textarea" :rows="3" placeholder="请输入既往病史" />
        </el-descriptions-item>
        <el-descriptions-item label="过敏史" :span="2">
          <div v-if="!isEditing" class="text-text-secondary">{{ currentPatient?.allergies || '无记录' }}</div>
          <el-input v-else v-model="editForm.allergies" type="textarea" :rows="2" placeholder="请输入过敏史" />
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <span class="dialog-footer">
          <el-button v-if="!isEditing" type="primary" class="btn-primary" @click="handleEditDetail">编辑档案</el-button>
          <template v-else>
            <el-button @click="handleCancelEdit">取消</el-button>
            <el-button type="primary" class="btn-primary" @click="handleSaveDetail">保存</el-button>
          </template>
        </span>
      </template>
    </el-dialog>

    <!-- Health Data Dialog -->
    <el-dialog v-model="dialogVisible" title="健康数据详情" width="70%" class="custom-dialog" @opened="initChart">
      <div class="mb-6">
        <el-radio-group v-model="chartType" @change="updateChart" class="custom-radio-group">
          <el-radio-button label="blood_pressure">血压</el-radio-button>
          <el-radio-button label="blood_sugar">血糖</el-radio-button>
          <el-radio-button label="weight">体重</el-radio-button>
          <el-radio-button label="heart_rate">心率</el-radio-button>
        </el-radio-group>
      </div>
      <div id="healthChart" class="w-full h-80 mb-6 bg-secondary-50 rounded-xl"></div>

      <el-table 
        :data="currentReadings" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        height="250"
      >
        <el-table-column prop="recorded_at" label="记录时间" width="180">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ new Date(scope.row.recorded_at).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <span class="px-2 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-700">
              {{ formatType(scope.row.type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="数值">
          <template #default="scope">
            <span class="font-medium text-text-primary">{{ scope.row.value_1 }}</span>
            <span v-if="scope.row.value_2" class="text-text-muted"> / {{ scope.row.value_2 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="100">
          <template #default="scope">
            <span class="text-text-muted">{{ scope.row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.notes || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, reactive, computed } from 'vue'
import { User, CircleCheck, Calendar, Bell, RefreshRight, Search, View, TrendCharts } from '@element-plus/icons-vue'
import { getMyPatients, getPatientReadings, getPatientDetail, updatePatientDetail } from '../../api/doctor'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const patients = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEditing = ref(false)
const currentReadings = ref([])
const currentPatient = ref<any>(null)
const searchQuery = ref('')
const editForm = reactive({
  medical_history: '',
  allergies: ''
})
const chartType = ref('blood_pressure')
let chartInstance: any = null

const activeCount = computed(() => patients.value.filter((p: any) => p.status === 'active').length)
const todayAppointments = ref(0)
const alertsCount = ref(0)

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value
  return patients.value.filter((p: any) => 
    p.patient?.name?.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const fetchPatients = async () => {
  loading.value = true
  try {
    const res: any = await getMyPatients()
    patients.value = res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleViewDetail = async (row: any) => {
  if (!row.patient || !row.patient.id) return
  
  try {
    const res: any = await getPatientDetail(row.patient.id)
    currentPatient.value = res
    isEditing.value = false
    detailVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handleEditDetail = () => {
  editForm.medical_history = currentPatient.value.medical_history || ''
  editForm.allergies = currentPatient.value.allergies || ''
  isEditing.value = true
}

const handleSaveDetail = async () => {
  try {
    const res: any = await updatePatientDetail(currentPatient.value.id, editForm)
    currentPatient.value = res
    isEditing.value = false
    ElMessage.success('更新成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('更新失败')
  }
}

const handleCancelEdit = () => {
  isEditing.value = false
}

const handleViewHealthData = async (row: any) => {
  if (!row.patient || !row.patient.id) return
  
  try {
    const res: any = await getPatientReadings(row.patient.id)
    currentReadings.value = res
    dialogVisible.value = true
    chartType.value = 'blood_pressure'
  } catch (error) {
    console.error(error)
  }
}

const initChart = async () => {
  await nextTick()
  const chartDom = document.getElementById('healthChart')
  if (chartDom) {
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartDom)
    updateChart()
  }
}

const updateChart = () => {
  if (!chartInstance) return
  
  const filteredData = currentReadings.value
    .filter((r: any) => r.type === chartType.value)
    .sort((a: any, b: any) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime())

  const dates = filteredData.map((r: any) => {
    const d = new Date(r.recorded_at)
    return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours()}:${d.getMinutes()}`
  })
  
  const series = []
  
  if (chartType.value === 'blood_pressure') {
    series.push({
      name: '收缩压',
      type: 'line',
      data: filteredData.map((r: any) => r.value_1),
      smooth: true,
      itemStyle: { color: '#3B82F6' }
    })
    series.push({
      name: '舒张压',
      type: 'line',
      data: filteredData.map((r: any) => r.value_2),
      smooth: true,
      itemStyle: { color: '#10B981' }
    })
  } else {
    series.push({
      name: formatType(chartType.value),
      type: 'line',
      data: filteredData.map((r: any) => r.value_1),
      smooth: true,
      itemStyle: { color: '#3B82F6' }
    })
  }
  
  const option = {
    title: { 
      text: formatType(chartType.value) + '趋势',
      textStyle: { color: '#1E293B', fontSize: 16, fontWeight: 'bold' }
    },
    tooltip: { 
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E2E8F0',
      textStyle: { color: '#1E293B' }
    },
    legend: { 
      data: series.map(s => s.name),
      textStyle: { color: '#64748B' }
    },
    xAxis: { 
      type: 'category', 
      data: dates,
      axisLabel: { rotate: 45, color: '#64748B' },
      axisLine: { lineStyle: { color: '#E2E8F0' } }
    },
    yAxis: { 
      type: 'value',
      axisLabel: { color: '#64748B' },
      splitLine: { lineStyle: { color: '#E2E8F0', type: 'dashed' } }
    },
    series: series,
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    }
  }
  
  chartInstance.setOption(option, true)
}

const formatType = (type: string) => {
  const map: Record<string, string> = {
    'blood_pressure': '血压',
    'blood_sugar': '血糖',
    'weight': '体重',
    'heart_rate': '心率'
  }
  return map[type] || type
}

const formatDate = (iso: string) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString()
}

const formatGender = (gender: string) => {
  const map: any = { male: '男', female: '女', other: '其他' }
  return map[gender] || '未知'
}

onMounted(() => {
  fetchPatients()
})
</script>

<style scoped>
.btn-primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border: none;
  border-radius: 10px;
  font-weight: 500;
}
.btn-primary:hover {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
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

:deep(.custom-input .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #E2E8F0;
  padding: 4px 12px;
}
:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6;
}
:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

:deep(.custom-radio-group .el-radio-button__inner) {
  background-color: #fff;
  border-color: #E2E8F0;
  color: #64748B;
  font-weight: 500;
  padding: 8px 16px;
}
:deep(.custom-radio-group .el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 8px 0 0 8px;
}
:deep(.custom-radio-group .el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 8px 8px 0;
}
:deep(.custom-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #3B82F6;
  border-color: #3B82F6;
  color: white;
}

:deep(.custom-descriptions .el-descriptions__label) {
  background-color: #F8FAFC;
  color: #475569;
  font-weight: 500;
}
:deep(.custom-descriptions .el-descriptions__content) {
  background-color: #fff;
  color: #1E293B;
}

:deep(.custom-dialog .el-dialog__header) {
  border-bottom: 1px solid #E2E8F0;
  padding-bottom: 16px;
}
</style>
