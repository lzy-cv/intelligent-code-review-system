import { defineStore } from 'pinia'
import { getToken, setToken, clearToken } from '../api/http'
import type { UserInfo } from '../api/auth'

const USER_KEY = 'cr-user'

function loadUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: getToken(),
    user: loadUser(),
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
  },
  actions: {
    setAuth(token: string, user: UserInfo) {
      this.token = token
      this.user = user
      setToken(token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      clearToken()
      localStorage.removeItem(USER_KEY)
    },
  },
})
