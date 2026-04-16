import request from '../utils/request'

export function getDiseases(params: any) {
  return request({
    url: '/diseases/',
    method: 'get',
    params
  })
}

export function createDisease(data: any) {
  return request({
    url: '/diseases/',
    method: 'post',
    data
  })
}

export function updateDisease(id: number, data: any) {
  return request({
    url: `/diseases/${id}`,
    method: 'put',
    data
  })
}

export function deleteDisease(id: number) {
  return request({
    url: `/diseases/${id}`,
    method: 'delete'
  })
}

export function batchDeleteDiseases(ids: number[]) {
  return request({
    url: '/diseases/batch-delete',
    method: 'post',
    data: { ids }
  })
}

export function batchUpdateStatus(ids: number[], is_active: boolean) {
  return request({
    url: '/diseases/batch-status',
    method: 'post',
    data: { ids, is_active }
  })
}

export function downloadTemplate() {
  return request({
    url: '/diseases/template',
    method: 'get',
    responseType: 'blob'
  })
}

export function importDiseases(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/diseases/import',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
