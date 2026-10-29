import { useRouter } from 'vue-router'

import { useToast } from '@shared/composables/toast'

import { logout } from '@features/auth/auth.api'
import { useAuthStore } from '@features/auth/auth.store'

/** Sign out with a notice and redirect to the start page, for the account menu and drawer */
export function useLogout(): () => Promise<void> {
	const router = useRouter()
	const auth = useAuthStore()
	const toast = useToast()

	return async () => {
		try {
			await logout()
			auth.signOut()
			toast.show('Du bist abgemeldet. Bis bald!')
			await router.push({ name: 'home' })
		} catch {
			toast.show('Das Abmelden hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
		}
	}
}
