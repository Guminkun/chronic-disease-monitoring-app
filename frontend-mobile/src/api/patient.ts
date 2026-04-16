import request from '../utils/request'

export interface Disease {
  id?: number
  name: string
  diagnosis_date: string
  last_check_date?: string
  notes?: string
  status: string
  hospital?: string
  doctor_name?: string
}

export const getPatientDiseases = getDiseases
export const addPatientDisease = addDisease
export const updatePatientDisease = updateDisease
export const deletePatientDisease = deleteDisease

export type ReminderType = 'medication' | 'recheck'

export interface Reminder {
  id?: number
  patient_id?: string
  patient_disease_id: number
  type: ReminderType
  title: string
  schedule_text?: string
  end_date?: string
  is_active?: boolean
  created_at?: string
}

export function getDiseases(memberId?: string) {
  const params = memberId ? { member_id: memberId } : {}
  return request({
    url: '/patients/diseases',
    method: 'GET',
    params
  })
}

export function getSystemDiseases() {
  return request({
    url: '/diseases/',
    method: 'GET'
  })
}

export function addDisease(data: Disease) {
  return request({
    url: '/patients/diseases',
    method: 'POST',
    data
  })
}

export function updateDisease(id: number, data: Disease) {
  return request({
    url: `/patients/diseases/${id}`,
    method: 'PUT',
    data
  })
}

export function deleteDisease(id: number) {
  return request({
    url: `/patients/diseases/${id}`,
    method: 'DELETE'
  })
}

export function getReminders(patientDiseaseId: number) {
  return request({
    url: `/patients/diseases/${patientDiseaseId}/reminders`,
    method: 'GET'
  })
}

export function addReminder(patientDiseaseId: number, data: Reminder) {
  return request({
    url: `/patients/diseases/${patientDiseaseId}/reminders`,
    method: 'POST',
    data
  })
}

export function addPatientReminder(data: Partial<Reminder> & { patient_disease_id?: number }) {
  return request({
    url: '/patients/reminders',
    method: 'POST',
    data
  })
}

export function deleteReminder(reminderId: number) {
  return request({
    url: `/patients/reminders/${reminderId}`,
    method: 'DELETE'
  })
}

// 获取当前患者所有提醒
export function getPatientReminders() {
  return request({
    url: '/patients/reminders',
    method: 'GET'
  })
}

// 更新提醒（开关/修改）
export function updateReminder(reminderId: number, data: Partial<Reminder> & { patient_disease_id?: number }) {
  return request({
    url: `/patients/reminders/${reminderId}`,
    method: 'PUT',
    data
  })
}

export interface HealthReadingData {
  type: string
  value_1: number
  value_2?: number
  unit?: string
  notes?: string
  recorded_at?: string
}

export function addHealthReading(data: HealthReadingData) {
  return request({
    url: '/patients/readings',
    method: 'POST',
    data: data
  })
}

export function getHealthReadings(type: string, memberId?: string) {
  const params = memberId ? { member_id: memberId } : {}
  return request({
    url: `/patients/readings/${type}`,
    method: 'GET',
    params
  })
}

export function getHospitals() {
  return request({
    url: '/hospitals/',
    method: 'GET'
  })
}

export function generateBindingCode() {
  return request({
    url: '/patients/binding-code',
    method: 'POST'
  })
}

export function getMyDoctors() {
  return request({
    url: '/patients/doctors',
    method: 'GET'
  })
}

export function getPatientProfile() {
  return request({
    url: '/patients/me',
    method: 'GET'
  })
}

export function getNotifications() {
  return request({
    url: '/patients/notifications',
    method: 'GET'
  })
}

// Revisit Plans
export interface RevisitPlan {
  id?: number
  patient_disease_id?: number
  cycle_type: 'week' | 'month' | 'quarter' | 'year' | 'custom'
  cycle_value: number
  next_date: string
  reminder_days: number
  notes?: string
  is_active?: boolean
  patient_disease?: any
}

export function getRevisitPlans() {
  return request({
    url: '/patients/revisit-plans',
    method: 'GET'
  })
}

export function addRevisitPlan(data: RevisitPlan) {
  return request({
    url: '/patients/revisit-plans',
    method: 'POST',
    data
  })
}

export function updateRevisitPlan(id: number, data: RevisitPlan) {
  return request({
    url: `/patients/revisit-plans/${id}`,
    method: 'PUT',
    data
  })
}

export function deleteRevisitPlan(id: number) {
  return request({
    url: `/patients/revisit-plans/${id}`,
    method: 'DELETE'
  })
}

// Revisit Records
export interface RevisitRecord {
  id?: number
  plan_id?: number
  actual_date: string
  status?: string
  notes?: string
  plan?: any
}

export function addRevisitRecord(data: RevisitRecord) {
  return request({
    url: '/patients/revisit-records',
    method: 'POST',
    data
  })
}

export function getRevisitRecords() {
  return request({
    url: '/patients/revisit-records',
    method: 'GET'
  })
}

// Medication Plans
export interface MedicationPlan {
  id?: number
  name: string
  manufacturer?: string
  image_url?: string
  dosage_amount: number
  dosage_unit: string
  frequency_type: 'daily' | 'interval' | 'specific_days'
  frequency_value?: string
  taken_times: string[]
  timing_condition?: string
  start_date: string
  end_date?: string
  duration_days?: number
  notes?: string
  patient_disease_id?: number
  is_temporary?: boolean
  paused_until?: string
}

export function addMedicationPlan(data: MedicationPlan) {
  return request({
    url: '/medications/',
    method: 'POST',
    data
  })
}

export interface DailyMedicationTask {
  plan_id: number
  plan_name: string
  dosage: string
  timing: string
  scheduled_time: string
  log_id?: number
  status: 'pending' | 'taken' | 'skipped'
  taken_time?: string
}

export function getDailyMedicationTasks(date: string) {
  return request({
    url: `/medications/daily?date_str=${date}`,
    method: 'GET'
  })
}

export function checkinMedication(data: { plan_id: number, scheduled_time: string, status: string, taken_time?: string, skipped_reason?: string }) {
  return request({
    url: '/medications/checkin',
    method: 'POST',
    data
  })
}
