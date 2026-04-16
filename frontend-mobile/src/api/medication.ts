import request from '@/utils/request'

// 类型定义
export interface MedicationPlan {
  id?: number
  name: string
  manufacturer?: string
  image_url?: string
  dosage_amount: number
  dosage_unit: string
  frequency_type: string // daily, interval, specific_days
  frequency_value?: string
  taken_times: string[]
  timing_condition?: string
  start_date: string
  end_date?: string
  duration_days?: number
  notes?: string
  patient_disease_id?: number
  is_temporary?: boolean
  is_active?: boolean
  stock?: number
}

export interface MedicationLog {
  plan_id: number
  scheduled_time: string // ISO string
  taken_time?: string
  status: 'pending' | 'taken' | 'skipped'
  skipped_reason?: string
}

export interface DailyTask {
  plan_id: number
  plan_name: string
  dosage: string
  timing: string
  scheduled_time: string
  log_id?: number
  status: 'pending' | 'taken' | 'skipped'
  taken_time?: string
  is_temporary?: boolean
}

// API 方法
export const getDailyTasks = (dateStr: string, memberId?: string) => {
  const params: any = { date_str: dateStr }
  if (memberId) params.member_id = memberId
  return request({
    url: '/medications/daily',
    method: 'GET',
    params
  })
}

export const createPlan = (data: MedicationPlan) => {
  return request({
    url: '/medications/',
    method: 'POST',
    data
  })
}

export const checkin = (data: MedicationLog) => {
  return request({
    url: '/medications/checkin',
    method: 'POST',
    data
  })
}

export const getPlans = (includeTemporary: boolean = true, memberId?: string) => {
  const params: any = { include_temporary: includeTemporary }
  if (memberId) params.member_id = memberId
  return request({
    url: '/medications/plans',
    method: 'GET',
    params
  })
}

export const updatePlan = (planId: number, data: Partial<MedicationPlan>) => {
  return request({
    url: `/medications/${planId}`,
    method: 'PUT',
    data
  })
}

export const deletePlan = (planId: number) => {
  return request({
    url: `/medications/${planId}`,
    method: 'DELETE'
  })
}

export const pausePlan = (planId: number, days: number) => {
  return request({
    url: `/medications/${planId}/pause`,
    method: 'POST',
    params: { days }
  })
}

export const getStats = (period: 'week' | 'month' = 'week', memberId?: string) => {
  const params: any = { period }
  if (memberId) params.member_id = memberId
  return request({
    url: '/medications/stats',
    method: 'GET',
    params
  })
}

export interface MedicationHistoryParams {
  start_date?: string
  end_date?: string
  member_id?: string
  skip?: number
  limit?: number
}

export interface MedicationHistoryItem {
  id: number
  plan_id: number
  plan_name: string
  dosage: string
  scheduled_time: string
  taken_time: string | null
  status: 'pending' | 'taken' | 'skipped'
  skipped_reason?: string
}

export const getMedicationHistory = (params: MedicationHistoryParams) => {
  return request({
    url: '/medications/history',
    method: 'GET',
    params
  })
}

export interface MakeupReason {
  value: string
  label: string
}

export interface MakeupTask {
  plan_id: number
  plan_name: string
  dosage: string
  scheduled_time: string
  date_str: string
  is_makeup_done: boolean
}

export interface MakeupCreate {
  plan_id: number
  scheduled_time: string
  makeup_reason: string
  makeup_note?: string
}

export const getMakeupReasons = () => {
  return request({
    url: '/medications/makeup-reasons',
    method: 'GET'
  })
}

export const getAvailableMakeupTasks = (dateStr: string, memberId?: string) => {
  const params: any = { date_str: dateStr }
  if (memberId) params.member_id = memberId
  return request({
    url: '/medications/makeup-available',
    method: 'GET',
    params
  })
}

export const createMakeup = (data: MakeupCreate) => {
  return request({
    url: '/medications/makeup',
    method: 'POST',
    data
  })
}

export const getMakeupHistory = (skip: number = 0, limit: number = 50, memberId?: string) => {
  const params: any = { skip, limit }
  if (memberId) params.member_id = memberId
  return request({
    url: '/medications/makeup-history',
    method: 'GET',
    params
  })
}
