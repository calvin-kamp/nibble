<script setup lang="ts">
import type { PublicStats } from '@features/landing/landing.types'

import { computed, onMounted, ref } from 'vue'

import { fetchPublicStats } from '@features/landing/landing.api'
import { formatMilestone } from '@shared/utils/number'

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

// Small numbers work against the page ("11 members"), so each figure only shows from a
// minimum on, and the block only with at least two figures.
const MINIMUM = { users: 5, recipes: 10, foods: 1000, entries: 100 } as const
const MIN_ITEMS = 2

const items = computed(() =>
	stats.value
		? [
				{ key: 'users', value: stats.value.users, label: 'Mitglieder' },
				{ key: 'recipes', value: stats.value.recipes, label: 'Rezepte aus der Community' },
				{ key: 'foods', value: stats.value.foods, label: 'Lebensmittel' },
				{ key: 'entries', value: stats.value.entries, label: 'Einträge im Tagebuch' },
			].filter((item) => item.value >= MINIMUM[item.key as keyof typeof MINIMUM])
		: [],
)

const isShown = computed<boolean>(() => loading.value || items.value.length >= MIN_ITEMS)

// Static class names so Tailwind finds them: the tiles share one row on large screens
const LG_SPAN: Record<number, string> = {
	2: 'lg:col-span-6',
	3: 'lg:col-span-4',
	4: 'lg:col-span-3',
}
</script>

<template>
	<section
		v-if="isShown"
		aria-labelledby="landing-stats-title"
		:aria-busy="loading"
	>
		<h2
			id="landing-stats-title"
			class="sr-only"
		>
			nibble in Zahlen
		</h2>

		<div
			v-if="loading"
			class="grid grid-cols-12 gap-px overflow-hidden rounded-xl border border-divider bg-divider"
			aria-hidden="true"
		>
			<div
				v-for="index in 4"
				:key="index"
				class="flex flex-col items-center gap-3 col-span-12 p-6 bg-card sm:col-span-6 md:p-8 lg:col-span-3"
			>
				<span class="h-10 w-24 rounded-md bg-muted animate-pulse" />

				<span class="h-4 w-32 rounded-sm bg-muted animate-pulse" />
			</div>
		</div>

		<dl
			v-else
			class="grid grid-cols-12 gap-px overflow-hidden rounded-xl border border-divider bg-divider"
		>
			<div
				v-for="(item, index) in items"
				:key="item.label"
				class="flex flex-col-reverse justify-end items-center gap-1 col-span-12 p-6 text-center bg-card sm:col-span-6 md:p-8"
				:class="[LG_SPAN[items.length], { 'sm:col-span-12': items.length === 3 && index === 2 }]"
			>
				<dt class="text-md text-foreground/80">
					{{ item.label }}
				</dt>

				<dd class="figure figure--lg md:text-5xl">
					{{ formatMilestone(item.value) }}
				</dd>
			</div>
		</dl>
	</section>
</template>
