import http from './http'

export function getSessionsApi() {
  return http.get('/api/chat/sessions')
}

export function getMessagesApi(params) {
  return http.get('/api/chat/messages', { params })
}

export function askQuestionApi(data) {
  return http.post('/api/chat/ask', data)
}
