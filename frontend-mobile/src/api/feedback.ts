import request from '@/utils/request'

// 反馈状态枚举
export enum FeedbackStatus {
  pending = 'pending',       // 待处理
  processing = 'processing', // 处理中
  replied = 'replied',       // 已回复
  closed = 'closed'          // 已关闭
}

// 反馈接口类型
export interface Feedback {
  id: number
  user_id: string
  content: string
  images?: string[]
  contact?: string
  status: FeedbackStatus
  reply_content?: string
  replied_at?: string
  replied_by?: string
  created_at: string
  updated_at: string
  user_name?: string
  user_phone?: string
  replier_name?: string
}

export interface FeedbackListResponse {
  items: Feedback[]
  total: number
  page: number
  page_size: number
}

export interface FeedbackCreate {
  content: string
  images?: string[]
  contact?: string
}

/**
 * 提交意见反馈
 */
export const submitFeedback = (data: FeedbackCreate) => {
  return request({
    url: '/feedback/',
    method: 'POST',
    data
  })
}

/**
 * 获取我的反馈列表
 */
export const getMyFeedbacks = (params: {
  page?: number
  page_size?: number
}) => {
  return request({
    url: '/feedback/my',
    params
  })
}

/**
 * 获取反馈详情
 */
export const getFeedbackDetail = (id: number) => {
  return request({
    url: `/feedback/${id}`
  })
}
