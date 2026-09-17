import type { AuthNotice } from '@interfaces/auth.types'

import { useRouter } from 'vue-router'
import { useAuthStore } from '@stores/auth.store'

export function useLogout(): { handleLogout: () => Promise<void> } {
  const router = useRouter()
  const auth = useAuthStore()

  async function handleLogout(): Promise<void> {
    const notice: AuthNotice = 'logged-out'

    try {
      await auth.logout()
    } finally {
      await router.push({ name: 'auth-login', query: { notice } })
    }
  }

  return { handleLogout }
}
