import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref<boolean>(true)

  function login(): void {
    isLoggedIn.value = true
  }

  function logout(): void {
    isLoggedIn.value = false
  }

  return { isLoggedIn, login, logout }
})
