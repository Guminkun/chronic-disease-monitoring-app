import request from '../utils/request'

export function getMedications(params: any) {
  return request({
    url: '/medication-dict/',
    method: 'get',
    params
  })
}

export function getMedicationCategories() {
  return request({
    url: '/medication-dict/categories',
    method: 'get'
  })
}

export function createMedication(data: any) {
  return request({
    url: '/medication-dict/',
    method: 'post',
    data
  })
}

export function updateMedication(id: number, data: any) {
  return request({
    url: `/medication-dict/${id}`,
    method: 'put',
    data
  })
}

export function deleteMedication(id: number) {
  return request({
    url: `/medication-dict/${id}`,
    method: 'delete'
  })
}

export function batchDeleteMedications(ids: number[]) {
  return request({
    url: '/medication-dict/batch-delete',
    method: 'post',
    data: { ids }
  })
}

export function batchUpdateStatus(ids: number[], is_active: boolean) {
  return request({
    url: '/medication-dict/batch-status',
    method: 'post',
    data: { ids, is_active }
  })
}

export function downloadTemplate() {
  return request({
    url: '/medication-dict/template',
    method: 'get',
    responseType: 'blob'
  })
}

export function importMedications(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/medication-dict/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
