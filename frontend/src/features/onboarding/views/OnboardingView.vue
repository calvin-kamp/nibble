<script setup lang="ts">
import type { OnboardingData, OnboardingProgress } from '@features/onboarding/onboarding.types'

import { onMounted, ref } from 'vue'

import OnboardingFlow from '@features/onboarding/components/OnboardingFlow.vue'

import { useToast } from '@shared/composables/toast'

import { useAuthStore } from '@features/auth/auth.store'
import { completeOnboarding, loadOnboardingProgress } from '@features/onboarding/onboarding.api'
import { useOnboardingStore } from '@features/onboarding/onboarding.store'
import { ApiError } from '@shared/api/client'

const toast = useToast()
const auth = useAuthStore()
const onboarding = useOnboardingStore()

// Continue where the user left off: from memory, after a reload at the backend's step
const progress = ref<OnboardingProgress | null>(null)
const loaded = ref<boolean>(false)

onMounted(async () => {
	try {
		progress.value =
			onboarding.progress ?? (auth.user ? await loadOnboardingProgress(auth.user) : null)
	} catch {
		// Without the backend's step, onboarding starts at the beginning
	} finally {
		loaded.value = true
	}
})

async function onComplete(data: OnboardingData): Promise<void> {
	try {
		auth.setUser(await completeOnboarding(data))
		onboarding.clear()
		toast.show('Alles eingerichtet. Viel Spaß mit Nibble!')
	} catch (error) {
		if (error instanceof ApiError && error.code === 'username_taken') {
			toast.show(
				'Dieser Benutzername ist schon vergeben. Geh zurück und wähl einen anderen.',
				'danger',
			)
		} else {
			toast.show(
				'Deine Einstellungen konnten nicht gespeichert werden. Versuch es bitte noch einmal.',
				'danger',
			)
		}
	}
}
</script>

<template>
	<main
		class="content-wrapper flex flex-col gap-6 pt-6 pb-12 md:gap-8 md:pt-8"
		:aria-busy="!loaded"
	>
		<OnboardingFlow
			v-if="loaded"
			:progress="progress"
			@complete="onComplete"
		/>
	</main>
</template>
