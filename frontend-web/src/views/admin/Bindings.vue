<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900">医患绑定关系管理</h2>
      <p class="text-gray-500 mt-1">管理医生和患者的绑定关系，保障数据安全</p>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-blue-50 rounded-xl p-6 border border-blue-100 flex flex-col justify-between h-32 transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start">
          <span class="text-gray-600 font-medium">全部绑定</span>
          <el-icon class="text-blue-500 text-xl"><Link /></el-icon>
        </div>
        <div>
          <h3 class="text-3xl font-bold text-gray-900 mb-1">2</h3>
          <p class="text-xs text-gray-500">当前系统总绑定数</p>
        </div>
      </div>
      
      <div class="bg-emerald-50 rounded-xl p-6 border border-emerald-100 flex flex-col justify-between h-32 transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start">
          <span class="text-gray-600 font-medium">生效中</span>
          <el-icon class="text-emerald-500 text-xl"><CircleCheck /></el-icon>
        </div>
        <div>
          <h3 class="text-3xl font-bold text-gray-900 mb-1">2</h3>
          <p class="text-xs text-gray-500">正在进行的绑定关系</p>
        </div>
      </div>

      <div class="bg-gray-50 rounded-xl p-6 border border-gray-100 flex flex-col justify-between h-32 transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start">
          <span class="text-gray-600 font-medium">已解绑</span>
          <el-icon class="text-gray-500 text-xl"><CircleClose /></el-icon>
        </div>
        <div>
          <h3 class="text-3xl font-bold text-gray-900 mb-1">1</h3>
          <p class="text-xs text-gray-500">历史绑定记录</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <!-- Tabs -->
      <div class="border-b border-gray-100">
        <div class="flex">
          <button 
            class="px-6 py-4 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'active' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="activeTab = 'active'"
          >
            绑定关系 (2)
          </button>
          <button 
            class="px-6 py-4 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'logs' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="activeTab = 'logs'"
          >
            操作日志 (2)
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="p-6 border-b border-gray-100 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div class="relative w-full md:w-96">
          <el-input
            v-model="searchQuery"
            placeholder="搜索医生名称、患者名称、手机号..."
            :prefix-icon="Search"
            clearable
          />
        </div>
        <el-select v-model="filterStatus" placeholder="全部状态" class="w-full md:w-32">
          <el-option label="全部状态" value="" />
          <el-option label="生效中" value="active" />
          <el-option label="已解绑" value="inactive" />
        </el-select>
      </div>

      <!-- List -->
      <div class="p-6 grid gap-4">
        <div v-for="item in bindings" :key="item.id" class="border border-gray-100 rounded-xl p-6 hover:shadow-md transition-all hover:-translate-y-0.5 bg-white">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div class="flex items-center gap-8 flex-1">
              <!-- Doctor -->
              <div class="flex items-center gap-4 min-w-[200px]">
                <div class="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
                  <el-icon><Avatar /></el-icon>
                </div>
                <div>
                  <div class="text-xs text-gray-500 mb-0.5">医生</div>
                  <div class="font-bold text-gray-900 text-base">{{ item.doctorName }}</div>
                  <div class="text-xs text-gray-400">{{ item.doctorPhone }}</div>
                </div>
              </div>
              
              <!-- Connection Line (Visual) -->
              <div class="hidden md:flex flex-1 items-center gap-2">
                <div class="h-[1px] flex-1 bg-gray-200"></div>
                <div class="px-3 py-1 bg-gray-50 rounded-full text-xs text-gray-500 whitespace-nowrap">
                  {{ item.type }}
                </div>
                <div class="h-[1px] flex-1 bg-gray-200"></div>
              </div>

              <!-- Patient -->
              <div class="flex items-center gap-4 min-w-[200px] justify-end">
                <div class="text-right">
                  <div class="text-xs text-gray-500 mb-0.5">患者</div>
                  <div class="font-bold text-gray-900 text-base">{{ item.patientName }}</div>
                  <div class="text-xs text-gray-400">{{ item.patientPhone }}</div>
                </div>
                <div class="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center text-green-500">
                  <el-icon><User /></el-icon>
                </div>
              </div>
            </div>

            <!-- Actions & Status -->
            <div class="flex items-center gap-4 pl-6 border-l border-gray-100">
              <div class="text-right mr-4">
                <div class="text-xs text-gray-400 mb-1">绑定日期</div>
                <div class="text-sm font-medium text-gray-700">{{ item.date }}</div>
              </div>
              
              <el-tag :type="item.status === 'active' ? 'success' : 'info'" effect="light" round class="px-4">
                {{ item.status === 'active' ? '生效中' : '已解绑' }}
              </el-tag>
              
              <el-dropdown trigger="click">
                <el-button circle plain :icon="More" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="View">查看详情</el-dropdown-item>
                    <el-dropdown-item :icon="Link" v-if="item.status === 'active'" class="text-red-500">解除绑定</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Pagination -->
      <div class="p-6">
        <Pagination
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="bindings.length"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, View, Link, CircleCheck, CircleClose, Avatar, User, More } from '@element-plus/icons-vue'
import Pagination from '../../components/Pagination.vue'

const activeTab = ref('active')
const searchQuery = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const bindings = ref([
  {
    id: 1,
    doctorName: '王医生',
    doctorPhone: '13900000001',
    patientName: '张三',
    patientPhone: '13800000001',
    type: '二维码绑定',
    date: '2026-01-20',
    status: 'active'
  },
  {
    id: 2,
    doctorName: '李医生',
    doctorPhone: '13900000002',
    patientName: '李四',
    patientPhone: '13800000002',
    type: '系统分配',
    date: '2026-01-18',
    status: 'active'
  }
])
</script>
