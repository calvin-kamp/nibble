<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { computed } from 'vue'

import { buildModifierClasses } from '@shared/utils/classes'

// Only the surface: background, radius, padding. Headings and layout are up to the
// component using the card.
interface Props {
	/** inverse for the dark card */
	variant?: 'default' | 'inverse'
	/** lg for larger cards with more padding */
	size?: 'default' | 'lg'
	as?: 'div' | 'article' | 'section' | 'form'
	/** As tall as the available space, e.g. in a grid. The content is a column; mt-auto pushes down. */
	stretch?: boolean
	class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<Props>(), {
	variant: 'default',
	size: 'default',
	as: 'div',
	stretch: false,
	class: undefined,
})

const modifierClasses = computed<string[]>(() => {
	return buildModifierClasses('card', [
		props.variant,
		props.size,
		props.stretch ? 'stretch' : 'default',
	])
})
</script>

<template>
	<component
		:is="props.as"
		class="card"
		:class="[modifierClasses, props.class]"
	>
		<!-- Edge to edge across the full width, e.g. for images -->
		<slot name="media" />

		<div class="card__body">
			<slot />
		</div>
	</component>
</template>
