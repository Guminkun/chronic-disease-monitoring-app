<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">检查报告管理</h2>
        <p class="text-gray-500 mt-1">管理所有患者上传的检查报告数据</p>
      </div>
      <el-button type="primary" class="!bg-primary" icon="Download">导出报告</el-button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">总报告数</div>
        <div class="text-3xl font-bold text-gray-900">2</div>
      </div>
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">OCR识别</div>
        <div class="text-3xl font-bold text-blue-500">1</div>
      </div>
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">手动录入</div>
        <div class="text-3xl font-bold text-green-500">1</div>
      </div>
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">异常数据</div>
        <div class="text-3xl font-bold text-red-500">1</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="p-6 border-b border-gray-100 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div class="relative w-full md:w-1/2">
          <el-input
            v-model="searchQuery"
            placeholder="搜索用户名、用户ID、报告类型..."
            prefix-icon="Search"
            clearable
          />
        </div>
        <div class="flex gap-4 w-full md:w-auto">
          <el-select v-model="filterType" placeholder="全部类型" class="w-full md:w-32">
            <el-option label="全部类型" value="" />
            <el-option label="血常规" value="blood_routine" />
            <el-option label="血糖检测" value="blood_sugar" />
          </el-select>
          <el-select v-model="filterMethod" placeholder="全部方式" class="w-full md:w-32">
            <el-option label="全部方式" value="" />
            <el-option label="OCR" value="ocr" />
            <el-option label="手动录入" value="manual" />
          </el-select>
        </div>
      </div>

      <!-- Table -->
      <el-table :data="reports" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#64748B' }">
        <el-table-column prop="patientName" label="患者姓名" width="120">
          <template #default="scope">
            <span class="font-medium text-gray-900">{{ scope.row.patientName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="报告类型" width="150" />
        <el-table-column prop="disease" label="关联病种" width="150" />
        <el-table-column prop="date" label="检查日期" width="150" />
        <el-table-column prop="method" label="上传方式" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.method === 'OCR' ? 'primary' : 'success'" effect="light" class="border-0" :class="scope.row.method === 'OCR' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'">
              {{ scope.row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'normal' ? 'success' : 'danger'" effect="light" class="border-0" :class="scope.row.status === 'normal' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
              {{ scope.row.status === 'normal' ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="150" align="right">
          <template #default>
            <el-button link type="info" :icon="View" />
            <el-button link type="info" :icon="Edit" />
            <el-button link type="danger" :icon="Delete" />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { View, Edit, Delete } from '@element-plus/icons-vue'

const searchQuery = ref('')
const filterType = ref('')
const filterMethod = ref('')

const reports = ref([
  {
    id: 1,
    patientName: '张三',
    type: '血常规',
    disease: '高血压',
    date: '2026-01-25',
    method: 'OCR',
    status: 'normal'
  },
  {
    id: 2,
    patientName: '张三',
    type: '血糖检测',
    disease: '2型糖尿病',
    date: '2026-01-20',
    method: 'manual',
    status: 'abnormal'
  }
])
</script>
