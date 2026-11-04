<script setup lang="ts">
import { ScanBarcodeIcon } from '@lucide/vue'

import { BaseIcon } from '@shared/ui'

import { formatNumber } from '@shared/utils/number'

const EATEN = 1420
const GOAL = 2100

const MACROS = [
	{ label: 'Protein', value: 86, goal: 130, color: 'var(--macro-protein)' },
	{ label: 'Kohlenhydrate', value: 152, goal: 240, color: 'var(--macro-carbs)' },
	{ label: 'Fett', value: 44, goal: 70, color: 'var(--macro-fat)' },
]

const RADIUS = 64
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const dash = `${(EATEN / GOAL) * CIRCUMFERENCE} ${CIRCUMFERENCE}`

const today = new Date().toLocaleDateString('de-DE', {
	weekday: 'short',
	day: 'numeric',
	month: 'short',
})
</script>

<template>
	<div
		class="relative w-full max-w-md mx-auto pb-14"
		aria-hidden="true"
	>
		<div class="flex flex-col gap-6 p-6 pb-14 rounded-xl bg-forest-muted ring-1 ring-forest-border sm:p-8">
			<div class="flex flex-wrap items-center justify-between gap-2">
				<span class="font-display text-2xl font-bold tracking-tighter text-forest-foreground">
					Heute
				</span>

				<span class="tag tag--inverse">
					{{ today }}
				</span>
			</div>

			<div class="@container">
				<div class="flex flex-col items-center gap-6 @sm:flex-row">
					<div class="relative grid place-items-center shrink-0 size-36">
						<svg
							class="absolute inset-0 size-full -rotate-90"
							viewBox="0 0 144 144"
						>
							<circle
								cx="72"
								cy="72"
								:r="RADIUS"
								fill="none"
								stroke="var(--forest-border)"
								stroke-width="12"
							/>

							<circle
								cx="72"
								cy="72"
								:r="RADIUS"
								fill="none"
								stroke="var(--highlight)"
								stroke-width="12"
								stroke-linecap="round"
								:stroke-dasharray="dash"
							/>
						</svg>

						<span class="relative text-center">
							<span class="block figure figure--lg text-forest-foreground">
								{{ formatNumber(GOAL - EATEN) }}
							</span>

							<span class="text-md">
								kcal übrig
							</span>
						</span>
					</div>

					<ul class="flex flex-col gap-3 w-full min-w-0">
						<li
							v-for="macro in MACROS"
							:key="macro.label"
							class="flex flex-col gap-1.5"
						>
							<span class="flex justify-between gap-2 text-md">
								<span class="font-bold text-forest-foreground truncate">
									{{
										macro.label
									}}
								</span>

								<span class="tabular-nums whitespace-nowrap">
									{{ macro.value }} g
								</span>
							</span>

							<span class="h-2 rounded-full bg-forest-border overflow-hidden">
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
		</div>

		<div class="absolute bottom-0 inset-x-4 flex items-center gap-3 p-3 pr-4 rounded-lg bg-card text-foreground shadow-overlay sm:left-auto sm:-right-4 sm:w-72">
			<span class="grid place-items-center shrink-0 size-11 rounded-md bg-highlight">
				<BaseIcon :icon="ScanBarcodeIcon" />
			</span>

			<span class="flex flex-col min-w-0">
				<span class="font-semibold truncate">
					Haferflocken, 40 g
				</span>

				<span class="text-md text-muted-foreground">
					Gescannt – <span class="whitespace-nowrap">
						149 kcal
					</span>
				</span>
			</span>
		</div>
	</div>
</template>
