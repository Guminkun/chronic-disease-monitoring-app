<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">健康宣教</h2>
        <p class="text-text-muted mt-1">管理小程序端健康宣教文章内容</p>
      </div>
      <el-button type="primary" class="btn-primary" :icon="Plus" @click="handleCreate">新建文章</el-button>
    </div>

    <!-- Filters -->
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center">
      <div class="w-64">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文章标题或作者..."
          :prefix-icon="Search"
          class="custom-input"
          size="large"
          clearable
          @clear="fetchData"
          @keyup.enter="fetchData"
        />
      </div>
      <el-select v-model="filterCategory" placeholder="全部分类" class="w-36 custom-select" size="large" clearable @change="fetchData">
        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
      </el-select>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table 
        :data="articles" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        v-loading="loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
      >
        <el-table-column label="文章信息" min-width="250">
          <template #default="scope">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-xl bg-secondary-100 flex-shrink-0 flex items-center justify-center overflow-hidden">
                 <img v-if="scope.row.cover_image" :src="scope.row.cover_image" class="w-full h-full object-cover" />
                 <el-icon v-else class="text-text-muted text-xl"><Reading /></el-icon>
              </div>
              <div>
                <p class="font-medium text-text-primary line-clamp-1">{{ scope.row.title }}</p>
                <p class="text-xs text-text-muted">创建于 {{ formatDate(scope.row.created_at) }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="分类" width="120">
          <template #default="scope">
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
              {{ scope.row.category?.name || '未分类' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="author" label="作者" width="120">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.author || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="阅读量" width="100">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.views || 0 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                scope.row.is_published 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-amber-100 text-amber-700'
              ]"
            >
              {{ scope.row.is_published ? '已发布' : '草稿' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column label="更新时间" width="140">
          <template #default="scope">
            <span class="text-text-secondary text-sm">{{ formatDate(scope.row.updated_at) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="80" align="center">
          <template #default="scope">
            <el-dropdown trigger="click">
              <el-button circle class="action-btn">
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEdit(scope.row)">编辑</el-dropdown-item>
                  <el-dropdown-item @click="togglePublish(scope.row)">
                    {{ scope.row.is_published ? '下架' : '发布' }}
                  </el-dropdown-item>
                  <el-dropdown-item divided class="text-red-500">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="p-5 bg-white border-t border-secondary-100">
        <Pagination
          v-model:currentPage="page"
          v-model:pageSize="pageSize"
          :total="total"
          @change="fetchData"
        />
      </div>
    </div>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '新建文章' : '编辑文章'"
      width="800px"
      top="5vh"
      class="custom-dialog"
    >
      <el-form :model="form" label-width="80px" class="custom-form">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入文章标题" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category_id" placeholder="请选择分类" class="w-full">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者">
              <el-input v-model="form.author" placeholder="请输入作者" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="封面图">
          <el-input v-model="form.cover_image" placeholder="请输入图片URL" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="文章摘要" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入文章内容 (支持HTML)" />
        </el-form-item>
        <el-form-item label="设置">
          <div class="flex gap-6">
            <el-checkbox v-model="form.is_published">立即发布</el-checkbox>
            <el-checkbox v-model="form.is_recommended">设为推荐</el-checkbox>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" class="btn-primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Search, Plus, More, Reading } from '@element-plus/icons-vue'
import { getArticles, getCategories, createArticle, updateArticle } from '../../api/education_manage'
import { ElMessage } from 'element-plus'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const filterCategory = ref('')
const loading = ref(false)
const articles = ref([])
const categories = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const form = reactive({
  id: undefined as number | undefined,
  title: '',
  category_id: undefined as number | undefined,
  author: '',
  cover_image: '',
  summary: '',
  content: '',
  is_published: true,
  is_recommended: false
})

const fetchCategories = async () => {
  try {
    const res: any = await getCategories()
    categories.value = res
  } catch (e) {
    console.error(e)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await getArticles({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      q: searchQuery.value,
      category_id: filterCategory.value || undefined
    })
    articles.value = res.items || res
    total.value = res.total || articles.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatDate = (iso: string) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString()
}

const handleCreate = () => {
  dialogType.value = 'create'
  Object.assign(form, {
    id: undefined,
    title: '',
    category_id: undefined,
    author: '',
    cover_image: '',
    summary: '',
    content: '',
    is_published: true,
    is_recommended: false
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  Object.assign(form, row)
  form.category_id = row.category?.id
  dialogVisible.value = true
}

const togglePublish = async (row: any) => {
  try {
    await updateArticle(row.id, { is_published: !row.is_published })
    ElMessage.success(row.is_published ? '已下架' : '已发布')
    fetchData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const submitForm = async () => {
  try {
    if (dialogType.value === 'create') {
      await createArticle(form)
      ElMessage.success('创建成功')
    } else {
      await updateArticle(form.id!, form)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchCategories()
  fetchData()
})
</script>

<style scoped>
.btn-primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border: none;
  border-radius: 10px;
  font-weight: 500;
}
.btn-primary:hover {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
}

:deep(.custom-input .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #E2E8F0;
  padding: 4px 12px;
}
:deep(.custom-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6;
}
:deep(.custom-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

:deep(.custom-select .el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #E2E8F0;
}

.action-btn {
  background-color: #F1F5F9;
  border: none;
  color: #64748B;
}
.action-btn:hover {
  background-color: #E2E8F0;
  color: #3B82F6;
}

:deep(.custom-dialog .el-dialog__header) {
  border-bottom: 1px solid #E2E8F0;
  padding-bottom: 16px;
}

:deep(.custom-form .el-form-item__label) {
  color: #475569;
  font-weight: 500;
}
</style>
