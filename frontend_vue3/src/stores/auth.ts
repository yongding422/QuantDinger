/**
 * Auth store — token, user, login/logout.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/api/request'

export interface User {
  id: number
  username: string
  nickname: string
  email?: string
  avatar: string
  timezone: string
  role: {
    id: string
    permissions: string[]
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  function setAuth(newToken: string, newUser: User) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchUser() {
    try {
      const res = await request.get<{ data: { data: User } }>('/auth/info')
      const userData = res.data.data?.data
      if (userData) {
        user.value = userData
        localStorage.setItem('user', JSON.stringify(userData))
      }
    } catch {
      // silently fail — token might be expired
    }
  }

  return { token, user, isAuthenticated, setAuth, logout, fetchUser }
})
