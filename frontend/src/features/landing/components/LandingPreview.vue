<script setup lang="ts">
import { ScanBarcodeIcon } from '@lucide/vue'

import { BaseIcon } from '@shared/ui'

import { formatNumber } from '@shared/utils/number'

// A day in the app as an illustration next to the hero text. Made-up values, so it is hidden
// from screen readers; the text next to it says the same in words.
const EATEN = 1420
const GOAL = 2100

const MACROS = [
	{ label: 'Protein', value: 86, goal: 130, color: 'var(--color-macro-protein)' },
	{ label: 'Kohlenhydrate', value: 152, goal: 240, color: 'var(--color-macro-carbs)' },
	{ label: 'Fett', value: 44, goal: 70, color: 'var(--color-macro-fat)' },
]

const progress = `${(EATEN / GOAL) * 360}deg`

const today = new Date().toLocaleDateString('de-DE', {
	weekday: 'short',
	day: 'numeric',
	month: 'short',
})
</script>

<template>
	<div
		class="relative w-full max-w-md mx-auto pb-10"
		aria-hidden="true"
	>
		<div
			class="flex flex-col gap-6 p-6 pb-14 rounded-xl bg-white/8 ring-1 ring-white/15 sm:p-8"
		>
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="font-display text-2xl font-extrabold text-white">Heute</span>

				<span class="px-3 py-1 rounded-full bg-white/10 text-sm font-semibold">{{
					today
				}}</span>
			</div>

			<!-- Like the today card: ring on top on phones, next to the macros from sm -->
			<div class="flex flex-col items-center gap-6 sm:flex-row">
				<!-- Ring as conic gradient: lime up to the eaten share, the track after it -->
				<div
					class="grid place-items-center shrink-0 size-36 rounded-full"
					:style="{
						background: `conic-gradient(var(--color-lime) ${progress}, rgb(255 255 255 / 0.12) 0)`,
					}"
				>
					<div class="grid place-items-center size-28 rounded-full bg-forest text-center">
						<span>
							<span
								class="block font-display text-3xl font-extrabold text-white tabular-nums"
							>
								{{ formatNumber(GOAL - EATEN) }}
							</span>

							<span class="text-sm">kcal übrig</span>
						</span>
					</div>
				</div>

				<ul class="flex flex-col gap-3 w-full min-w-0">
					<li
						v-for="macro in MACROS"
						:key="macro.label"
						class="flex flex-col gap-1.5"
					>
						<span class="flex justify-between gap-2 text-sm">
							<span class="font-bold text-white truncate">{{ macro.label }}</span>

							<span class="tabular-nums">{{ macro.value }} g</span>
						</span>

						<span class="h-2 rounded-full bg-white/12 overflow-hidden">
							<span
								class="block h-full rounded-full"
								:style="{
									width: `${(macro.value / macro.goal) * 100}%`,
									background: macro.color,
								}"
							/>
						</span>
					</li>
				</ul>
			</div>
		</div>

		<!-- Just scanned: shows the barcode scanner without explaining it -->
		<div
			class="absolute bottom-0 inset-x-4  flex items-center gap-3 p-3 pr-4 rounded-lg bg-surface text-ink shadow-xl sm:left-auto sm:-right-4 sm:w-72"
		>
			<span class="grid place-items-center shrink-0 size-11 rounded-md bg-lime">
				<BaseIcon :icon="ScanBarcodeIcon" />
			</span>

			<span class="flex flex-col min-w-0">
				<span class="font-semibold truncate">Haferflocken, 40 g</span>

				<span class="text-sm text-muted">Gescannt · 149 kcal</span>
			</span>
		</div>
	</div>
</template>
