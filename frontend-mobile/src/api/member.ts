import request from '../utils/request'

const getBaseURL = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  // #ifdef MP-WEIXIN
  return apiBase
  // #endif
  
  // #ifdef APP-PLUS
  return apiBase
  // #endif
  
  // #ifdef H5
  return '/api'
  // #endif
  
  return '/api'
}

export interface Member {
  id: string
  nickname: string
  relation: string
  avatar_url?: string
  age?: number
  gender?: string
  height?: number
  weight?: number
  blood_type?: string
  lifestyle?: string
  allergy_history?: string
  past_history?: string
  family_history?: string
  surgery_history?: string
  other_notes?: string
  is_current: boolean
  created_at: string
  updated_at: string
}

export interface MemberFormData {
  nickname: string
  relation: string
  avatar_url?: string
  age?: number | ''
  gender?: string
  height?: number | ''
  weight?: number | ''
  blood_type?: string
  lifestyle?: string
  allergy_history?: string
  past_history?: string
  family_history?: string
  surgery_history?: string
  other_notes?: string
}

export const getMembers = () => {
  return request({ url: '/members/', method: 'GET' })
}

export const getMember = (id: string) => {
  return request({ url: `/members/${id}`, method: 'GET' })
}

export const createMember = (data: MemberFormData) => {
  return request({ url: '/members/', method: 'POST', data })
}

export const updateMember = (id: string, data: Partial<MemberFormData>) => {
  return request({ url: `/members/${id}`, method: 'PUT', data })
}

export const deleteMember = (id: string) => {
  return request({ url: `/members/${id}`, method: 'DELETE' })
}

export const setCurrentMember = (id: string) => {
  return request({ url: `/members/${id}/set-current`, method: 'POST' })
}

export const getCurrentMember = () => {
  return request({ url: '/members/current', method: 'GET' })
}

export const uploadAvatar = (filePath: string): Promise<{ url: string }> => {
  return new Promise((resolve, reject) => {
    const baseURL = getBaseURL()
    uni.uploadFile({
      url: baseURL + '/members/upload-avatar',
      filePath: filePath,
      name: 'file',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          resolve(data)
        } else {
          reject(new Error('上传失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}
