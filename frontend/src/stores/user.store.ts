import type { Sex } from '@interfaces/user.types'

import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const sex: Sex = 'male'
  const age = 30
  const height = 180
  const weight = 75

  return { sex, age, height, weight }
})
