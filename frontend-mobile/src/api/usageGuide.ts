import request from '../utils/request'

export interface UsageGuide {
  id: number
  title: string
  description?: string
  content?: string
  cover_image?: string
  images?: string[]
  videos?: string[]
  views: number
  is_published: boolean
  created_at: string
  updated_at: string
}

// 获取已发布的使用说明列表（移动端）
export function getPublishedUsageGuides(params?: { skip?: number, limit?: number }) {
  return request({
    url: '/usage-guides/published',
    method: 'GET',
    data: params
  })
}

// 获取使用说明详情
export function getUsageGuide(id: number) {
  return request({
    url: `/usage-guides/${id}`,
    method: 'GET'
  })
}
