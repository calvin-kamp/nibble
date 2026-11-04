<script setup lang="ts">
import type { OnboardingData, OnboardingProgress } from '@features/onboarding/onboarding.types'

import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import OnboardingFlow from '@features/onboarding/components/OnboardingFlow.vue'

import { useToast } from '@shared/composables/toast'

import { useAuthStore } from '@features/auth/auth.store'
import { completeOnboarding, loadOnboardingProgress } from '@features/onboarding/onboarding.api'
import { useOnboardingStore } from '@features/onboarding/onboarding.store'

const router = useRouter()
const toast = useToast()
const auth = useAuthStore()
const onboarding = useOnboardingStore()

const progress = ref<OnboardingProgress | null>(null)
const loaded = ref<boolean>(false)

onMounted(async () => {
	try {
		progress.value =
			onboarding.progress ?? (auth.user ? await loadOnboardingProgress(auth.user) : null)
	} catch {
	} finally {
		loaded.value = true
	}
})

const completing = ref<boolean>(false)

async function onComplete(data: OnboardingData): Promise<void> {
	if (completing.value) return

	completing.value = true

	try {
		auth.setUser(await completeOnboarding(data))
		onboarding.clear()
		toast.show('Alles eingerichtet. Viel Spaß mit nibble!')

		// Only now: before, the router guard would still treat the onboarding as unfinished
		await router.push({ name: data.consent ? 'dashboard' : 'recipe-list' })
	} catch {
		toast.show(
			'Deine Einstellungen konnten nicht gespeichert werden. Versuch es bitte noch einmal.',
			'danger',
		)
	} finally {
		completing.value = false
	}
}
</script>

<template>
	<main
		class="content-wrapper flex flex-col gap-10 pt-6 pb-16 md:pt-8"
		:aria-busy="!loaded"
	>
		<OnboardingFlow
			v-if="loaded"
			:progress="progress"
			@complete="onComplete"
		/>
	</main>
</template>
