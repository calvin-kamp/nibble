<script setup lang="ts">
import type { TrackingEntryKind } from '@features/tracking/tracking.types'

import { UtensilsIcon, WeightIcon } from '@lucide/vue'

import { BaseButton, BaseIcon } from '@shared/ui'

const emit = defineEmits<{
	select: [kind: TrackingEntryKind]
}>()

const OPTIONS = [
	{ kind: 'food' as const, label: 'Essen eintragen', icon: UtensilsIcon },
	{ kind: 'weight' as const, label: 'Gewicht eintragen', icon: WeightIcon },
]
</script>

<template>
	<ul class="flex flex-col gap-2">
		<li
			v-for="option in OPTIONS"
			:key="option.kind"
		>
			<BaseButton
				variant="muted"
				size="lg"
				class="w-full justify-start"
				@click="emit('select', option.kind)"
			>
				<BaseIcon
					class="text-brand"
					:icon="option.icon"
				/>
				{{ option.label }}
			</BaseButton>
		</li>
	</ul>
</template>
