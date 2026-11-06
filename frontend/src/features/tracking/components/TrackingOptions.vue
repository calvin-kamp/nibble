<script setup lang="ts">
import type { TrackingEntryKind } from '@features/tracking/tracking.types'

import { UtensilsIcon, WeightIcon } from '@lucide/vue'

import { BaseButton, BaseIcon } from '@shared/ui'

const emit = defineEmits<{
	select: [kind: TrackingEntryKind]
}>()

// Food is the main action and gets the primary button, weight the lime one
const OPTIONS = [
	{ kind: 'food' as const, label: 'Essen eintragen', icon: UtensilsIcon, variant: 'primary' as const },
	{
		kind: 'weight' as const,
		label: 'Gewicht eintragen',
		icon: WeightIcon,
		variant: 'secondary' as const,
	},
]
</script>

<template>
	<ul class="flex flex-col gap-3">
		<li
			v-for="option in OPTIONS"
			:key="option.kind"
		>
			<BaseButton
				:variant="option.variant"
				size="lg"
				class="w-full"
				@click="emit('select', option.kind)"
			>
				<BaseIcon :icon="option.icon" />

				{{ option.label }}
			</BaseButton>
		</li>
	</ul>
</template>
