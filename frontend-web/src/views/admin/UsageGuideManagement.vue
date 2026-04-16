<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-text-primary">使用说明</h2>
        <p class="text-text-muted mt-1">管理小程序功能使用说明内容，支持图片和视频</p>
      </div>
      <el-button type="primary" class="btn-primary" :icon="Plus" @click="handleCreate">新建说明</el-button>
    </div>
    <div class="bg-white p-5 rounded-2xl border border-secondary-100 shadow-sm flex flex-wrap gap-4 items-center">
      <div class="w-64">
        <el-input v-model="searchQuery" placeholder="搜索标题或描述..." :prefix-icon="Search" class="custom-input" size="large" clearable @clear="fetchData" @keyup.enter="fetchData" />
      </div>
      <el-select v-model="filterStatus" placeholder="全部状态" class="w-36 custom-select" size="large" clearable @change="fetchData">
        <el-option label="已发布" :value="true" />
        <el-option label="草稿" :value="false" />
      </el-select>
    </div>
    <div class="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <el-table :data="guides" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#475569', fontWeight: '600' }" v-loading="loading">
        <el-table-column label="说明信息" min-width="320">
          <template #default="scope">
            <div class="flex items-center gap-3">
              <div class="w-14 h-14 rounded-xl bg-secondary-100 flex-shrink-0 flex items-center justify-center overflow-hidden">
                <img v-if="scope.row.cover_image" :src="scope.row.cover_image" class="w-full h-full object-cover" />
                <el-icon v-else class="text-text-muted text-2xl"><Document /></el-icon>
              </div>
              <div>
                <p class="font-medium text-text-primary line-clamp-1">{{ scope.row.title }}</p>
                <p class="text-xs text-text-muted line-clamp-1">{{ scope.row.description || '暂无描述' }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="媒体" width="100" align="center">
          <template #default="scope">
            <div class="flex items-center justify-center gap-2">
              <span v-if="scope.row.images?.length" class="flex items-center gap-1 text-blue-500"><el-icon><Picture /></el-icon>{{ scope.row.images.length }}</span>
              <span v-if="scope.row.videos?.length" class="flex items-center gap-1 text-green-500"><el-icon><VideoCamera /></el-icon>{{ scope.row.videos.length }}</span>
              <span v-if="!scope.row.images?.length && !scope.row.videos?.length" class="text-text-muted">-</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览量" width="80" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <span :class="['px-3 py-1 rounded-full text-xs font-medium', scope.row.is_published ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700']">{{ scope.row.is_published ? '已发布' : '草稿' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="140">
          <template #default="scope"><span class="text-text-secondary text-sm">{{ formatDate(scope.row.updated_at) }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="scope">
            <el-dropdown trigger="click">
              <el-button circle class="action-btn"><el-icon><More /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleEdit(scope.row)">编辑</el-dropdown-item>
                  <el-dropdown-item @click="togglePublishStatus(scope.row)">{{ scope.row.is_published ? '下架' : '发布' }}</el-dropdown-item>
                  <el-dropdown-item divided class="text-red-500" @click="handleDelete(scope.row)">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <div class="p-5 bg-white border-t border-secondary-100">
        <Pagination
          v-model:currentPage="page"
          v-model:pageSize="pageSize"
          :total="total"
          @change="fetchData"
        />
      </div>
    </div>
    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建使用说明' : '编辑使用说明'" width="900px" top="3vh" :close-on-click-modal="false">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="标题" required><el-input v-model="form.title" placeholder="请输入标题" maxlength="200" show-word-limit /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="排序权重"><el-input-number v-model="form.sort_order" :min="0" :max="9999" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" /></el-form-item>
        <el-form-item label="封面图片">
          <div class="flex items-start gap-4">
            <div class="w-32 h-24 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center overflow-hidden bg-gray-50">
              <img v-if="form.cover_image" :src="form.cover_image" class="w-full h-full object-cover" />
              <el-icon v-else class="text-gray-400 text-2xl"><Plus /></el-icon>
            </div>
            <div class="flex flex-col gap-2">
              <el-upload :show-file-list="false" :before-upload="beforeCoverUpload" :http-request="handleCoverUpload" accept="image/*"><el-button size="small" type="primary">上传封面</el-button></el-upload>
              <el-input v-model="form.cover_image" placeholder="或输入图片URL" class="w-60" size="small" />
            </div>
          </div>
        </el-form-item>
        <el-form-item label="详细内容"><el-input v-model="form.content" type="textarea" :rows="6" placeholder="请输入详细内容" /></el-form-item>
        <el-form-item label="图片上传">
          <el-upload v-model:file-list="imageFileList" list-type="picture-card" :before-upload="beforeImageUpload" :http-request="handleImageUpload" accept="image/*" multiple><el-icon><Plus /></el-icon></el-upload>
        </el-form-item>
        <el-form-item label="视频上传">
          <el-upload v-model:file-list="videoFileList" list-type="picture-card" :before-upload="beforeVideoUpload" :http-request="handleVideoUpload" accept="video/*" multiple><el-icon><VideoCamera /></el-icon></el-upload>
        </el-form-item>
        <el-form-item label="发布设置"><el-checkbox v-model="form.is_published">立即发布</el-checkbox></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Search, Plus, More, Document, Picture, VideoCamera } from '@element-plus/icons-vue'
import { getUsageGuides, createUsageGuide, updateUsageGuide, deleteUsageGuide as deleteUsageGuideApi, togglePublish as togglePublishApi, uploadImage as uploadImageApi, uploadVideo as uploadVideoApi } from '../../api/usageGuides'
import { ElMessage, ElMessageBox } from 'element-plus'
import Pagination from '../../components/Pagination.vue'

const searchQuery = ref('')
const filterStatus = ref<boolean | ''>('')
const loading = ref(false)
const guides = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const dialogType = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const form = reactive({ id: undefined as number | undefined, title: '', description: '', content: '', cover_image: '', images: [] as string[], videos: [] as string[], sort_order: 0, is_published: true })
const imageFileList = ref<any[]>([])
const videoFileList = ref<any[]>([])

const fetchData = async () => {
  loading.value = true
  try { const res: any = await getUsageGuides({ skip: (page.value - 1) * pageSize.value, limit: pageSize.value, q: searchQuery.value || undefined, is_published: filterStatus.value === '' ? undefined : filterStatus.value }); guides.value = res.items || []; total.value = res.total || 0 } catch (e) { console.error(e) } finally { loading.value = false }
}
const formatDate = (iso: string) => iso ? new Date(iso).toLocaleDateString() : '-'

const handleCreate = () => {
  dialogType.value = 'create'
  Object.assign(form, { id: undefined, title: '', description: '', content: '', cover_image: '', images: [], videos: [], sort_order: 0, is_published: true })
  imageFileList.value = []; videoFileList.value = []; dialogVisible.value = true
}
const handleEdit = (row: any) => {
  dialogType.value = 'edit'; Object.assign(form, row)
  imageFileList.value = (row.images || []).map((url: string, i: number) => ({ name: `image-${i}`, url }))
  videoFileList.value = (row.videos || []).map((url: string, i: number) => ({ name: `video-${i}`, url }))
  dialogVisible.value = true
}
const togglePublishStatus = async (row: any) => { try { await togglePublishApi(row.id); ElMessage.success(row.is_published ? '已下架' : '已发布'); fetchData() } catch (e) { ElMessage.error('操作失败') } }
const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该使用说明吗？', '提示', { type: 'warning' }).then(async () => {
    try { await deleteUsageGuideApi(row.id); ElMessage.success('删除成功'); fetchData() } catch (e) { ElMessage.error('删除失败') }
  }).catch(() => {})
}

const beforeCoverUpload = (file: File) => { const isImage = file.type.startsWith('image/'); const isLt10M = file.size / 1024 / 1024 < 10; if (!isImage) ElMessage.error('只能上传图片文件'); if (!isLt10M) ElMessage.error('图片大小不能超过 10MB'); return isImage && isLt10M }
const handleCoverUpload = async (options: any) => { try { const res: any = await uploadImageApi(options.file); form.cover_image = res.url; ElMessage.success('上传成功') } catch (e) { ElMessage.error('上传失败') } }
const beforeImageUpload = (file: File) => { const isImage = file.type.startsWith('image/'); const isLt10M = file.size / 1024 / 1024 < 10; if (!isImage) ElMessage.error('只能上传图片文件'); if (!isLt10M) ElMessage.error('图片大小不能超过 10MB'); return isImage && isLt10M }
const handleImageUpload = async (options: any) => { try { const res: any = await uploadImageApi(options.file); form.images = [...(form.images || []), res.url]; ElMessage.success('上传成功') } catch (e) { ElMessage.error('上传失败') } }
const beforeVideoUpload = (file: File) => { const isVideo = file.type.startsWith('video/'); const isLt100M = file.size / 1024 / 1024 < 100; if (!isVideo) ElMessage.error('只能上传视频文件'); if (!isLt100M) ElMessage.error('视频大小不能超过 100MB'); return isVideo && isLt100M }
const handleVideoUpload = async (options: any) => { try { const res: any = await uploadVideoApi(options.file); form.videos = [...(form.videos || []), res.url]; ElMessage.success('上传成功') } catch (e) { ElMessage.error('上传失败') } }

const submitForm = async () => {
  if (!form.title) { ElMessage.warning('请输入标题'); return }
  submitting.value = true
  try {
    const data = { ...form, images: form.images.filter(Boolean), videos: form.videos.filter(Boolean) }
    if (dialogType.value === 'create') { await createUsageGuide(data); ElMessage.success('创建成功') }
    else { await updateUsageGuide(form.id!, data); ElMessage.success('更新成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { ElMessage.error('操作失败') } finally { submitting.value = false }
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.btn-primary { background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); border: none; border-radius: 10px; font-weight: 500; }
.btn-primary:hover { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); }
:deep(.custom-input .el-input__wrapper) { border-radius: 10px; box-shadow: 0 0 0 1px #E2E8F0; padding: 4px 12px; }
:deep(.custom-select .el-input__wrapper) { border-radius: 10px; box-shadow: 0 0 0 1px #E2E8F0; }
.action-btn { background-color: #F1F5F9; border: none; color: #64748B; }
.action-btn:hover { background-color: #E2E8F0; color: #3B82F6; }
</style>
