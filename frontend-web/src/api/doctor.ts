import request from '../utils/request'

export function getMyPatients() {
  return request({
    url: '/doctors/patients',
    method: 'get'
  })
}

export function getPatientReadings(patientId: string, type?: string) {
  return request({
    url: `/doctors/patients/${patientId}/readings`,
    method: 'get',
    params: { type }
  })
}

export function getPatientDetail(patientId: string) {
  return request({
    url: `/doctors/patients/${patientId}`,
    method: 'get'
  })
}

export function updatePatientDetail(patientId: string, data: any) {
  return request({
    url: `/doctors/patients/${patientId}`,
    method: 'put',
    data
  })
}
