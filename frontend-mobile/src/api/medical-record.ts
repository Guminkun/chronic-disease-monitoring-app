import request from '../utils/request'
import { BASE_URL } from '../utils/request'

export interface MedicalRecord {
  id?: string
  patient_id?: string
  member_id?: string
  title?: string
  hospital?: string
  patient_name?: string
  age?: string
  gender?: string
  report_type?: string
  report_date?: string
  image_url?: string
  chief_complaint?: string
  present_illness?: string
  past_history?: string
  personal_history?: string
  family_history?: string
  data?: any
  created_at?: string
}

export function getMedicalRecords(memberId?: string) {
  const params = memberId ? { member_id: memberId } : {}
  return request({
    url: '/patients/medical-records',
    method: 'GET',
    params
  })
}

export function getMedicalRecordDetail(id: string) {
  return request({
    url: `/patients/medical-records/${id}`,
    method: 'GET'
  })
}

export function deleteMedicalRecord(id: string) {
  return request({
    url: `/patients/medical-records/${id}`,
    method: 'DELETE'
  })
}

export function batchDeleteMedicalRecords(ids: string[]) {
  return request({
    url: '/patients/medical-records/batch-delete',
    method: 'POST',
    data: { ids }
  })
}

export function uploadMedicalRecord(filePath: string, memberId?: string) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    let url = `${BASE_URL}/patients/medical-records/upload`
    // #ifdef MP-WEIXIN
    url = 'http://127.0.0.1:8000/patients/medical-records/upload'
    // #endif
    // #ifdef APP-PLUS
    url = 'http://192.168.1.100:8000/patients/medical-records/upload'
    // #endif
    
    const formData: any = {}
    if (memberId) {
      formData.member_id = memberId
    }
    
    uni.uploadFile({
      url,
      filePath: filePath,
      name: 'file',
      formData: formData,
      timeout: 180000,
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (uploadFileRes) => {
        if (uploadFileRes.statusCode === 200) {
          try {
            const data = JSON.parse(uploadFileRes.data)
            resolve(data)
          } catch (e) {
            reject(new Error('Failed to parse response'))
          }
        } else if (uploadFileRes.statusCode === 401 || uploadFileRes.statusCode === 403) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('role')
          uni.showToast({
            title: '登录已过期',
            icon: 'none'
          })
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/login/login'
            })
          }, 1500)
          reject(new Error('Unauthorized'))
        } else {
          try {
            const errObj = JSON.parse(uploadFileRes.data || '{}')
            const detail = errObj?.detail || `状态码 ${uploadFileRes.statusCode}`
            reject(new Error(detail))
          } catch {
            reject(new Error(`上传失败，状态码 ${uploadFileRes.statusCode}`))
          }
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
