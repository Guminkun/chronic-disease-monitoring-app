import request from '../utils/request'

export interface Hospital {
  id: number
  name: string
  alias?: string
  city?: string
  address?: string
  level?: string
}

export function getHospitals(params?: { q?: string, city?: string }) {
  return request({
    url: '/hospitals/',
    method: 'GET',
    params
  })
}

export function searchHospitals(q: string) {
  return request({
    url: '/hospitals/',
    method: 'GET',
    params: { q }
  })
}

export function getHospital(id: number) {
  return request({
    url: `/hospitals/${id}`,
    method: 'GET'
  })
}
