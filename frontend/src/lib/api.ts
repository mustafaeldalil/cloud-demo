const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchWithAuth(endpoint: string, token: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || 'Request failed')
  }
  
  return response.json()
}

export async function testDatabase(token: string) {
  return fetchWithAuth('/api/test/database', token)
}

export async function testR2(token: string) {
  return fetchWithAuth('/api/test/r2', token, { method: 'POST' })
}

export async function chat(token: string, message: string) {
  return fetchWithAuth('/api/chat', token, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export async function getMetabaseEmbedUrl(token: string, dashboardId: number) {
  return fetchWithAuth(`/api/metabase/embed/${dashboardId}`, token)
}
