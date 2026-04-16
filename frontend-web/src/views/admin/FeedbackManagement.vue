<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">意见反馈</h2>
        <p class="text-text-muted mt-1">管理用户提交的意见反馈</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-sm text-text-muted">共 {{ total }} 条反馈</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center">
      <div class="w-64">
        <el-input
          v-model="keyword"
          placeholder="搜索反馈内容..."
          :prefix-icon="Search"
          class="custom-input"
          size="large"
          clearable
          @clear="fetchData"
          @keyup.enter="fetchData"
        />
      </div>
      <el-select v-model="filterStatus" placeholder="状态筛选" class="w-36 custom-select" size="large" clearable @change="fetchData">
        <el-option label="待处理" value="pending" />
        <el-option label="处理中" value="processing" />
        <el-option label="已回复" value="replied" />
        <el-option label="已关闭" value="closed" />
      </el-select>
      <div class="flex-grow"></div>
      <el-button type="primary" :icon="Search" @click="fetchData">搜索</el-button>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table 
        :data="feedbackList" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        v-loading="loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
      >
        <el-table-column label="用户信息" min-width="150">
          <template #default="scope">
            <div>
              <p class="font-medium text-text-primary">{{ scope.row.user_name || '未知用户' }}</p>
              <p class="text-xs text-text-muted">{{ scope.row.user_phone || '-' }}</p>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="反馈内容" min-width="300">
          <template #default="scope">
            <div class="line-clamp-2">{{ scope.row.content }}</div>
            <div class="flex gap-1 mt-1" v-if="scope.row.images?.length">
              <el-image 
                v-for="(img, idx) in scope.row.images.slice(0, 3)" 
                :key="idx"
                :src="img" 
                :preview-src-list="scope.row.images"
                :initial-index="idx"
                fit="cover"
                class="w-10 h-10 rounded"
              />
              <span v-if="scope.row.images.length > 3" class="text-xs text-text-muted">+{{ scope.row.images.length - 3 }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="联系方式" width="140">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ scope.row.contact || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                getStatusClass(scope.row.status)
              ]"
            >
              {{ getStatusText(scope.row.status) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="提交时间" width="160">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ formatDateTime(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <div class="flex gap-2">
              <el-button type="primary" link size="small" @click="handleView(scope.row)">查看</el-button>
              <el-button 
                v-if="scope.row.status !== 'replied'" 
                type="success" 
                link 
                size="small" 
                @click="handleReply(scope.row)"
              >
                回复
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="p-4 border-t border-secondary-100">
        <Pagination
          v-model:currentPage="page"
          v-model:pageSize="pageSize"
          :total="total"
          @change="fetchData"
        />
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="反馈详情" width="600px" destroy-on-close>
      <div v-if="currentFeedback" class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium text-text-primary">{{ currentFeedback.user_name || '未知用户' }}</p>
            <p class="text-sm text-text-muted">{{ currentFeedback.user_phone || '-' }}</p>
          </div>
          <span 
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium',
              getStatusClass(currentFeedback.status)
            ]"
          >
            {{ getStatusText(currentFeedback.status) }}
          </span>
        </div>
        
        <div class="bg-secondary-50 p-4 rounded-lg">
          <p class="text-text-primary whitespace-pre-wrap">{{ currentFeedback.content }}</p>
        </div>
        
        <div v-if="currentFeedback.images?.length" class="flex flex-wrap gap-2">
          <el-image 
            v-for="(img, idx) in currentFeedback.images" 
            :key="idx"
            :src="img" 
            :preview-src-list="currentFeedback.images"
            :initial-index="idx"
            fit="cover"
            class="w-20 h-20 rounded-lg"
          />
        </div>
        
        <div v-if="currentFeedback.contact" class="text-sm">
          <span class="text-text-muted">联系方式：</span>
          <span class="text-text-primary">{{ currentFeedback.contact }}</span>
        </div>
        
        <div class="text-sm text-text-muted">
          提交时间：{{ formatDateTime(currentFeedback.created_at) }}
        </div>
        
        <!-- 回复内容 -->
        <div v-if="currentFeedback.reply_content" class="bg-green-50 p-4 rounded-lg border border-green-200">
          <div class="flex items-center gap-2 mb-2">
            <el-icon class="text-green-600"><ChatDotRound /></el-icon>
            <span class="font-medium text-green-700">管理员回复</span>
          </div>
          <p class="text-text-primary whitespace-pre-wrap">{{ currentFeedback.reply_content }}</p>
          <div class="text-xs text-text-muted mt-2">
            {{ currentFeedback.replier_name || '管理员' }} · {{ formatDateTime(currentFeedback.replied_at) }}
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-between">
          <div>
            <el-button 
              v-if="currentFeedback?.status === 'pending'" 
              type="warning" 
              @click="handleUpdateStatus(currentFeedback, 'processing')"
            >
              标记处理中
            </el-button>
            <el-button 
              v-if="currentFeedback?.status !== 'closed'" 
              @click="handleUpdateStatus(currentFeedback, 'closed')"
            >
              关闭反馈
            </el-button>
          </div>
          <div>
            <el-button @click="detailVisible = false">关闭</el-button>
            <el-button 
              v-if="currentFeedback?.status !== 'replied'" 
              type="primary" 
              @click="handleReply(currentFeedback); detailVisible = false"
            >
              回复
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 回复对话框 -->
    <el-dialog v-model="replyVisible" title="回复反馈" width="500px" destroy-on-close>
      <div v-if="currentFeedback" class="space-y-4">
        <div class="bg-secondary-50 p-3 rounded-lg text-sm text-text-secondary max-h-32 overflow-y-auto">
          {{ currentFeedback.content }}
        </div>
        
        <el-form :model="replyForm" label-position="top">
          <el-form-item label="回复内容" required>
            <el-input
              v-model="replyForm.reply_content"
              type="textarea"
              :rows="5"
              placeholder="请输入回复内容..."
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="replyVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ChatDotRound } from '@element-plus/icons-vue'
import { 
  getFeedbacks, 
  replyFeedback, 
  updateFeedbackStatus, 
  deleteFeedback 
} from '../../api/feedback'
import type { Feedback, FeedbackStatus } from '../../api/feedback'
import Pagination from '../../components/Pagination.vue'

const loading = ref(false)
const feedbackList = ref<Feedback[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const filterStatus = ref('')

const detailVisible = ref(false)
const replyVisible = ref(false)
const currentFeedback = ref<Feedback | null>(null)
const replyForm = ref({ reply_content: '' })
const submitting = ref(false)

// 获取状态文本
const getStatusText = (status: FeedbackStatus) => {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    replied: '已回复',
    closed: '已关闭'
  }
  return map[status] || status
}

// 获取状态样式类
const getStatusClass = (status: FeedbackStatus) => {
  const map: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    processing: 'bg-blue-100 text-blue-700',
    replied: 'bg-green-100 text-green-700',
    closed: 'bg-gray-100 text-gray-700'
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

// 格式化日期时间
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getFeedbacks({
      page: page.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined,
      keyword: keyword.value || undefined
    }) as any
    feedbackList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载反馈列表失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleView = (feedback: Feedback) => {
  currentFeedback.value = feedback
  detailVisible.value = true
}

// 打开回复对话框
const handleReply = (feedback: Feedback) => {
  currentFeedback.value = feedback
  replyForm.value.reply_content = ''
  replyVisible.value = true
}

// 提交回复
const submitReply = async () => {
  if (!currentFeedback.value) return
  if (!replyForm.value.reply_content.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  submitting.value = true
  try {
    await replyFeedback(currentFeedback.value.id, replyForm.value.reply_content)
    ElMessage.success('回复成功')
    replyVisible.value = false
    fetchData()
  } catch (error) {
    console.error('回复失败:', error)
    ElMessage.error('回复失败')
  } finally {
    submitting.value = false
  }
}

// 更新状态
const handleUpdateStatus = async (feedback: Feedback, status: string) => {
  try {
    await updateFeedbackStatus(feedback.id, status)
    ElMessage.success('状态更新成功')
    detailVisible.value = false
    fetchData()
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('更新状态失败')
  }
}

// 删除反馈
const handleDelete = (feedback: Feedback) => {
  ElMessageBox.confirm(
    '确定要删除这条反馈吗？此操作不可恢复。',
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteFeedback(feedback.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
