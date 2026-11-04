import type { AuthUser } from '@features/auth/auth.types'

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchCurrentUser } from '@features/auth/auth.api'
import { usePendingCalculationStore } from '@features/calorie-calculator/calorie-calculator.store'
import { useOnboardingStore } from '@features/onboarding/onboarding.store'

export const useAuthStore = defineStore('auth', () => {
	const user = ref<AuthUser | null>(null)
	const isReady = ref<boolean>(false)

	// For the navigation guards: they already run at startup, before init() has finished
	let markReady!: () => void
	const ready = new Promise<void>((resolve) => (markReady = resolve))

	const isLoggedIn = computed<boolean>(() => user.value !== null)
	const isEmailVerified = computed<boolean>(() => user.value?.isEmailVerified ?? false)
	const hasCompletedOnboarding = computed<boolean>(
		() => user.value?.hasCompletedOnboarding ?? false,
	)
	const isStaff = computed<boolean>(() => user.value?.isStaff ?? false)
	const hasDataConsent = computed<boolean>(() => user.value?.hasDataConsent ?? false)

	/** On app start: the cookies are httpOnly, so the API has to be asked who is signed in */
	async function init(): Promise<void> {
		try {
			user.value = await fetchCurrentUser()
		} catch {
			// 401 means guest. If the API is unreachable, the app also continues as a guest.
			user.value = null
		} finally {
			isReady.value = true
			markReady()
		}
	}

	function whenReady(): Promise<void> {
		return ready
	}

	async function refreshUser(): Promise<void> {
		user.value = await fetchCurrentUser()
	}

	function signIn(signedInUser: AuthUser): void {
		user.value = signedInUser
	}

	/** Also forgets what was entered in memory, so the next person on this device starts clean */
	function signOut(): void {
		user.value = null
		useOnboardingStore().clear()
		usePendingCalculationStore().clear()
	}

	function setUser(updatedUser: AuthUser): void {
		user.value = updatedUser
	}

	return {
		user,
		isReady,
		isLoggedIn,
		isEmailVerified,
		hasCompletedOnboarding,
		isStaff,
		hasDataConsent,
		init,
		whenReady,
		refreshUser,
		signIn,
		signOut,
		setUser,
	}
})
