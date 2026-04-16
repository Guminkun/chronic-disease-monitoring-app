<template>
  <div class="demo-container">
    <div class="demo-header">
      <h1 class="demo-title">分页组件演示</h1>
      <p class="demo-subtitle">功能完善的自定义分页组件</p>
    </div>

    <div class="demo-section">
      <h2 class="section-title">基础用法</h2>
      <p class="section-desc">包含数据总量、页码选择器、分页控件和跳转功能</p>
      
      <div class="demo-card">
        <div class="demo-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>姓名</th>
                <th>年龄</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in currentData" :key="item.id">
                <td>{{ item.id }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.age }}</td>
                <td>
                  <span :class="['status-badge', item.status]">
                    {{ item.status === 'active' ? '活跃' : '禁用' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <Pagination
          v-model:currentPage="currentPage"
          v-model:pageSize="pageSize"
          :total="total"
          @change="handlePageChange"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2 class="section-title">自定义每页条数选项</h2>
      <p class="section-desc">可以通过 pageSizeOptions 属性自定义每页条数的选项</p>
      
      <div class="demo-card">
        <div class="demo-stats">
          <div class="stat-item">
            <span class="stat-label">当前页:</span>
            <span class="stat-value">{{ customCurrentPage }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">每页条数:</span>
            <span class="stat-value">{{ customPageSize }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">数据总量:</span>
            <span class="stat-value">{{ customTotal }}</span>
          </div>
        </div>
        
        <Pagination
          v-model:currentPage="customCurrentPage"
          v-model:pageSize="customPageSize"
          :total="customTotal"
          :page-size-options="[5, 10, 20, 50, 100]"
          @change="handleCustomPageChange"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2 class="section-title">少量数据</h2>
      <p class="section-desc">当数据总量较少时，页码会智能展示</p>
      
      <div class="demo-card">
        <Pagination
          v-model:currentPage="smallCurrentPage"
          v-model:pageSize="smallPageSize"
          :total="35"
          @change="handleSmallPageChange"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2 class="section-title">大量数据</h2>
      <p class="section-desc">当页码较多时，会自动显示省略号</p>
      
      <div class="demo-card">
        <Pagination
          v-model:currentPage="largeCurrentPage"
          v-model:pageSize="largePageSize"
          :total="1000"
          @change="handleLargePageChange"
        />
      </div>
    </div>

    <div class="demo-section">
      <h2 class="section-title">响应式布局</h2>
      <p class="section-desc">调整浏览器窗口大小查看响应式效果</p>
      
      <div class="demo-card">
        <Pagination
          v-model:currentPage="responsivePage"
          v-model:pageSize="responsiveSize"
          :total="500"
        />
      </div>
    </div>

    <div class="api-section">
      <h2 class="section-title">API 文档</h2>
      
      <div class="api-table">
        <h3>Props</h3>
        <table>
          <thead>
            <tr>
              <th>属性名</th>
              <th>说明</th>
              <th>类型</th>
              <th>默认值</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>total</td>
              <td>数据总条数</td>
              <td>number</td>
              <td>0</td>
            </tr>
            <tr>
              <td>currentPage</td>
              <td>当前页码（支持 v-model）</td>
              <td>number</td>
              <td>1</td>
            </tr>
            <tr>
              <td>pageSize</td>
              <td>每页显示条数（支持 v-model）</td>
              <td>number</td>
              <td>10</td>
            </tr>
            <tr>
              <td>pageSizeOptions</td>
              <td>每页条数选项</td>
              <td>number[]</td>
              <td>[10, 25, 50]</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="api-table">
        <h3>Events</h3>
        <table>
          <thead>
            <tr>
              <th>事件名</th>
              <th>说明</th>
              <th>参数</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>update:currentPage</td>
              <td>当前页码改变时触发</td>
              <td>(page: number)</td>
            </tr>
            <tr>
              <td>update:pageSize</td>
              <td>每页条数改变时触发</td>
              <td>(size: number)</td>
            </tr>
            <tr>
              <td>change</td>
              <td>页码或每页条数改变时触发</td>
              <td>(page: number, pageSize: number)</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Pagination from '../components/Pagination.vue'

const generateMockData = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `用户${i + 1}`,
    age: Math.floor(Math.random() * 50) + 18,
    status: Math.random() > 0.3 ? 'active' : 'inactive'
  }))
}

const allData = generateMockData(100)

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

const currentData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allData.slice(start, end)
})

const handlePageChange = (page: number, size: number) => {
  console.log('页码变化:', page, '每页条数:', size)
}

const customCurrentPage = ref(1)
const customPageSize = ref(10)
const customTotal = ref(200)

const handleCustomPageChange = (page: number, size: number) => {
  console.log('自定义分页变化:', page, size)
}

const smallCurrentPage = ref(1)
const smallPageSize = ref(10)

const handleSmallPageChange = (page: number) => {
  console.log('少量数据分页:', page)
}

const largeCurrentPage = ref(1)
const largePageSize = ref(10)

const handleLargePageChange = (page: number) => {
  console.log('大量数据分页:', page)
}

const responsivePage = ref(1)
const responsiveSize = ref(25)
</script>

<style scoped>
.demo-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px;
}

.demo-header {
  margin-bottom: 32px;
}

.demo-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.demo-subtitle {
  font-size: 16px;
  color: #64748b;
}

.demo-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.section-desc {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 16px;
}

.demo-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.demo-table {
  margin-bottom: 24px;
  overflow-x: auto;
}

.demo-table table {
  width: 100%;
  border-collapse: collapse;
}

.demo-table th,
.demo-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.demo-table th {
  font-weight: 600;
  color: #475569;
  background: #f8fafc;
  font-size: 14px;
}

.demo-table td {
  color: #1e293b;
  font-size: 14px;
}

.demo-table tr:hover td {
  background: #f8fafc;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.demo-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #3b82f6;
}

.api-section {
  margin-top: 48px;
}

.api-table {
  margin-bottom: 32px;
}

.api-table h3 {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 12px;
}

.api-table table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.api-table th,
.api-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.api-table th {
  font-weight: 600;
  color: #475569;
  background: #f8fafc;
  font-size: 13px;
}

.api-table td {
  color: #1e293b;
  font-size: 13px;
}

.api-table td:first-child {
  color: #3b82f6;
  font-weight: 500;
}

.api-table td:nth-child(3) {
  color: #8b5cf6;
}
</style>
