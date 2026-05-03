import http, { API_BASE_URL } from './http'

export function getSessionsApi() {
  return http.get('/api/chat/sessions')
}

export function getMessagesApi(params) {
  return http.get('/api/chat/messages', { params })
}

export function askQuestionApi(data) {
  return http.post('/api/chat/ask', data)
}

export async function streamQuestionApi(data, callbacks = {}) {
  const token = localStorage.getItem('enterprise-qa-token')
  const response = await fetch(`${API_BASE_URL}/api/chat/ask/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
  })

  const contentType = response.headers.get('content-type') || ''
  if (!response.ok || contentType.includes('application/json')) {
    let message = '问答请求失败'

    try {
      const payload = await response.json()
      message = payload?.message || message
    } catch {
      const text = await response.text()
      message = text || message
    }

    throw new Error(message)
  }

  if (!response.body) {
    throw new Error('浏览器不支持流式响应')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  const handleLine = (line) => {
    if (!line.trim()) {
      return
    }

    const payload = JSON.parse(line)
    const { event, data: eventData, message } = payload

    if (event === 'start') {
      callbacks.onStart?.(eventData)
      return
    }

    if (event === 'context') {
      callbacks.onContext?.(eventData)
      return
    }

    if (event === 'chunk') {
      callbacks.onChunk?.(eventData || '')
      return
    }

    if (event === 'complete') {
      callbacks.onComplete?.(eventData)
      return
    }

    if (event === 'error') {
      throw new Error(message || '问答失败')
    }
  }

  while (true) {
    const { value, done } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      handleLine(line)
    }
  }

  buffer += decoder.decode()
  if (buffer.trim()) {
    handleLine(buffer)
  }
}
