<template>
  <div class="min-h-screen bg-white">
    <!-- Navbar -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-secondary-100">
      <div class="container mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
          <div class="bg-gradient-to-br from-primary-500 to-primary-600 p-2 rounded-xl">
            <el-icon class="text-white text-xl"><Monitor /></el-icon>
          </div>
          <span class="text-xl font-bold text-text-primary">HealthMonitor</span>
        </div>
        <div class="hidden md:flex items-center space-x-8">
          <a href="#features" class="text-text-secondary hover:text-primary-500 transition-colors font-medium">功能特性</a>
          <a href="#benefits" class="text-text-secondary hover:text-primary-500 transition-colors font-medium">核心优势</a>
          <a href="#contact" class="text-text-secondary hover:text-primary-500 transition-colors font-medium">联系我们</a>
        </div>
        <router-link to="/login" 
          class="px-6 py-2.5 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-primary-500/25 transition-all">
          登录系统
        </router-link>
      </div>
    </nav>

    <!-- Hero Section -->
    <header class="pt-24 pb-16 md:pt-32 md:pb-24 bg-gradient-to-br from-primary-50 via-white to-blue-50 overflow-hidden">
      <div class="container mx-auto px-6">
        <div class="flex flex-col-reverse md:flex-row items-center gap-12">
          <div class="md:w-1/2 text-center md:text-left">
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-600 rounded-full text-sm font-medium mb-6">
              <el-icon><Star /></el-icon>
              专业慢病管理平台
            </div>
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-text-primary leading-tight mb-6">
              智能慢病管理
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-primary-600">
                守护健康
              </span>
            </h1>
            <p class="text-lg text-text-secondary mb-8 max-w-xl">
              为医疗机构和患者提供全方位的慢性病管理解决方案，实时监测、智能分析、精准服务，助力提升健康管理效率。
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
              <router-link to="/login" 
                class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 transition-all transform hover:-translate-y-0.5">
                立即开始使用
              </router-link>
              <a href="#features" 
                class="px-8 py-4 bg-white text-primary-600 border-2 border-primary-200 rounded-xl font-medium hover:border-primary-300 hover:bg-primary-50 transition-all">
                了解更多功能
              </a>
            </div>
            <!-- Stats -->
            <div class="flex gap-8 mt-12 justify-center md:justify-start">
              <div class="text-center">
                <div class="text-3xl font-bold text-text-primary">10K+</div>
                <div class="text-sm text-text-muted">活跃用户</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-text-primary">500+</div>
                <div class="text-sm text-text-muted">合作医院</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-text-primary">99.9%</div>
                <div class="text-sm text-text-muted">系统可用率</div>
              </div>
            </div>
          </div>
          <div class="md:w-1/2 relative">
            <!-- Decorative Elements -->
            <div class="absolute -top-10 -right-10 w-72 h-72 bg-primary-200 rounded-full opacity-30 blur-3xl"></div>
            <div class="absolute -bottom-10 -left-10 w-72 h-72 bg-blue-200 rounded-full opacity-30 blur-3xl"></div>
            <!-- Main Card -->
            <div class="relative bg-white rounded-3xl shadow-2xl p-6 border border-secondary-100">
              <div class="flex items-center justify-between mb-6">
                <div>
                  <h3 class="font-semibold text-text-primary">健康数据概览</h3>
                  <p class="text-sm text-text-muted">实时监测指标</p>
                </div>
                <div class="flex items-center gap-2 px-3 py-1.5 bg-green-100 text-green-600 rounded-full text-sm">
                  <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  正常
                </div>
              </div>
              <!-- Chart Placeholder -->
              <div class="bg-gradient-to-br from-primary-50 to-blue-50 rounded-2xl p-4 mb-4">
                <div class="flex items-end justify-between h-32 gap-2">
                  <div class="flex-1 bg-primary-300 rounded-t-lg" style="height: 40%"></div>
                  <div class="flex-1 bg-primary-400 rounded-t-lg" style="height: 60%"></div>
                  <div class="flex-1 bg-primary-300 rounded-t-lg" style="height: 45%"></div>
                  <div class="flex-1 bg-primary-500 rounded-t-lg" style="height: 80%"></div>
                  <div class="flex-1 bg-primary-400 rounded-t-lg" style="height: 65%"></div>
                  <div class="flex-1 bg-primary-300 rounded-t-lg" style="height: 50%"></div>
                  <div class="flex-1 bg-primary-500 rounded-t-lg" style="height: 90%"></div>
                </div>
                <div class="flex justify-between mt-2 text-xs text-text-muted">
                  <span>周一</span>
                  <span>周二</span>
                  <span>周三</span>
                  <span>周四</span>
                  <span>周五</span>
                  <span>周六</span>
                  <span>周日</span>
                </div>
              </div>
              <!-- Metrics -->
              <div class="grid grid-cols-3 gap-3">
                <div class="bg-secondary-50 rounded-xl p-3 text-center">
                  <el-icon class="text-primary-500 text-xl mb-1"><Monitor /></el-icon>
                  <div class="text-lg font-bold text-text-primary">72</div>
                  <div class="text-xs text-text-muted">心率</div>
                </div>
                <div class="bg-secondary-50 rounded-xl p-3 text-center">
                  <el-icon class="text-red-500 text-xl mb-1"><FirstAidKit /></el-icon>
                  <div class="text-lg font-bold text-text-primary">120/80</div>
                  <div class="text-xs text-text-muted">血压</div>
                </div>
                <div class="bg-secondary-50 rounded-xl p-3 text-center">
                  <el-icon class="text-amber-500 text-xl mb-1"><Sunny /></el-icon>
                  <div class="text-lg font-bold text-text-primary">5.6</div>
                  <div class="text-xs text-text-muted">血糖</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-white">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-text-primary mb-4">核心功能特性</h2>
          <p class="text-text-secondary max-w-2xl mx-auto">
            全方位的慢病管理解决方案，为医生和患者提供便捷、高效的服务体验
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-primary-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><DataBoard /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">实时数据监测</h3>
            <p class="text-text-secondary leading-relaxed">
              实时追踪患者健康指标，包括血压、血糖、心率等关键数据，及时发现异常情况。
            </p>
          </div>
          <!-- Feature 2 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-green-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><FirstAidKit /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">智能用药提醒</h3>
            <p class="text-text-secondary leading-relaxed">
              自动化的用药提醒系统，确保患者按时服药，提高治疗依从性和效果。
            </p>
          </div>
          <!-- Feature 3 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-amber-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><Document /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">健康报告管理</h3>
            <p class="text-text-secondary leading-relaxed">
              支持上传和管理各类检查报告，OCR智能识别，方便医生查看和分析。
            </p>
          </div>
          <!-- Feature 4 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><User /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">医患绑定管理</h3>
            <p class="text-text-secondary leading-relaxed">
              便捷的医患关系建立，支持扫码绑定，医生可管理多名患者健康数据。
            </p>
          </div>
          <!-- Feature 5 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-cyan-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><ChatDotRound /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">在线健康咨询</h3>
            <p class="text-text-secondary leading-relaxed">
              内置即时通讯功能，患者可随时向医生咨询，获得专业健康指导。
            </p>
          </div>
          <!-- Feature 6 -->
          <div class="group p-8 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:shadow-xl hover:shadow-primary-500/5 transition-all">
            <div class="w-14 h-14 bg-gradient-to-br from-rose-500 to-rose-600 rounded-2xl flex items-center justify-center mb-6 text-white shadow-lg shadow-rose-500/25 group-hover:scale-110 transition-transform">
              <el-icon class="text-2xl"><Reading /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-text-primary mb-3">健康宣教内容</h3>
            <p class="text-text-secondary leading-relaxed">
              丰富的健康知识库，提供疾病科普、饮食建议、运动指导等内容。
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Benefits Section -->
    <section id="benefits" class="py-20 bg-gradient-to-br from-primary-500 to-primary-700 relative overflow-hidden">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
      </div>
      <div class="container mx-auto px-6 relative z-10">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">为什么选择我们？</h2>
          <p class="text-white/80 max-w-2xl mx-auto">
            我们致力于提供最优质的慢病管理服务，让健康管理更简单、更高效
          </p>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center p-8">
            <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6">
              <el-icon class="text-white text-4xl"><Lock /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">安全可靠</h3>
            <p class="text-white/70">
              采用银行级数据加密技术，严格遵循医疗数据安全标准，保护患者隐私
            </p>
          </div>
          <div class="text-center p-8">
            <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6">
              <el-icon class="text-white text-4xl"><Timer /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">高效便捷</h3>
            <p class="text-white/70">
              简化工作流程，减少行政负担，让医护人员专注于患者护理
            </p>
          </div>
          <div class="text-center p-8">
            <div class="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6">
              <el-icon class="text-white text-4xl"><TrendCharts /></el-icon>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">数据驱动</h3>
            <p class="text-white/70">
              智能数据分析，可视化健康趋势，辅助医生做出更准确的诊断决策
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section id="contact" class="py-20 bg-secondary-50">
      <div class="container mx-auto px-6">
        <div class="bg-white rounded-3xl shadow-xl p-8 md:p-12 border border-secondary-100">
          <div class="flex flex-col md:flex-row items-center justify-between gap-8">
            <div class="text-center md:text-left">
              <h2 class="text-3xl font-bold text-text-primary mb-4">准备好开始了吗？</h2>
              <p class="text-text-secondary max-w-lg">
                立即加入 HealthMonitor，体验智能慢病管理带来的便捷与高效。我们的团队随时为您提供支持。
              </p>
            </div>
            <div class="flex flex-col sm:flex-row gap-4">
              <router-link to="/login" 
                class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-medium shadow-lg shadow-primary-500/25 hover:shadow-xl transition-all text-center">
                立即登录
              </router-link>
              <a href="mailto:support@healthmonitor.com" 
                class="px-8 py-4 bg-white text-primary-600 border-2 border-primary-200 rounded-xl font-medium hover:border-primary-300 hover:bg-primary-50 transition-all text-center">
                联系我们
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-text-primary text-white py-12">
      <div class="container mx-auto px-6">
        <div class="flex flex-col md:flex-row justify-between items-center gap-6">
          <div class="flex items-center gap-3">
            <div class="bg-white/10 p-2 rounded-xl">
              <el-icon class="text-xl"><Monitor /></el-icon>
            </div>
            <div>
              <span class="font-bold text-lg">HealthMonitor</span>
              <p class="text-sm text-white/60">慢病管理系统</p>
            </div>
          </div>
          <div class="flex items-center gap-8 text-sm text-white/60">
            <a href="#" class="hover:text-white transition-colors">隐私政策</a>
            <a href="#" class="hover:text-white transition-colors">服务条款</a>
            <a href="#" class="hover:text-white transition-colors">帮助中心</a>
          </div>
          <p class="text-sm text-white/40">© 2024 HealthMonitor. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import {
  Monitor,
  Star,
  DataBoard,
  FirstAidKit,
  Document,
  User,
  ChatDotRound,
  Reading,
  Lock,
  Timer,
  TrendCharts,
  Sunny
} from '@element-plus/icons-vue'
</script>

<style scoped>
/* Smooth scroll */
html {
  scroll-behavior: smooth;
}
</style>
