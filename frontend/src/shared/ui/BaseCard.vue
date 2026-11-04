<script setup lang="ts">
import type { HTMLAttributes } from 'vue'

import { computed } from 'vue'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	variant?: 'default' | 'inverse'
	size?: 'default' | 'lg'
	as?: 'div' | 'article' | 'section' | 'form'
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
		<slot name="media" />

		<div class="card__body">
			<slot />
		</div>
	</component>
</template>
