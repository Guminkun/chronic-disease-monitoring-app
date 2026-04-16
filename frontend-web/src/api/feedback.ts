import request from '../utils/request'

// 反馈状态类型
export type FeedbackStatus = 'pending' | 'processing' | 'replied' | 'closed'

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

export interface FeedbackReply {
  reply_content: string
}

/**
 * 获取反馈列表（管理端）
 */
export const getFeedbacks = (params: {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}) => {
  return request({
    url: '/feedback/',
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

/**
 * 更新反馈状态
 */
export const updateFeedbackStatus = (id: number, status: string) => {
  return request({
    url: `/feedback/${id}/status`,
    method: 'PUT',
    data: { status }
  })
}

/**
 * 回复反馈
 */
export const replyFeedback = (id: number, reply_content: string) => {
  return request({
    url: `/feedback/${id}/reply`,
    method: 'POST',
    data: { reply_content }
  })
}

/**
 * 删除反馈
 */
export const deleteFeedback = (id: number) => {
  return request({
    url: `/feedback/${id}`,
    method: 'DELETE'
  })
}
