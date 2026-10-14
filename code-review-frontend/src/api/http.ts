const TOKEN_KEY = 'cr-token'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// 统一请求：自动携带 Bearer token，401 时清除 token 并跳登录
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken()
  const headers = new Headers(options.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const resp = await fetch(url, { ...options, headers })

  if (resp.status === 401) {
    clearToken()
    if (window.location.pathname !== '/login') window.location.href = '/login'
    throw new Error('登录已过期，请重新登录')
  }
  return resp
}
