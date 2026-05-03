import http from './http'

export function getKnowledgeBaseListApi() {
  return http.get('/api/kb/list')
}

export function createKnowledgeBaseApi(data) {
  return http.post('/api/kb/create', data)
}

export function getDocumentListApi(params) {
  return http.get('/api/kb/documents', { params })
}

export function uploadDocumentApi(formData) {
  return http.post('/api/kb/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function reindexDocumentApi(data) {
  return http.post('/api/kb/documents/reindex', data)
}
