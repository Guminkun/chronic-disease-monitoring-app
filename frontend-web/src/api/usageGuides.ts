import request from '../utils/request'

// 获取使用说明列表（管理端）
export function getUsageGuides(params: any) {
  return request({
    url: '/usage-guides/',
    method: 'get',
    params
  })
}

// 获取已发布的使用说明列表（移动端用）
export function getPublishedUsageGuides(params: any) {
  return request({
    url: '/usage-guides/published',
    method: 'get',
    params
  })
}

// 获取使用说明详情
export function getUsageGuide(id: number) {
  return request({
    url: `/usage-guides/${id}`,
    method: 'get'
  })
}

// 创建使用说明
export function createUsageGuide(data: any) {
  return request({
    url: '/usage-guides/',
    method: 'post',
    data
  })
}

// 更新使用说明
export function updateUsageGuide(id: number, data: any) {
  return request({
    url: `/usage-guides/${id}`,
    method: 'put',
    data
  })
}

// 删除使用说明
export function deleteUsageGuide(id: number) {
  return request({
    url: `/usage-guides/${id}`,
    method: 'delete'
  })
}

// 批量删除使用说明
export function batchDeleteUsageGuides(ids: number[]) {
  return request({
    url: '/usage-guides/batch-delete',
    method: 'post',
    data: { ids }
  })
}

// 切换发布状态
export function togglePublish(id: number) {
  return request({
    url: `/usage-guides/${id}/publish`,
    method: 'put'
  })
}

// 上传图片
export function uploadImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/usage-guides/upload/image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 上传视频
export function uploadVideo(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/usage-guides/upload/video',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
