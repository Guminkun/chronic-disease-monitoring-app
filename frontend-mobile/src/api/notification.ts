import request from '../utils/request'

export interface NotificationItem {
  id: number
  patient_id: string
  member_id?: string
  title: string
  content: string
  type: string
  category: string
  source_id?: string
  source_type?: string
  priority: number
  extra_data?: Record<string, any>
  is_read: boolean
  read_at?: string
  is_handled: boolean
  handled_at?: string
  handler_type?: string
  created_at: string
  member_nickname?: string
  member_relation?: string
}

export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  unread_count: number
  unhandled_count: number
}

export interface NotificationQueryParams {
  member_id?: string
  is_read?: boolean
  is_handled?: boolean
  category?: string
  type?: string
  all_members?: boolean
  skip?: number
  limit?: number
}

export function getNotifications(params?: NotificationQueryParams): Promise<NotificationListResponse> {
  return request({
    url: '/notifications/',
    method: 'GET',
    params
  })
}

export function markNotificationAsRead(notificationId: number) {
  return request({
    url: `/notifications/${notificationId}/read`,
    method: 'PUT'
  })
}

export function markAllNotificationsAsRead(memberId?: string) {
  const params = memberId ? { member_id: memberId } : {}
  return request({
    url: '/notifications/read-all',
    method: 'PUT',
    params
  })
}

export function deleteNotification(notificationId: number) {
  return request({
    url: `/notifications/${notificationId}`,
    method: 'DELETE'
  })
}

export function getUnreadNotificationCount(memberId?: string) {
  const params = memberId ? { member_id: memberId } : {}
  return request({
    url: '/notifications/unread-count',
    method: 'GET',
    params
  })
}

export function createNotification(data: {
  title: string
  content: string
  type: string
  category: string
  member_id?: string
  source_id?: string
  source_type?: string
  priority?: number
  extra_data?: Record<string, any>
}) {
  return request({
    url: '/notifications/',
    method: 'POST',
    data
  })
}

export function getPatientDynamicNotifications() {
  return request({
    url: '/patients/notifications',
    method: 'GET'
  })
}

export function markNotificationAsHandled(notificationId: number, handlerType?: string) {
  return request({
    url: `/notifications/${notificationId}/handle`,
    method: 'PUT',
    params: { handler_type: handlerType || 'user' }
  })
}

export function markAllNotificationsAsHandled(memberId?: string, type?: string) {
  const params: any = {}
  if (memberId) params.member_id = memberId
  if (type) params.type = type
  return request({
    url: '/notifications/handle-all',
    method: 'PUT',
    params
  })
}
