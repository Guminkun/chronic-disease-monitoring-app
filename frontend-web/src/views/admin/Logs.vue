<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">系统日志</h2>
        <p class="text-gray-500 mt-1">审计和追踪所有系统操作</p>
      </div>
      <el-button type="primary" class="!bg-primary" icon="Download">导出日志</el-button>
    </div>

    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="p-6 border-b border-gray-100 flex gap-4 items-center">
        <div class="relative flex-1 max-w-lg">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户、操作内容..."
            prefix-icon="Search"
            clearable
            @clear="fetchLogs"
            @keyup.enter="fetchLogs"
          />
        </div>
        <el-select v-model="filterAction" placeholder="全部类型" class="w-32" clearable @change="fetchLogs">
          <el-option label="全部类型" value="" />
          <el-option label="用户登录" value="login" />
          <el-option label="上传报告" value="create_report" />
          <el-option label="删除报告" value="delete_report" />
          <el-option label="导出数据" value="export_data" />
          <el-option label="注销账号" value="delete_account" />
          <el-option label="创建用药" value="create_medication_plan" />
        </el-select>
      </div>

      <el-table
        :data="logs"
        style="width: 100%"
        :header-cell-style="{ background: '#F8FAFC', color: '#64748B' }"
        v-loading="loading"
      >
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="user" label="用户" width="150">
          <template #default="scope">
            <span class="font-medium text-gray-900">{{ scope.row.user }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" min-width="200" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getTypeTag(scope.row.type)" size="small" effect="light">{{ scope.row.typeText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'" size="small" effect="light">
              {{ scope.row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="140" />
      </el-table>

      <div class="p-6 border-t border-gray-100">
        <Pagination
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="total"
          @change="fetchLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Pagination from '../../components/Pagination.vue'
import request from '../../utils/request'

const searchQuery = ref('')
const filterAction = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const logs = ref<any[]>([])
const total = ref(0)

const fetchLogs = async () => {
  loading.value = true
  try {
    const res: any = await request({
      url: '/dashboard/logs',
      method: 'get',
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        action: filterAction.value || undefined,
        q: searchQuery.value || undefined
      }
    })
    logs.value = res.items || []
    total.value = res.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'lecture': 'success',
    'read': 'primary',
    'publish': 'warning',
    'edit': 'info',
    'info': 'info'
  }
  return map[type] || 'info'
}

onMounted(() => {
  fetchLogs()
})
</script>
