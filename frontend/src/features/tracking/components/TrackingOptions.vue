<script setup lang="ts">
import type { TrackingEntryKind } from '@features/tracking/tracking.types'

import { UtensilsIcon, WeightIcon } from '@lucide/vue'

import { BaseIcon } from '@shared/ui'

const emit = defineEmits<{
	select: [kind: TrackingEntryKind]
}>()

const OPTIONS = [
	{
		kind: 'food' as const,
		label: 'Essen eintragen',
		hint: 'Suchen, scannen oder eine Mahlzeit wählen',
		icon: UtensilsIcon,
	},
	{
		kind: 'weight' as const,
		label: 'Gewicht eintragen',
		hint: 'Ein Wert pro Tag, am besten morgens',
		icon: WeightIcon,
	},
]
</script>

<template>
	<ul class="entry-choice">
		<li
			v-for="option in OPTIONS"
			:key="option.kind"
		>
			<button
				type="button"
				class="entry-choice__option"
				:class="`entry-choice__option--${option.kind}`"
				@click="emit('select', option.kind)"
			>
				<BaseIcon
					class="entry-choice__icon"
					:icon="option.icon"
					:size="32"
				/>

				<span class="entry-choice__text">
					<span class="entry-choice__label">
						{{ option.label }}
					</span>

					<span class="entry-choice__hint">
						{{ option.hint }}
					</span>
				</span>
			</button>
		</li>
	</ul>
</template>
