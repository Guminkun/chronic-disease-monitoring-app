<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">药品库管理</h2>
        <p class="text-text-muted mt-1">管理系统药品信息库</p>
      </div>
      <div class="flex gap-3">
        <el-button type="success" class="btn-success" :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button type="primary" class="btn-primary" :icon="Plus" @click="handleCreate">添加药品</el-button>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center justify-between">
      <div class="flex gap-4 items-center flex-wrap">
        <div class="w-52">
          <el-input
            v-model="searchQuery"
            placeholder="通用名称/商品名称"
            :prefix-icon="Search"
            class="custom-input"
            size="large"
            clearable
            @clear="fetchData"
            @keyup.enter="fetchData"
          />
        </div>
        <div class="w-52">
          <el-input
            v-model="searchManufacturer"
            placeholder="生产企业"
            :prefix-icon="Search"
            class="custom-input"
            size="large"
            clearable
            @clear="fetchData"
            @keyup.enter="fetchData"
          />
        </div>
        <el-select v-model="filterCategory" placeholder="治疗系统分类" class="w-48 custom-select" size="large" clearable @change="fetchData">
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </div>

      <!-- Batch Actions -->
      <div v-if="selectedIds.length > 0" class="flex gap-2 items-center animate-fade-in">
        <span class="text-sm text-text-muted mr-2">已选 {{ selectedIds.length }} 项</span>
        <el-button type="success" plain size="default" @click="handleBatchStatus(true)">批量启用</el-button>
        <el-button type="warning" plain size="default" @click="handleBatchStatus(false)">批量停用</el-button>
        <el-button type="danger" size="default" @click="handleBatchDelete">批量删除</el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table 
        :data="medications" 
        style="width: 100%" 
        :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600', borderColor: '#E2E8F0' }"
        :cell-style="{ background: '#fff', color: '#1E293B', borderColor: '#F1F5F9' }"
        v-loading="loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column label="序号" type="index" width="65" align="center"
          :index="(i) => (page - 1) * pageSize + i + 1"
        />
        
        <el-table-column label="通用名称" min-width="160">
          <template #default="scope">
            <div class="flex items-center gap-2">
              <div class="p-2 rounded-xl bg-green-100 text-green-600 shrink-0">
                <el-icon class="text-lg"><FirstAidKit /></el-icon>
              </div>
              <span class="font-medium text-text-primary">{{ scope.row.generic_name || scope.row.title || '-' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="商品名称" min-width="130">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.trade_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="manufacturer" label="生产企业" min-width="180">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.manufacturer || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="specification" label="规格" width="120">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.specification || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="therapeutic_system_subcategory" label="治疗系统分类" width="150">
          <template #default="scope">
            <span class="text-text-secondary">{{ scope.row.therapeutic_system_subcategory || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span 
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                scope.row.status === 'active' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-gray-100 text-gray-600'
              ]"
            >
              {{ scope.row.status === 'active' ? '启用' : '停用' }}
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
                  <el-dropdown-item :icon="Document" @click="handleDetail(scope.row)">详情</el-dropdown-item>
                  <el-dropdown-item :icon="Edit" @click="handleEdit(scope.row)">编辑</el-dropdown-item>
                  <el-dropdown-item :icon="Delete" divided class="text-red-500" @click="handleDelete(scope.row)">删除</el-dropdown-item>
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
      :title="dialogType === 'create' ? '添加药品' : '编辑药品'"
      width="800px"
      class="custom-dialog"
    >
      <el-form :model="form" label-width="140px" class="custom-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="标题">
              <el-input v-model="form.title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标题链接">
              <el-input v-model="form.title_url" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="编号">
              <el-input v-model="form.number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="r3">
              <el-input v-model="form.r3" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="通用名称">
              <el-input v-model="form.generic_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称">
              <el-input v-model="form.trade_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="汉语拼音">
              <el-input v-model="form.pinyin" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="批准文号">
              <el-input v-model="form.approval_number" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
           <el-col :span="12">
             <el-form-item label="药品分类">
               <el-input v-model="form.category" />
             </el-form-item>
           </el-col>
           <el-col :span="12">
             <el-form-item label="生产企业">
               <el-input v-model="form.manufacturer" />
             </el-form-item>
           </el-col>
         </el-row>
         <el-row :gutter="20">
           <el-col :span="12">
             <el-form-item label="治疗系统分类">
               <el-input v-model="form.therapeutic_system_category" placeholder="如：心血管系统" />
             </el-form-item>
           </el-col>
           <el-col :span="12">
             <el-form-item label="治疗系统二级分类">
               <el-input v-model="form.therapeutic_system_subcategory" placeholder="如：抗高血压药" />
             </el-form-item>
           </el-col>
         </el-row>
         <el-row :gutter="20">
           <el-col :span="12">
             <el-form-item label="药品性质">
               <el-input v-model="form.drug_nature" />
             </el-form-item>
           </el-col>
           <el-col :span="12">
             <el-form-item label="规格">
               <el-input v-model="form.specification" />
             </el-form-item>
           </el-col>
         </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效期">
              <el-input v-model="form.expiry_period" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="状态">
              <el-switch v-model="form.status" active-value="active" inactive-value="inactive" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">相关疾病 / 性状 / 成份</el-divider>
        <el-form-item label="相关疾病">
          <el-input v-model="form.related_diseases" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="性状">
          <el-input v-model="form.properties" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="主要成份">
          <el-input v-model="form.main_ingredients" type="textarea" :rows="2" />
        </el-form-item>

        <el-divider content-position="left">临床信息</el-divider>
        <el-form-item label="适应症">
          <el-input v-model="form.indications" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="不良反应">
          <el-input v-model="form.adverse_reactions" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="用法用量">
          <el-input v-model="form.usage_dosage" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="禁忌">
          <el-input v-model="form.contraindications" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="注意事项">
          <el-input v-model="form.precautions" type="textarea" :rows="2" />
        </el-form-item>

        <el-divider content-position="left">特殊人群 / 药理药代</el-divider>
        <el-form-item label="孕妇及哺乳期妇女用药">
          <el-input v-model="form.pregnancy_lactation" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="儿童用药">
          <el-input v-model="form.pediatric_use" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="老人用药">
          <el-input v-model="form.geriatric_use" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="药物相互作用">
          <el-input v-model="form.drug_interactions" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="药理毒理">
          <el-input v-model="form.pharmacology_toxicology" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="药代动力学">
          <el-input v-model="form.pharmacokinetics" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="贮藏">
          <el-input v-model="form.storage" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" class="btn-primary" @click="submitForm">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="药品详情"
      width="700px"
      class="custom-dialog"
    >
      <el-descriptions :column="2" border class="custom-descriptions">
        <el-descriptions-item label="标题" :span="2">{{ currentMedication.title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="标题链接" :span="2">{{ currentMedication.title_url || '-' }}</el-descriptions-item>
        <el-descriptions-item label="编号">{{ currentMedication.number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="r3">{{ currentMedication.r3 || '-' }}</el-descriptions-item>
        <el-descriptions-item label="通用名称">{{ currentMedication.generic_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="商品名称">{{ currentMedication.trade_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="汉语拼音">{{ currentMedication.pinyin || '-' }}</el-descriptions-item>
        <el-descriptions-item label="批准文号">{{ currentMedication.approval_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="药品分类">{{ currentMedication.category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="生产企业">{{ currentMedication.manufacturer || '-' }}</el-descriptions-item>
        <el-descriptions-item label="治疗系统分类">{{ currentMedication.therapeutic_system_category || '-' }}</el-descriptions-item>
        <el-descriptions-item label="治疗系统二级分类">{{ currentMedication.therapeutic_system_subcategory || '-' }}</el-descriptions-item>
        <el-descriptions-item label="药品性质">{{ currentMedication.drug_nature || '-' }}</el-descriptions-item>
        <el-descriptions-item label="规格">{{ currentMedication.specification || '-' }}</el-descriptions-item>
        <el-descriptions-item label="有效期">{{ currentMedication.expiry_period || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <span :class="['px-2 py-1 rounded-full text-xs font-medium', currentMedication.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600']">
            {{ currentMedication.status === 'active' ? '启用' : '停用' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="相关疾病" :span="2">{{ currentMedication.related_diseases || '-' }}</el-descriptions-item>
        <el-descriptions-item label="性状" :span="2">{{ currentMedication.properties || '-' }}</el-descriptions-item>
        <el-descriptions-item label="主要成份" :span="2">{{ currentMedication.main_ingredients || '-' }}</el-descriptions-item>
        <el-descriptions-item label="适应症" :span="2">{{ currentMedication.indications || '-' }}</el-descriptions-item>
        <el-descriptions-item label="不良反应" :span="2">{{ currentMedication.adverse_reactions || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用法用量" :span="2">{{ currentMedication.usage_dosage || '-' }}</el-descriptions-item>
        <el-descriptions-item label="禁忌" :span="2">{{ currentMedication.contraindications || '-' }}</el-descriptions-item>
        <el-descriptions-item label="注意事项" :span="2">{{ currentMedication.precautions || '-' }}</el-descriptions-item>
        <el-descriptions-item label="孕妇及哺乳期妇女用药" :span="2">{{ currentMedication.pregnancy_lactation || '-' }}</el-descriptions-item>
        <el-descriptions-item label="儿童用药">{{ currentMedication.pediatric_use || '-' }}</el-descriptions-item>
        <el-descriptions-item label="老人用药">{{ currentMedication.geriatric_use || '-' }}</el-descriptions-item>
        <el-descriptions-item label="药物相互作用" :span="2">{{ currentMedication.drug_interactions || '-' }}</el-descriptions-item>
        <el-descriptions-item label="药理毒理" :span="2">{{ currentMedication.pharmacology_toxicology || '-' }}</el-descriptions-item>
        <el-descriptions-item label="药代动力学" :span="2">{{ currentMedication.pharmacokinetics || '-' }}</el-descriptions-item>
        <el-descriptions-item label="贮藏" :span="2">{{ currentMedication.storage || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入药品"
      width="500px"
      class="custom-dialog"
    >
      <div class="space-y-6">
        <div class="flex items-center justify-between p-4 bg-secondary-50 rounded-xl border border-secondary-100">
          <div>
            <h4 class="font-medium text-text-primary mb-1">第一步：下载模板</h4>
            <p class="text-xs text-text-muted">请按照模板格式填写药品信息</p>
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
import { Search, Plus, More, FirstAidKit, Upload, Download, UploadFilled, Document, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import { getMedications, createMedication, updateMedication, deleteMedication, downloadTemplate, importMedications, batchDeleteMedications, batchUpdateStatus, getMedicationCategories } from '../../api/medication_dict'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const searchManufacturer = ref('')
const filterCategory = ref('')
const categories = ref<string[]>([])
const loading = ref(false)
const medications = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const selectedIds = ref<number[]>([])

const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const detailDialogVisible = ref(false)
const currentMedication = ref<any>({})

const form = reactive({
  id: undefined as number | undefined,
  title: '',
  title_url: '',
  number: '',
  r3: '',
  generic_name: '',
  trade_name: '',
  pinyin: '',
  approval_number: '',
  category: '',
  manufacturer: '',
  therapeutic_system_category: '',
  therapeutic_system_subcategory: '',
  drug_nature: '',
  related_diseases: '',
  properties: '',
  main_ingredients: '',
  indications: '',
  specification: '',
  adverse_reactions: '',
  usage_dosage: '',
  contraindications: '',
  precautions: '',
  pregnancy_lactation: '',
  pediatric_use: '',
  geriatric_use: '',
  drug_interactions: '',
  pharmacology_toxicology: '',
  pharmacokinetics: '',
  storage: '',
  expiry_period: '',
  status: 'active'
})

// Import related
const importDialogVisible = ref(false)
const uploading = ref(false)
const fileList = ref<UploadFile[]>([])

const fetchData = async () => {
  loading.value = true
  try {
    const res: any = await getMedications({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
      q: searchQuery.value || undefined,
      manufacturer: searchManufacturer.value || undefined,
      category: filterCategory.value || undefined
    })
    medications.value = res.items || res
    total.value = res.total || medications.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res: any = await getMedicationCategories()
    categories.value = res.items || []
  } catch (e) {
    console.error(e)
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
      await batchDeleteMedications(selectedIds.value)
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
    ElMessage.success(`成功批量${is_active ? '启用' : '停用'} ${selectedIds.value.length} 条数据`)
    fetchData()
  } catch (e) {
    ElMessage.error('批量更新状态失败')
  }
}

const handleCreate = () => {
  dialogType.value = 'create'
  Object.assign(form, {
    id: undefined,
    title: '',
    title_url: '',
    number: '',
    r3: '',
    generic_name: '',
    trade_name: '',
    pinyin: '',
    approval_number: '',
    category: '',
    manufacturer: '',
    therapeutic_system_category: '',
    therapeutic_system_subcategory: '',
    drug_nature: '',
    related_diseases: '',
    properties: '',
    main_ingredients: '',
    indications: '',
    specification: '',
    adverse_reactions: '',
    usage_dosage: '',
    contraindications: '',
    precautions: '',
    pregnancy_lactation: '',
    pediatric_use: '',
    geriatric_use: '',
    drug_interactions: '',
    pharmacology_toxicology: '',
    pharmacokinetics: '',
    storage: '',
    expiry_period: '',
    status: 'active'
  })
  dialogVisible.value = true
}

const handleDetail = (row: any) => {
  currentMedication.value = row
  detailDialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogType.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除该药品吗？', '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    await deleteMedication(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {
    // cancelled
  }
}

const submitForm = async () => {
  try {
    if (dialogType.value === 'create') {
      await createMedication(form)
      ElMessage.success('添加成功')
    } else {
      await updateMedication(form.id!, form)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {
    console.error(e)
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
    link.download = '药品导入模板.xlsx'
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
    
    const res: any = await importMedications(rawFile)
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
  fetchCategories()
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

:deep(.custom-descriptions .el-descriptions__label) {
  background-color: #F8FAFC;
  color: #475569;
  font-weight: 500;
}
:deep(.custom-descriptions .el-descriptions__content) {
  background-color: #fff;
  color: #1E293B;
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
