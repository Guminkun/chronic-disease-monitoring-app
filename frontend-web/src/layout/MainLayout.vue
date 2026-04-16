<template>
  <el-container class="layout-container h-screen w-full overflow-hidden bg-background">
    <!-- 明亮风格侧边栏 -->
    <el-aside width="260px" class="bg-white flex flex-col border-r border-sidebar-border h-full flex-shrink-0 shadow-sidebar">
      <!-- Logo 区域 -->
      <div class="h-20 flex items-center px-6 border-b border-secondary-100 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="bg-gradient-to-br from-primary-500 to-primary-600 p-2 rounded-xl shadow-lg">
            <el-icon class="text-white text-xl"><Monitor /></el-icon>
          </div>
          <div>
            <h1 class="text-text-primary font-bold text-lg leading-tight">HealthMonitor</h1>
            <p class="text-xs text-text-muted">慢病管理后台</p>
          </div>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <el-scrollbar class="flex-1 py-4">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical w-full border-none bg-white px-3"
          background-color="#FFFFFF"
          text-color="#64748B"
          active-text-color="#3B82F6"
          router
        >
          <!-- Admin Menu -->
          <template v-if="userStore.role === 'admin'">
            <div class="px-4 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">概览</div>
            <el-menu-item index="/admin" class="menu-item">
              <el-icon><DataBoard /></el-icon>
              <span>数据概览</span>
            </el-menu-item>
            
            <div class="px-4 py-2 mt-4 text-xs font-semibold text-text-muted uppercase tracking-wider">系统管理</div>
            <el-menu-item index="/admin/users" class="menu-item">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/doctor-approval" class="menu-item">
              <el-icon><CircleCheck /></el-icon>
              <span>医生审核</span>
            </el-menu-item>
            <el-menu-item index="/admin/bindings" class="menu-item">
              <el-icon><Link /></el-icon>
              <span>医患绑定</span>
            </el-menu-item>
            
            <div class="px-4 py-2 mt-4 text-xs font-semibold text-text-muted uppercase tracking-wider">数据管理</div>
            <el-menu-item index="/admin/medications" class="menu-item">
              <el-icon><FirstAidKit /></el-icon>
              <span>药品库</span>
            </el-menu-item>
            <el-menu-item index="/admin/diseases" class="menu-item">
              <el-icon><Monitor /></el-icon>
              <span>慢性病字典</span>
            </el-menu-item>
            <el-menu-item index="/admin/education" class="menu-item">
              <el-icon><Reading /></el-icon>
              <span>健康宣教</span>
            </el-menu-item>
            <el-menu-item index="/admin/usage-guides" class="menu-item">
              <el-icon><Collection /></el-icon>
              <span>使用说明</span>
            </el-menu-item>
            <el-menu-item index="/admin/reports" class="menu-item">
              <el-icon><Document /></el-icon>
              <span>检查报告</span>
            </el-menu-item>
            
            <div class="px-4 py-2 mt-4 text-xs font-semibold text-text-muted uppercase tracking-wider">系统设置</div>
            <el-menu-item index="/admin/analytics" class="menu-item">
              <el-icon><TrendCharts /></el-icon>
              <span>数据统计</span>
            </el-menu-item>
            <el-menu-item index="/admin/logs" class="menu-item">
              <el-icon><List /></el-icon>
              <span>日志管理</span>
            </el-menu-item>
            <el-menu-item index="/admin/feedback" class="menu-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>意见反馈</span>
            </el-menu-item>
            <el-menu-item index="/admin/permissions" class="menu-item">
              <el-icon><Lock /></el-icon>
              <span>权限管理</span>
            </el-menu-item>
          </template>
  
          <!-- Doctor Menu -->
          <template v-if="userStore.role === 'doctor'">
            <div class="px-4 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">工作台</div>
            <el-menu-item index="/doctor" class="menu-item">
              <el-icon><DataBoard /></el-icon>
              <span>工作台</span>
            </el-menu-item>
            <el-menu-item index="/doctor/patients" class="menu-item">
              <el-icon><User /></el-icon>
              <span>我的患者</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <!-- 用户信息区域 -->
      <div class="p-4 border-t border-secondary-100 flex-shrink-0">
        <div class="flex items-center gap-3 px-3 py-3 bg-secondary-50 rounded-xl">
          <el-avatar :size="40" class="bg-primary-500 text-white font-medium">
            {{ userStore.user?.full_name?.charAt(0) || 'A' }}
          </el-avatar>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-text-primary truncate">{{ userStore.user?.full_name || '用户' }}</p>
            <p class="text-xs text-text-muted">{{ roleName }}</p>
          </div>
          <button 
            class="p-2 text-text-muted hover:text-danger-500 hover:bg-danger-50 rounded-lg transition-colors"
            @click="handleLogout"
            title="退出登录"
          >
            <el-icon><SwitchButton /></el-icon>
          </button>
        </div>
      </div>
    </el-aside>
    
    <!-- 主内容区域 -->
    <el-container class="h-full flex flex-col min-w-0">
      <!-- 顶部导航栏 -->
      <el-header class="bg-white border-b border-secondary-100 h-16 flex items-center justify-between px-8 shadow-sm z-10 flex-shrink-0">
        <div class="flex items-center gap-4">
          <h2 class="text-xl font-bold text-text-primary">{{ currentRouteName }}</h2>
        </div>
        <div class="flex items-center gap-6">
          <!-- 快捷操作 -->
          <div class="flex items-center gap-2">
            <button class="p-2 text-text-muted hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors">
              <el-icon size="20"><Bell /></el-icon>
            </button>
            <button class="p-2 text-text-muted hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors">
              <el-icon size="20"><Setting /></el-icon>
            </button>
          </div>
        </div>
      </el-header>
      
      <!-- 页面内容 -->
      <el-main class="p-6 overflow-y-auto flex-1 bg-background">
        <div class="min-w-[800px]">
          <router-view></router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { 
  DataBoard, 
  User, 
  Monitor, 
  SwitchButton, 
  CircleCheck, 
  FirstAidKit, 
  Document,
  Link,
  TrendCharts,
  List,
  Lock,
  Reading,
  Bell,
  Setting,
  ChatDotRound,
  Collection
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const currentRouteName = computed(() => {
  const nameMap: Record<string, string> = {
    'Dashboard': '数据概览',
    'UserManagement': '用户管理',
    'DoctorApproval': '医生审核',
    'MedicationLibrary': '药品库管理',
    'DiseaseManagement': '慢性病字典',
    'HealthEducation': '健康宣教',
    'ReportManagement': '检查报告',
    'Bindings': '医患绑定',
    'Analytics': '数据统计',
    'Logs': '日志管理',
    'Permissions': '权限管理',
    'FeedbackManagement': '意见反馈',
    'SkillManagement': '技能说明',
    'DoctorDashboard': '医生工作台',
    'MyPatients': '我的患者'
  }
  return nameMap[route.name as string] || route.name as string
})

const roleName = computed(() => {
  switch (userStore.role) {
    case 'admin': return '管理员'
    case 'doctor': return '医生'
    default: return '用户'
  }
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
:deep(.el-menu) {
  border-right: none !important;
}

:deep(.menu-item) {
  margin: 2px 0;
  border-radius: 10px;
  height: 44px;
  line-height: 44px;
  width: auto;
  transition: all 0.2s ease;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
  color: #3B82F6 !important;
  font-weight: 500;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #3B82F6 !important;
}

:deep(.el-menu-item:hover:not(.is-active)) {
  background-color: #F8FAFC !important;
  color: #1E293B !important;
}
</style>
