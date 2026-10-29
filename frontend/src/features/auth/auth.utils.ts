import type { LocationQuery, Router } from 'vue-router'

import { useToast } from '@shared/composables/toast'

import { useAuthStore } from '@features/auth/auth.store'

/**
 * Target after signing in, taken from ?weiter=. Only paths inside the app, otherwise a crafted
 * link could redirect to a foreign site.
 */
export function redirectTarget(query: LocationQuery): string | null {
	const target = query.weiter

	if (typeof target !== 'string' || !target.startsWith('/') || target.startsWith('//'))
		return null

	return target
}

/**
 * Call when the API reports that the token has expired (e.g. on 401 in the API client).
 * Signs out, shows a notice and leads to the sign-in page. Afterwards the user returns to the
 * page they were on.
 */
export async function expireSession(router: Router): Promise<void> {
	useAuthStore().signOut()
	useToast().show('Deine Sitzung ist abgelaufen. Bitte melde dich neu an.', 'info')

	await router.push({
		name: 'auth-login',
		query: { weiter: router.currentRoute.value.fullPath },
	})
}
