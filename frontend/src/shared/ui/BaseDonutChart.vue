<script setup lang="ts">
import type { DonutSegment } from '@shared/ui/types'
import type { HTMLAttributes } from 'vue'

import { VisDonut, VisSingleContainer } from '@unovis/vue'
import { computed } from 'vue'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	segments: DonutSegment[]
	/**
	 * With max, the segments fill the ring proportionally (progress, e.g. kcal of the target).
	 * Without max, they share the whole ring (distribution, e.g. macros).
	 */
	max?: number
	/** Description for screen readers, e.g. "1.240 von 1.940 Kilokalorien gegessen" */
	label: string
	centralLabel?: string
	centralSubLabel?: string
	height?: number
	/** Ring width in px */
	arcWidth?: number
	/** Rounded segment ends */
	rounded?: boolean
	/** inverse for dark backgrounds */
	variant?: 'default' | 'inverse'
	/** sm for small rings, e.g. macros next to the large calorie ring */
	size?: 'default' | 'sm'
	class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
	max: undefined,
	centralLabel: undefined,
	centralSubLabel: undefined,
	height: 240,
	arcWidth: 20,
	rounded: true,
	variant: 'default',
	size: 'default',
	class: undefined,
})

const modifierClasses = computed<string[]>(() => {
	return buildModifierClasses('donut-chart', [props.variant, props.size])
})

const FULL_CIRCLE = 2 * Math.PI

const segmentValue = (segment: DonutSegment): number => segment.value
const segmentColor = (segment: DonutSegment): string | undefined => segment.color

const total = computed<number>(() =>
	props.segments.reduce((sum, segment) => sum + Math.max(segment.value, 0), 0),
)

// Without max the segments share the whole ring. With max, a transparent segment is added for
// the remainder, with the background underneath. A shorter angle range would work too, but
// Unovis then centers the partial ring on its bounding box: at 50 % or less it shifts sideways.
const data = computed<DonutSegment[]>(() => {
	if (props.max === undefined) return props.segments

	return [
		...props.segments,
		{ value: Math.max(props.max - total.value, 0), color: 'transparent' },
	]
})
</script>

<template>
	<!-- Own outer element, because Unovis sets its container size via CSS
       and classes like w-60 do not apply there -->
	<div
		class="donut-chart"
		:class="[modifierClasses, props.class]"
	>
		<VisSingleContainer
			:data="data"
			:height="props.height"
			:aria-label="props.label"
		>
			<VisDonut
				:value="segmentValue"
				:color="segmentColor"
				:angle-range="[0, FULL_CIRCLE]"
				show-background
				:background-angle-range="[0, FULL_CIRCLE]"
				:arc-width="props.arcWidth"
				:corner-radius="props.rounded ? props.arcWidth / 2 : 0"
			/>
		</VisSingleContainer>

		<!-- As HTML instead of a Unovis label, so it can be styled with regular CSS -->
		<p
			v-if="props.centralLabel || props.centralSubLabel"
			class="donut-chart__center"
		>
			<span
				v-if="props.centralLabel"
				class="donut-chart__label"
				>{{ props.centralLabel }}</span
			>

			<span
				v-if="props.centralSubLabel"
				class="donut-chart__sub-label"
			>
				{{ props.centralSubLabel }}
			</span>
		</p>
	</div>
</template>
