import type { LoginCredentials, RegisterCredentials, User } from '@interfaces/auth.types'

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@api/auth.api'
import { HttpError, setAccessToken, setRefreshHandler } from '@lib/http'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const user = ref<User | null>(null)
  const sessionExpired = ref<boolean>(false)

  const isLoggedIn = computed<boolean>(() => accessToken.value !== null)

  function setToken(token: string | null): void {
    accessToken.value = token
    setAccessToken(token)
  }

  function clearSession(): void {
    setToken(null)
    user.value = null
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    const response = await authApi.login(credentials)

    setToken(response.access)
    user.value = response.user
  }

  async function register(credentials: RegisterCredentials): Promise<void> {
    const response = await authApi.register(credentials)

    setToken(response.access)
    user.value = response.user
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  async function refreshAccessToken(): Promise<string | null> {
    try {
      const response = await authApi.refresh()

      setToken(response.access)

      return response.access
    } catch (error) {
      if (error instanceof HttpError) {
        if (isLoggedIn.value) sessionExpired.value = true

        clearSession()
      }

      return null
    }
  }

  async function restoreSession(): Promise<void> {
    const token = await refreshAccessToken()

    if (!token) return

    try {
      user.value = await authApi.getCurrentUser()
    } catch {
      clearSession()
    }
  }

  function acknowledgeSessionExpired(): void {
    sessionExpired.value = false
  }

  setRefreshHandler(refreshAccessToken)

  return {
    accessToken,
    user,
    isLoggedIn,
    sessionExpired,
    login,
    register,
    logout,
    restoreSession,
    acknowledgeSessionExpired,
  }
})
