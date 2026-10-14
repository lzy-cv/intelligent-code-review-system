import { apiFetch } from './http'

export interface UserInfo {
  id: number
  username: string
  created_at?: string
}

export interface AuthResult {
  token: string
  user: UserInfo
}

async function authCall(path: string, username: string, password: string): Promise<AuthResult> {
  const resp = await apiFetch(path, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  if (!resp.ok) {
    let detail = `请求失败(${resp.status})`
    try {
      detail = (await resp.json()).detail || detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return (await resp.json()) as AuthResult
}

export function login(username: string, password: string) {
  return authCall('/api/auth/login', username, password)
}

export function register(username: string, password: string) {
  return authCall('/api/auth/register', username, password)
}
