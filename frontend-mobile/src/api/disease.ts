import request from '../utils/request'

export interface DiseaseDict {
  id: number
  name: string
  code?: string
  category?: string
  chapter_name?: string
  section_name?: string
  subcategory_name?: string
  diagnosis_code?: string
  diagnosis_name?: string
  description?: string
  created_at?: string
}

export function searchDiseases(params: { q?: string, skip?: number, limit?: number } = {}) {
  return request({
    url: '/diseases/',
    method: 'GET',
    params
  })
}
