import request from '../utils/request'

export type MedicationDictStatus = 'active' | 'inactive'

export interface MedicationDictItem {
  id: number
  title?: string | null
  title_url?: string | null
  number?: string | null
  r3?: string | null
  generic_name?: string | null
  trade_name?: string | null
  pinyin?: string | null
  approval_number?: string | null
  category?: string | null
  manufacturer?: string | null
  therapeutic_system_category?: string | null
  therapeutic_system_subcategory?: string | null
  drug_nature?: string | null
  related_diseases?: string | null
  properties?: string | null
  main_ingredients?: string | null
  indications?: string | null
  specification?: string | null
  adverse_reactions?: string | null
  usage_dosage?: string | null
  contraindications?: string | null
  precautions?: string | null
  pregnancy_lactation?: string | null
  pediatric_use?: string | null
  geriatric_use?: string | null
  drug_interactions?: string | null
  pharmacology_toxicology?: string | null
  pharmacokinetics?: string | null
  storage?: string | null
  expiry_period?: string | null
  status: MedicationDictStatus
  name: string
}

export interface MedicationDictListResponse {
  items: MedicationDictItem[]
  total: number
}

export interface CategoryTreeItem {
  name: string
  subcategories: string[]
}

export interface SearchResultItem {
  type: 'medication' | 'disease'
  id: number
  name: string
  sub_name?: string
  category?: string
  manufacturer?: string
  specification?: string
  section?: string
}

export interface SearchResultResponse {
  items: SearchResultItem[]
  total: number
}

export function searchMedicationDict(params: { q: string; skip?: number; limit?: number }) {
  return request({
    url: '/medication-dict/',
    method: 'GET',
    params
  }) as Promise<MedicationDictListResponse>
}

export function getMedicationDetail(id: number) {
  return request({
    url: `/medication-dict/${id}`,
    method: 'GET'
  }) as Promise<MedicationDictItem>
}

export function getCategoryTree() {
  return request({
    url: '/medication-dict/category-tree',
    method: 'GET'
  }) as Promise<CategoryTreeItem[]>
}

export function searchAll(keyword: string, limit?: number) {
  return request({
    url: '/medication-dict/search-all',
    method: 'GET',
    params: { q: keyword, limit }
  }) as Promise<SearchResultResponse>
}

