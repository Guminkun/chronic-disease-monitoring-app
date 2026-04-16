<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">医生审核管理</h2>
        <p class="text-gray-500 mt-1">管理医生注册申请和审核</p>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">待审核</div>
        <div class="text-3xl font-bold text-gray-900">2</div>
      </div>
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">已批准</div>
        <div class="text-3xl font-bold text-green-500">0</div>
      </div>
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div class="text-gray-500 text-sm font-medium mb-4">已拒绝</div>
        <div class="text-3xl font-bold text-red-500">0</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <!-- Filters -->
      <div class="p-6 border-b border-gray-100 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div class="relative w-full md:w-2/3">
          <el-input
            v-model="searchQuery"
            placeholder="搜索医生名称、执业证书、医院..."
            :prefix-icon="Search"
            clearable
          />
        </div>
        <el-select v-model="filterStatus" placeholder="全部状态" class="w-full md:w-32">
          <el-option label="全部状态" value="" />
          <el-option label="待审核" value="pending" />
          <el-option label="已批准" value="approved" />
          <el-option label="已拒绝" value="rejected" />
        </el-select>
      </div>

      <!-- Doctor Cards List -->
      <div class="p-6 space-y-6">
        <div v-for="doc in doctors" :key="doc.id" class="border border-gray-100 rounded-xl p-6 hover:shadow-md transition-shadow">
          <!-- Card Header -->
          <div class="flex justify-between items-start mb-6">
            <div class="flex items-center gap-4">
              <h3 class="text-xl font-bold text-gray-900">{{ doc.name }}</h3>
              <el-tag type="warning" effect="light" round>待审核</el-tag>
            </div>
            <el-tag type="warning" effect="plain" round class="border-0 bg-yellow-50 text-yellow-600">
              待审核
            </el-tag>
          </div>
          
          <div class="text-gray-500 text-sm mb-6">
            执业证号: <span class="text-gray-900">{{ doc.licenseNo }}</span>
          </div>

          <!-- Card Body -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div>
              <div class="text-xs text-gray-400 mb-1">医院</div>
              <div class="text-sm font-medium text-gray-900">{{ doc.hospital }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-1">科室</div>
              <div class="text-sm font-medium text-gray-900">{{ doc.department }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-1">联系电话</div>
              <div class="text-sm font-medium text-gray-900">{{ doc.phone }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-1">申请日期</div>
              <div class="text-sm font-medium text-gray-900">{{ doc.applyDate }}</div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <div class="text-xs text-gray-400 mb-1">教育背景</div>
              <div class="text-sm text-gray-600">{{ doc.education }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-400 mb-1">工作经验</div>
              <div class="text-sm text-gray-600">{{ doc.experience }}</div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-4 border-t border-gray-50 pt-6">
            <el-button class="flex-1" :icon="View">查看详情</el-button>
            <el-button class="flex-1 !bg-green-500 !border-green-500" type="success" :icon="Check">批准</el-button>
            <el-button class="flex-1" type="danger" plain :icon="Close">拒绝</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, View, Check, Close } from '@element-plus/icons-vue'

const searchQuery = ref('')
const filterStatus = ref('')

const doctors = ref([
  {
    id: 1,
    name: '王医生',
    licenseNo: '110310101010101',
    hospital: '北京协和医院',
    department: '心内科',
    phone: '13811111111',
    applyDate: '2026-01-20',
    education: '北京大学医学部 临床医学 (硕士)',
    experience: '15年心内科工作经验，擅长高血压、冠心病诊疗',
    status: 'pending'
  }
])
</script>
