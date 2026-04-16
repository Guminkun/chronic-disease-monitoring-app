<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">用户管理</h2>
        <p class="text-text-muted mt-1">管理系统所有注册用户</p>
      </div>
      <el-button type="primary" class="btn-primary" :icon="Plus">添加用户</el-button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center">
      <div class="w-64">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户姓名或手机号..."
          :prefix-icon="Search"
          class="custom-input"
          size="large"
          clearable
          @clear="fetchData"
          @keyup.enter="fetchData"
        />
      </div>
      <el-select v-model="filterStatus" placeholder="状态" class="w-36 custom-select" size="large" clearable @change="fetchData">
        <el-option label="活跃" value="active" />
        <el-option label="未活跃" value="inactive" />
      </el-select>
      <div class="flex-grow"></div>
      <el-button type="primary" link :icon="Download" class="text-primary-600">导出数据</el-button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table 
        :data="users" 
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
                {{ scope.row.name.charAt(0) }}
              </el-avatar>
              <div>
                <p class="font-medium text-text-primary">{{ scope.row.name }}</p>
                <p class="text-xs text-text-muted">{{ scope.row.user?.phone || '无手机号' }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="性别/年龄" width="120">
          <template #default="scope">
            <span class="text-text-secondary">{{ formatGender(scope.row.gender) }} / {{ scope.row.age || '-' }}岁</span>
          </template>
        </el-table-column>
        
        <el-table-column label="慢性病" min-width="200">
          <template #default="scope">
            <div class="flex flex-wrap gap-1.5">
              <el-tag 
                v-for="d in (scope.row.patient_diseases || [])" 
                :key="d.id" 
                size="small" 
                :color="getDiseaseColor(d.name)"
                class="border-none text-white font-medium"
              >
                {{ d.name }}
              </el-tag>
              <span v-if="!scope.row.patient_diseases?.length" class="text-text-muted text-sm">-</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                scope.row.user?.is_active 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-red-100 text-red-700'
              ]"
            >
              {{ scope.row.user?.is_active ? '活跃' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="注册时间" width="140">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ formatDate(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="最近访问" width="140">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ formatDate(scope.row.updated_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="80" align="center">
          <template #default>
            <el-dropdown trigger="click">
              <el-button circle class="action-btn">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>查看详情</el-dropdown-item>
                  <el-dropdown-item>编辑资料</el-dropdown-item>
                  <el-dropdown-item divided class="text-red-500">禁用账号</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="p-5 bg-white border-t border-secondary-100">
        <Pagination
          v-model:currentPage="page"
          v-model:pageSize="pageSize"
          :total="total"
          @change="fetchData"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Download, Plus, More } from '@element-plus/icons-vue'
import { getPatients } from '../../api/user_manage'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const filterStatus = ref('')
const loading = ref(false)
const users = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await getPatients({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      q: searchQuery.value
    })
    users.value = res.items || res
    total.value = res.total || users.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatDate = (iso: string) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString()
}

const formatGender = (gender: string) => {
  const map: any = { male: '男', female: '女', other: '其他' }
  return map[gender] || '未知'
}

const getDiseaseColor = (name: string) => {
  if (name.includes('糖尿病')) return '#8b5cf6'
  if (name.includes('高血压')) return '#ef4444'
  if (name.includes('心脏')) return '#f97316'
  return '#3b82f6'
}

onMounted(() => {
  fetchData()
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

:deep(.custom-select .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #E2E8F0;
}

.action-btn {
  background-color: #F1F5F9;
  border: none;
  color: #64748B;
}
.action-btn:hover {
  background-color: #E2E8F0;
  color: #3B82F6;
}
</style>
