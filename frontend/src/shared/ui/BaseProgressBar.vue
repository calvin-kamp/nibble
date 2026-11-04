<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { computed } from 'vue'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	value: number
	max: number
	label?: string
	color?: string
	variant?: 'default' | 'inverse'
	class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
	label: undefined,
	color: undefined,
	variant: 'default',
	class: undefined,
})

const modifierClasses = computed<string[]>(() => {
	return buildModifierClasses('progress-bar', [props.variant])
})

const hasMax = computed<boolean>(() => props.max > 0)

const percent = computed<number>(() => {
	if (!hasMax.value) return 0

	return Math.min(Math.max(props.value / props.max, 0), 1) * 100
})
</script>

<template>
	<div
		class="progress-bar"
		:class="[modifierClasses, props.class]"
		:style="props.color ? { '--progress-bar-color': props.color } : undefined"
		role="progressbar"
		:aria-label="props.label"
		:aria-valuenow="hasMax ? props.value : undefined"
		aria-valuemin="0"
		:aria-valuemax="hasMax ? props.max : undefined"
		:aria-valuetext="hasMax ? undefined : 'Kein Ziel festgelegt'"
	>
		<div
			class="progress-bar__fill"
			:style="{ width: `${percent}%` }"
		/>
	</div>
</template>
