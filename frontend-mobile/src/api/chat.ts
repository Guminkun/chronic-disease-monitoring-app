import request from '@/utils/request'

export interface Message {
  id: number
  sender_id: string
  receiver_id: string
  content: string
  msg_type: string
  is_read: boolean
  created_at: string
}

export const sendMessage = (data: { receiver_id: string, content: string, msg_type?: string }) => {
  return request({
    url: '/chat/messages',
    method: 'POST',
    data
  })
}

export const getMessages = (otherUserId: string, params?: { skip?: number, limit?: number }) => {
  return request({
    url: `/chat/messages/${otherUserId}`,
    method: 'GET',
    data: params
  })
}
