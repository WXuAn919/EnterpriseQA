import http from './http'

export function loginApi(data) {
  return http.post('/api/auth/login', data)
}

export function getProfileApi() {
  return http.get('/api/auth/profile')
}
