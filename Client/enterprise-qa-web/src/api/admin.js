import http from './http'

export function getUsersApi() {
  return http.get('/api/admin/users')
}

export function getDashboardApi() {
  return http.get('/api/admin/dashboard')
}
