# MinIO 存储安全升级文档

## 升级概述

本次升级将MinIO存储从公开读取改为私有访问，实现生产级安全标准。

## 核心改动

### 1. 存储策略调整

**改动前:**
- 所有bucket公开读取
- 文件路径简单: `{timestamp}_{filename}`
- URL永久有效
- 无数据隔离
- 存储完整URL

**改动后:**
- 所有bucket私有访问
- 文件路径安全隔离: `user_{user_id}/member_{member_id}/{file_type}/{timestamp}_{uuid}.jpg`
- 临时签名URL（10分钟有效期）
- 严格用户/成员隔离
- 存储文件key（file key）

### 2. 新增功能

✅ **临时签名URL** - 所有图片访问必须通过后端生成临时URL
✅ **数据隔离** - 文件按用户/成员隔离，防止越权访问
✅ **MD5去重** - 相同文件只存一份，节省存储空间
✅ **图片压缩** - 自动压缩图片，减少体积和流量
✅ **缩略图生成** - 报告图片生成缩略图，提升列表加载速度
✅ **权限校验** - 获取图片前验证用户权限

### 3. 文件路径规范

```
检查报告: jianchabaogao/user_{uid}/member_{mid}/reports/20260416093745_a1b2c3d4.jpg
病历: binli/user_{uid}/member_{mid}/medical_records/20260416093745_a1b2c3d4.jpg
头像: avatars/user_{uid}/member_{mid}/avatar.jpg
使用指南: usageguides/user_{uid}/member_{mid}/guides/20260416093745_a1b2c3d4.jpg
缩略图: jianchabaogao/user_{uid}/member_{mid}/reports_thumbnails/20260416093745_a1b2c3d4_thumbnail.jpg
```

### 4. 数据库字段变更

**reports表新增字段:**
- `thumbnail_url` TEXT - 缩略图文件key
- `file_md5` VARCHAR(32) - 文件MD5哈希

**字段含义变更:**
- `image_url` - 从完整URL改为文件key

## 部署步骤

### 步骤1: 创建私有Bucket

在MinIO控制台或使用mc命令创建以下bucket（设置为私有）:

```bash
mc alias set myminio http://192.168.88.205:9000 admin Psbc@1234
mc mb myminio/binli
mc mb myminio/jianchabaogao
mc mb myminio/avatars
mc mb myminio/usageguides

# 确保bucket是私有的（默认就是私有）
mc anonymous set none myminio/binli
mc anonymous set none myminio/jianchabaogao
mc anonymous set none myminio/avatars
mc anonymous set none myminio/usageguides
```

### 步骤2: 运行数据库迁移

```bash
cd backend
python migrate_minio_fields.py
```

### 步骤3: 更新环境配置

确保 `.env` 文件中配置正确:

```env
MINIO_ENDPOINT=192.168.88.205:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=Psbc@1234
MINIO_BUCKET_NAME=binli
MINIO_BUCKET_REPORT=jianchabaogao
MINIO_BUCKET_MEDICAL=binli
MINIO_SECURE=False

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_ENABLE_CONSOLE=True
LOG_ENABLE_FILE=True
```

### 步骤4: 重启后端服务

```bash
# 停止旧服务
pkill -f uvicorn

# 启动新服务
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 步骤5: 更新前端代码

前端需要修改图片访问方式，详见前端改动说明。

## API接口变更

### 新增接口

**1. 获取临时签名URL**
```http
GET /files/presigned-url?file_key=user_xxx/member_xxx/reports/xxx.jpg
```

**2. 获取报告图片URL**
```http
GET /files/report/{report_id}/image?thumbnail=false
```

**3. 获取成员头像URL**
```http
GET /files/member/{member_id}/avatar
```

### 修改接口

**上传接口不再返回完整URL，只返回文件key:**
```json
{
  "success": true,
  "file_key": "user_xxx/member_xxx/reports/20260416093745_a1b2c3d4.jpg",
  "thumbnail_key": "user_xxx/member_xxx/reports_thumbnails/20260416093745_a1b2c3d4_thumbnail.jpg",
  "md5": "d41d8cd98f00b204e9800998ecf8427e"
}
```

## 前端改动指南

### 1. 报告图片展示

**改动前:**
```vue
<image :src="report.image_url" />
```

**改动后:**
```vue
<template>
  <image :src="imageUrl" @error="loadImageUrl" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReportImageUrl } from '@/api/file'

const imageUrl = ref('')
const props = defineProps(['report'])

onMounted(async () => {
  await loadImageUrl()
})

const loadImageUrl = async () => {
  try {
    const res = await getReportImageUrl(props.report.id)
    imageUrl.value = res.url
  } catch (e) {
    console.error('Failed to load image:', e)
  }
}
</script>
```

### 2. 成员头像展示

```vue
<template>
  <image :src="avatarUrl" @error="loadAvatar" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMemberAvatarUrl } from '@/api/file'

const avatarUrl = ref('')
const props = defineProps(['memberId'])

onMounted(async () => {
  await loadAvatar()
})

const loadAvatar = async () => {
  try {
    const res = await getMemberAvatarUrl(props.memberId)
    avatarUrl.value = res.url
  } catch (e) {
    console.error('Failed to load avatar:', e)
  }
}
</script>
```

### 3. 新增API封装

创建 `frontend-mobile/src/api/file.ts`:

```typescript
import request from '@/utils/request'

export const getPresignedUrl = (fileKey: string) => {
  return request.get('/files/presigned-url', {
    params: { file_key: fileKey }
  })
}

export const getReportImageUrl = (reportId: string, thumbnail = false) => {
  return request.get(`/files/report/${reportId}/image`, {
    params: { thumbnail }
  })
}

export const getMemberAvatarUrl = (memberId: string) => {
  return request.get(`/files/member/${memberId}/avatar`)
}
```

## 兼容性说明

### 旧数据处理

系统会自动处理旧数据：
- 旧URL格式：`http://192.168.88.205:9000/jianchabaogao/20260416093745_report.jpg`
- 新URL格式：`user_xxx/member_xxx/reports/20260416093745_a1b2c3d4.jpg`

**判断逻辑:**
```python
if image_url.startswith('http'):
    # 旧格式，直接返回（保持兼容）
    return image_url
else:
    # 新格式，生成签名URL
    return minio_service.get_presigned_url(image_url)
```

### 过渡期策略

系统支持新旧两种格式并存：
1. 旧数据继续使用旧URL
2. 新上传使用新格式
3. 逐步迁移旧数据（可选）

## 性能优化

### 1. 缩略图使用

列表页使用缩略图，提升加载速度：
```javascript
// 报告列表使用缩略图
const imageUrl = await getReportImageUrl(reportId, thumbnail=true)
```

### 2. 图片压缩

上传时自动压缩：
- 最大尺寸: 1920x1920
- 质量: 85%（动态调整到500KB以内）
- 格式: JPEG

### 3. MD5去重

相同文件只存储一份：
```python
# 计算MD5
md5_hash = calculate_md5(file_data)

# 检查是否存在
if existing_file := check_file_by_md5(md5_hash):
    return existing_file_key
```

## 安全特性

### 1. 权限校验

所有图片访问都验证权限：
- 用户只能访问自己的文件
- 医生可以访问绑定患者的文件
- 管理员可以访问所有文件

### 2. 临时URL

- 有效期: 10分钟
- 自动过期，无法长期访问
- 每次访问需要重新生成

### 3. 数据隔离

文件按用户/成员隔离：
```
user_123/
  ├── member_456/
  │   ├── reports/
  │   └── medical_records/
  └── member_789/
      └── reports/
```

### 4. 级联删除

删除成员时自动清理MinIO文件：
```python
# 删除成员时触发
minio_service.delete_files_by_prefix(f"user_{user_id}/member_{member_id}/")
```

## 监控与日志

### 日志输出

所有MinIO操作都记录日志：
```
2026-04-16 09:37:45 - minio_service - INFO - File uploaded: user_123/member_456/reports/20260416093745_a1b2c3d4.jpg
2026-04-16 09:37:46 - minio_service - INFO - Generated presigned URL for user 123
2026-04-16 09:37:47 - minio_service - INFO - Deleted 15 files with prefix: user_123/member_456/
```

### 监控指标

建议监控以下指标：
- 上传成功率
- 签名URL生成成功率
- 图片加载失败率
- 存储空间使用量
- 缩略图命中率

## 故障排查

### 问题1: 图片无法加载

**检查步骤:**
1. 确认bucket是私有访问
2. 检查签名URL是否正确生成
3. 验证用户权限
4. 查看后端日志

### 问题2: 上传失败

**检查步骤:**
1. 确认bucket已创建
2. 检查MinIO连接配置
3. 验证文件大小和类型
4. 查看后端日志

### 问题3: 权限错误

**检查步骤:**
1. 确认用户已登录
2. 验证文件归属
3. 检查数据库关联关系
4. 查看权限校验日志

## 回滚方案

如需回滚到旧版本：

1. 恢复bucket公开策略:
```bash
mc anonymous set download myminio/jianchabaogao
mc anonymous set download myminio/binli
```

2. 回滚代码:
```bash
git checkout <旧版本commit>
```

3. 重启服务

## 联系支持

如有问题，请查看：
- 后端日志: `backend/logs/app.log`
- MinIO日志: MinIO控制台
- 数据库日志: PostgreSQL日志

---

**最后更新:** 2026-04-16
**版本:** v2.0.0
