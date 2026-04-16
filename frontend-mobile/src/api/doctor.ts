import request from '../utils/request'

export function getMyPatients() {
  return request({
    url: '/doctors/patients',
    method: 'GET'
  })
}

export function bindPatient(code: string) {
  return request({
    url: '/doctors/patients/bind',
    method: 'POST',
    data: { code }
  })
}

export function getPatientDetail(patientId: string) {
  return request({
    url: `/doctors/patients/${patientId}`,
    method: 'GET'
  })
}

export function getPatientDiseases(patientId: string) {
  return request({
    url: `/doctors/patients/${patientId}/diseases`,
    method: 'GET'
  })
}

export function getPatientReadings(patientId: string, type?: string) {
  return request({
    url: `/doctors/patients/${patientId}/readings`,
    method: 'GET',
    params: { type }
  })
}

export function getPatientReports(patientId: string) {
  return request({
    url: `/doctors/patients/${patientId}/reports`,
    method: 'GET'
  })
}

export function getPatientReminders(patientId: string) {
  return request({
    url: `/doctors/patients/${patientId}/reminders`,
    method: 'GET'
  })
}
