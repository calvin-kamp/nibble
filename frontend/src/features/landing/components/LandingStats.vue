<script setup lang="ts">
import type { PublicStats } from '@features/landing/landing.types'

import { computed, onMounted, ref } from 'vue'

import { fetchPublicStats } from '@features/landing/landing.api'
import { formatNumber } from '@shared/utils/number'

// Totals from the backend. Without them the section is simply left out; the page works
// without numbers.
const stats = ref<PublicStats | null>(null)
const loading = ref<boolean>(true)

onMounted(async () => {
	try {
		stats.value = await fetchPublicStats()
	} catch {
		stats.value = null
	} finally {
		loading.value = false
	}
})

const items = computed(() =>
	stats.value
		? [
				{ value: stats.value.users, label: 'Mitglieder' },
				{ value: stats.value.recipes, label: 'Rezepte aus der Community' },
				{ value: stats.value.foods, label: 'Lebensmittel zum Suchen und Scannen' },
				{ value: stats.value.entries, label: 'Einträge im Tagebuch' },
			]
		: [],
)
</script>

<template>
	<section
		v-if="loading || stats"
		aria-labelledby="landing-stats-title"
		:aria-busy="loading"
	>
		<h2
			id="landing-stats-title"
			class="sr-only"
		>
			nibble in Zahlen
		</h2>

		<!-- Placeholders only for the eye; a description list may hold nothing but terms and values -->
		<div
			v-if="loading"
			class="grid grid-cols-12 gap-px overflow-hidden rounded-xl bg-divider"
			aria-hidden="true"
		>
			<div
				v-for="index in 4"
				:key="index"
				class="flex flex-col items-center gap-3 col-span-12 p-6 bg-surface sm:col-span-6 md:p-8 lg:col-span-3"
			>
				<span class="h-10 w-24 rounded-md bg-surface-muted animate-pulse" />

				<span class="h-4 w-32 rounded-sm bg-surface-muted animate-pulse" />
			</div>
		</div>

		<dl
			v-else
			class="grid grid-cols-12 gap-px overflow-hidden rounded-xl bg-divider"
		>
			<div
				v-for="item in items"
				:key="item.label"
				class="flex flex-col-reverse justify-end items-center gap-1 col-span-12 p-6 text-center bg-surface sm:col-span-6 md:p-8 lg:col-span-3"
			>
				<dt class="text-sm text-ink-soft md:text-md">{{ item.label }}</dt>

				<dd
					class="font-display text-3xl font-extrabold leading-none tracking-tighter tabular-nums md:text-5xl"
				>
					{{ formatNumber(item.value) }}
				</dd>
			</div>
		</dl>
	</section>
</template>
