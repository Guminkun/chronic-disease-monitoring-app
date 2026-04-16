<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-blue-50 flex">
    <!-- 左侧装饰区域 -->
    <div class="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-500 to-primary-700 relative overflow-hidden">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
      </div>
      <div class="relative z-10 flex flex-col justify-center px-16 text-white">
        <div class="flex items-center gap-4 mb-8">
          <div class="bg-white/20 backdrop-blur-sm p-3 rounded-2xl">
            <el-icon class="text-4xl"><Monitor /></el-icon>
          </div>
          <div>
            <h1 class="text-3xl font-bold">HealthMonitor</h1>
            <p class="text-white/80">慢病管理系统</p>
          </div>
        </div>
        <h2 class="text-4xl font-bold mb-6 leading-tight">
          智能慢病管理<br />
          <span class="text-white/80">守护健康每一天</span>
        </h2>
        <p class="text-lg text-white/70 mb-8 max-w-md">
          专业的慢性病管理平台，为医生和患者提供全方位的健康监测、用药提醒、数据分析服务。
        </p>
        <div class="flex gap-6">
          <div class="flex items-center gap-3">
            <div class="bg-white/20 p-2 rounded-lg">
              <el-icon><User /></el-icon>
            </div>
            <span class="text-sm">用户管理</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="bg-white/20 p-2 rounded-lg">
              <el-icon><DataBoard /></el-icon>
            </div>
            <span class="text-sm">数据分析</span>
          </div>
          <div class="flex items-center gap-3">
            <div class="bg-white/20 p-2 rounded-lg">
              <el-icon><FirstAidKit /></el-icon>
            </div>
            <span class="text-sm">用药提醒</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <!-- 移动端 Logo -->
        <div class="lg:hidden flex items-center justify-center gap-3 mb-8">
          <div class="bg-gradient-to-br from-primary-500 to-primary-600 p-2 rounded-xl">
            <el-icon class="text-white text-2xl"><Monitor /></el-icon>
          </div>
          <div>
            <h1 class="text-xl font-bold text-text-primary">HealthMonitor</h1>
            <p class="text-xs text-text-muted">慢病管理系统</p>
          </div>
        </div>

        <!-- 登录卡片 -->
        <div class="bg-white rounded-2xl shadow-xl p-8 border border-secondary-100">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-text-primary mb-2">欢迎回来</h2>
            <p class="text-text-muted">请登录您的账号</p>
          </div>

          <el-tabs v-model="activeTab" class="login-tabs">
            <el-tab-pane label="密码登录" name="password">
              <el-form :model="form" :rules="rules" ref="formRef" label-width="0px" class="mt-6">
                <el-form-item prop="username">
                  <el-input 
                    v-model="form.username" 
                    placeholder="请输入手机号"
                    size="large"
                    class="custom-input"
                  >
                    <template #prefix>
                      <el-icon class="text-text-muted"><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item prop="password" class="mt-4">
                  <el-input 
                    v-model="form.password" 
                    type="password" 
                    placeholder="请输入密码" 
                    show-password
                    size="large"
                    class="custom-input"
                  >
                    <template #prefix>
                      <el-icon class="text-text-muted"><Lock /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item class="mt-6">
                  <el-button 
                    type="primary" 
                    :loading="loading" 
                    class="w-full h-12 text-base font-medium rounded-xl"
                    @click="handleLogin"
                  >
                    登 录
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <!-- 测试账号提示 -->
          <div class="mt-6 p-4 bg-secondary-50 rounded-xl">
            <p class="text-xs text-text-muted text-center mb-2">测试账号</p>
            <div class="grid grid-cols-2 gap-3 text-xs">
              <div class="bg-white p-2 rounded-lg text-center border border-secondary-100">
                <p class="text-text-muted">管理员</p>
                <p class="text-text-primary font-medium">admin / admin</p>
              </div>
              <div class="bg-white p-2 rounded-lg text-center border border-secondary-100">
                <p class="text-text-muted">医生</p>
                <p class="text-text-primary font-medium">13900000001 / 123456</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部信息 -->
        <p class="text-center text-text-muted text-sm mt-8">
          © 2024 HealthMonitor. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { User, Lock, Monitor, DataBoard, FirstAidKit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('password')
const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(form)
        
        const role = userStore.role
        
        if (role === 'patient') {
          ElMessage.warning('患者请使用移动端 App 登录')
          userStore.logout()
          return
        }

        ElMessage.success('登录成功')
        // Redirect based on role
        if (role === 'admin') {
          router.push('/admin')
        } else if (role === 'doctor') {
          router.push('/doctor')
        }
      } catch (error) {
        ElMessage.error('登录失败，请检查账号密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background-color: #3B82F6;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  color: #64748B;
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #3B82F6;
}

.custom-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #E2E8F0;
  padding: 4px 12px;
}

.custom-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
}
</style>
