<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">慢性病字典</h2>
        <p class="text-text-muted mt-1">管理系统慢性病基础数据</p>
      </div>
      <div class="flex gap-3">
        <el-button type="success" class="btn-success" :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button type="primary" class="btn-primary" :icon="Plus" @click="handleCreate">添加疾病</el-button>
      </div>
    </div>

    <!-- Filters & Actions -->
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center justify-between">
      <div class="flex gap-4 items-center">
        <div class="w-80">
          <el-input
            v-model="searchQuery"
            placeholder="搜索诊断名称、疾病名称、编码..."
            :prefix-icon="Search"
            class="custom-input"
            size="large"
            clearable
            @clear="fetchData"
            @keyup.enter="fetchData"
          />
        </div>
      </div>
      
      <!-- Batch Actions -->
      <div v-if="selectedIds.length > 0" class="flex gap-2 items-center animate-fade-in">
        <span class="text-sm text-text-muted mr-2">已选 {{ selectedIds.length }} 项</span>
        <el-button type="success" plain size="default" @click="handleBatchStatus(true)">批量启用</el-button>
        <el-button type="warning" plain size="default" @click="handleBatchStatus(false)">批量禁用</el-button>
        <el-button type="danger" size="default" @click="handleBatchDelete">批量删除</el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table 
        :data="diseases" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        v-loading="loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="一级分类(章)" width="150" show-overflow-tooltip>
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.chapter_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="二级分类(节)" width="150" show-overflow-tooltip>
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.section_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="类目名称" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <div class="flex items-center gap-2">
              <div class="p-1.5 rounded-lg bg-purple-100 text-purple-600 shrink-0">
                <el-icon><Document /></el-icon>
              </div>
              <span class="font-medium text-text-primary">{{ scope.row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="code" label="类目代码" width="100">
          <template #default="scope">
            <span class="font-mono text-text-muted bg-secondary-50 px-2 py-1 rounded">{{ scope.row.code || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="亚目名称" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.subcategory_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="诊断名称" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <div class="flex flex-col">
              <span class="text-primary-600 font-medium">{{ scope.row.diagnosis_name || '-' }}</span>
              <span class="text-xs text-text-muted font-mono" v-if="scope.row.diagnosis_code">{{ scope.row.diagnosis_code }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="120" show-overflow-tooltip>
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.description || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                scope.row.is_active 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600'
              ]"
            >
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </span>
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
                  <el-dropdown-item :icon="Edit" @click="handleEdit(scope.row)">编辑</el-dropdown-item>
                  <el-dropdown-item :icon="Delete" divided class="text-red-500" @click="handleSingleDelete(scope.row)">删除</el-dropdown-item>
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

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'create' ? '添加疾病' : '编辑疾病'"
      width="600px"
      class="custom-dialog"
    >
      <el-form :model="form" label-width="100px" class="custom-form grid grid-cols-2 gap-x-4">
        <el-form-item label="一级分类" class="col-span-2">
          <el-input v-model="form.chapter_name" placeholder="对应'章的名称'" />
        </el-form-item>
        <el-form-item label="二级分类" class="col-span-2">
          <el-input v-model="form.section_name" placeholder="对应'节名称'" />
        </el-form-item>
        <el-form-item label="类目名称">
          <el-input v-model="form.name" placeholder="对应原疾病名称" />
        </el-form-item>
        <el-form-item label="类目代码">
          <el-input v-model="form.code" placeholder="对应原ICD编码" />
        </el-form-item>
        <el-form-item label="亚目名称">
          <el-input v-model="form.subcategory_name" />
        </el-form-item>
        <el-form-item label="亚目代码">
          <el-input v-model="form.subcategory_code" />
        </el-form-item>
        <el-form-item label="诊断名称">
          <el-input v-model="form.diagnosis_name" />
        </el-form-item>
        <el-form-item label="诊断代码">
          <el-input v-model="form.diagnosis_code" />
        </el-form-item>
        <el-form-item label="章代码范围">
          <el-input v-model="form.chapter_code_range" />
        </el-form-item>
        <el-form-item label="节代码范围">
          <el-input v-model="form.section_code_range" />
        </el-form-item>
        <el-form-item label="状态" class="col-span-2">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="描述" class="col-span-2">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" class="btn-primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入疾病"
      width="500px"
      class="custom-dialog"
    >
      <div class="space-y-6">
        <div class="flex items-center justify-between p-4 bg-secondary-50 rounded-xl border border-secondary-100">
          <div>
            <h4 class="font-medium text-text-primary mb-1">第一步：下载模板</h4>
            <p class="text-xs text-text-muted">请按照模板格式填写疾病信息</p>
          </div>
          <el-button type="primary" link :icon="Download" @click="downloadTemplateFile">下载模板</el-button>
        </div>

        <div>
          <h4 class="font-medium text-text-primary mb-3">第二步：上传文件</h4>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            :show-file-list="true"
            v-model:file-list="fileList"
            accept=".xlsx, .xls"
          >
            <el-icon class="el-icon--upload text-4xl text-primary-500"><upload-filled /></el-icon>
            <div class="el-upload__text text-text-secondary">
              拖拽文件到此处或 <em class="text-primary-600">点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip text-text-muted">
                只能上传 xlsx/xls 文件
              </div>
            </template>
          </el-upload>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" class="btn-primary" @click="submitImport" :loading="uploading">开始导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Search, Plus, More, Upload, Download, UploadFilled, Edit, Delete, Document } from '@element-plus/icons-vue'
import { 
  getDiseases, 
  createDisease, 
  updateDisease, 
  deleteDisease,
  downloadTemplate, 
  importDiseases,
  batchDeleteDiseases,
  batchUpdateStatus 
} from '../../api/disease_manage'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const loading = ref(false)
const diseases = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const selectedIds = ref<number[]>([])

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const form = reactive({
  id: undefined as number | undefined,
  name: '',
  code: '',
  chapter: '',
  chapter_code_range: '',
  chapter_name: '',
  section_code_range: '',
  section_name: '',
  subcategory_code: '',
  subcategory_name: '',
  diagnosis_code: '',
  diagnosis_name: '',
  is_active: true,
  description: ''
})

// Import related
const importDialogVisible = ref(false)
const uploading = ref(false)
const fileList = ref<UploadFile[]>([])

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await getDiseases({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      q: searchQuery.value
    })
    diseases.value = res.items || res
    total.value = res.total || diseases.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return
  
  ElMessageBox.confirm(
    `确定要批量删除选中的 ${selectedIds.value.length} 条数据吗？此操作不可撤销。`,
    '批量删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await batchDeleteDiseases(selectedIds.value)
      ElMessage.success('批量删除成功')
      fetchData()
    } catch (e) {
      ElMessage.error('批量删除失败')
    }
  })
}

const handleBatchStatus = async (is_active: boolean) => {
  if (selectedIds.value.length === 0) return
  
  try {
    await batchUpdateStatus(selectedIds.value, is_active)
    ElMessage.success(`成功批量${is_active ? '启用' : '禁用'} ${selectedIds.value.length} 条数据`)
    fetchData()
  } catch (e) {
    ElMessage.error('批量更新状态失败')
  }
}

const handleSingleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除疾病 "${row.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteDisease(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  })
}

const resetForm = () => {
  Object.assign(form, {
    id: undefined,
    name: '',
    code: '',
    chapter: '',
    chapter_code_range: '',
    chapter_name: '',
    section_code_range: '',
    section_name: '',
    subcategory_code: '',
    subcategory_name: '',
    diagnosis_code: '',
    diagnosis_name: '',
    is_active: true,
    description: ''
  })
}

const handleCreate = () => {
  dialogType.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  resetForm()
  Object.assign(form, row)
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    if (dialogType.value === 'create') {
      await createDisease(form)
      ElMessage.success('创建成功')
    } else {
      await updateDisease(form.id!, form)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// Import logic
const handleImport = () => {
  importDialogVisible.value = true
  fileList.value = []
}

const downloadTemplateFile = async () => {
  try {
    const res: any = await downloadTemplate()
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '疾病导入模板.xlsx'
    link.click()
    URL.revokeObjectURL(link.href)
  } catch (e) {
    ElMessage.error('下载模板失败')
  }
}

const handleFileChange = (file: UploadFile) => {
  fileList.value = [file]
}

const submitImport = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  try {
    const firstFile = fileList.value[0]
    const rawFile = firstFile?.raw
    if (!rawFile) return
    
    const res: any = await importDiseases(rawFile)
    ElMessage.success(res.message)
    if (res.errors && res.errors.length > 0) {
      ElMessage.warning(`部分导入失败: ${res.errors.length} 条`)
      console.warn(res.errors)
    }
    importDialogVisible.value = false
    fetchData()
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e.response?.data?.detail || '导入失败')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
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

.btn-success {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border: none;
  border-radius: 10px;
  font-weight: 500;
}
.btn-success:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
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

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
</style>
