import type { OnboardingProgress } from '@features/onboarding/onboarding.types'

import { defineStore } from 'pinia'
import { ref } from 'vue'

// Where the user is in onboarding and what they entered so far. Kept in memory only, never in
// browser storage: leaving the page and coming back resumes here, after a reload onboarding
// continues at the step the backend knows.
export const useOnboardingStore = defineStore('onboarding', () => {
	const progress = ref<OnboardingProgress | null>(null)

	function save(current: OnboardingProgress): void {
		progress.value = current
	}

	function clear(): void {
		progress.value = null
	}

	return { progress, save, clear }
})
