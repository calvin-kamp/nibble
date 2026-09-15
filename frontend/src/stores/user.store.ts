import type { Sex } from '@interfaces/user.types'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const name = ref<string>('John Doe')
  const email = ref<string>('john.doe@gmail.com')

  const sex: Sex = 'male'
  const age = 30
  const height = 180
  const weight = 75

  return { name, email, sex, age, height, weight }
})
