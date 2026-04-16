<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">系统日志</h2>
        <p class="text-gray-500 mt-1">审计和追踪所有系统操作</p>
      </div>
      <el-button type="primary" class="!bg-primary" icon="Download">导出日志</el-button>
    </div>

    <!-- Main Content -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="p-6 border-b border-gray-100 flex gap-4 items-center">
        <div class="relative flex-1 max-w-lg">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户、操作内容..."
            prefix-icon="Search"
            clearable
          />
        </div>
        <el-select v-model="filterType" placeholder="全部类型" class="w-32">
          <el-option label="全部类型" value="" />
          <el-option label="讲座" value="lecture" />
          <el-option label="阅读" value="read" />
          <el-option label="发布" value="publish" />
          <el-option label="编辑" value="edit" />
        </el-select>
        <el-button icon="Filter">更多筛选</el-button>
      </div>

      <!-- Table -->
      <el-table :data="logs" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#64748B' }">
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

      <!-- Pagination -->
      <div class="p-6 border-t border-gray-100">
        <Pagination
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="logs.length"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const logs = ref([
  {
    time: '2026-01-28 15:30:45',
    user: '医生 · 王明',
    action: '查看未有学时的研读课程',
    type: 'lecture',
    typeText: '讲座',
    status: 'success',
    ip: '192.168.1.100'
  },
  {
    time: '2026-01-28 15:28:12',
    user: '患者 · 李明',
    action: '上传检查报告 (血常规)',
    type: 'read',
    typeText: '阅读',
    status: 'success',
    ip: '192.168.1.101'
  },
  {
    time: '2026-01-28 15:25:30',
    user: '管理员 · 系统',
    action: '批准医生张红的注册申请',
    type: 'publish',
    typeText: '发布',
    status: 'success',
    ip: '192.168.1.102'
  },
  {
    time: '2026-01-28 15:20:15',
    user: '医生 · 李华',
    action: '创建患者王建的诊疗记录',
    type: 'read',
    typeText: '阅读',
    status: 'success',
    ip: '192.168.1.103'
  },
  {
    time: '2026-01-28 15:15:00',
    user: '患者 · 王建',
    action: '修改个人信息 (电话号码)',
    type: 'publish',
    typeText: '发布',
    status: 'success',
    ip: '192.168.1.104'
  }
])

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'lecture': 'success',
    'read': 'primary',
    'publish': 'warning',
    'edit': 'info'
  }
  return map[type] || 'info'
}
</script>
