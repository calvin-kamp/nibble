import type { AuthUser } from '@features/auth/auth.types'

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchCurrentUser } from '@features/auth/auth.api'
import { usePendingCalculationStore } from '@features/calorie-calculator/calorie-calculator.store'
import { useOnboardingStore } from '@features/onboarding/onboarding.store'

export const useAuthStore = defineStore('auth', () => {
	const user = ref<AuthUser | null>(null)
	/** Whether init() has finished. Until then it is unknown whether anyone is signed in. */
	const isReady = ref<boolean>(false)

	// For the navigation guards: they already run at startup, before init() has finished
	let markReady!: () => void
	const ready = new Promise<void>((resolve) => (markReady = resolve))

	const isLoggedIn = computed<boolean>(() => user.value !== null)
	const isEmailVerified = computed<boolean>(() => user.value?.isEmailVerified ?? false)
	const hasCompletedOnboarding = computed<boolean>(
		() => user.value?.hasCompletedOnboarding ?? false,
	)
	/** Moderation: approves or rejects submitted recipes on the admin page */
	const isStaff = computed<boolean>(() => user.value?.isStaff ?? false)
	/** Consent from onboarding: without it there is no tracking and no saved meals */
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

	/** Resolves once it is known whether anyone is signed in */
	function whenReady(): Promise<void> {
		return ready
	}

	/** Reloads the state, e.g. after the email address has been confirmed */
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

	/** New state from an API response, e.g. after onboarding */
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
