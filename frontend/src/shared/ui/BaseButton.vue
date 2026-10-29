<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { LocationQueryRaw, RouteParamsRawGeneric } from 'vue-router'

import { computed } from 'vue'

import BaseLink from './BaseLink.vue'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	/** selected for an on state, e.g. "Gespeichert" */
	variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'muted' | 'danger' | 'selected'
	/** sm and icon-sm: visually smaller, the hit area stays 44px */
	size?: 'default' | 'sm' | 'lg' | 'icon' | 'icon-sm' | 'icon-lg'
	type?: HTMLButtonElement['type']
	class?: HTMLAttributes['class']
	href?: string
	routeName?: string
	params?: RouteParamsRawGeneric
	query?: LocationQueryRaw
}

const props = withDefaults(defineProps<Props>(), {
	variant: 'primary',
	size: 'default',
	type: 'button',
	class: undefined,
	href: undefined,
	routeName: undefined,
	params: undefined,
	query: undefined,
})

const modifierClasses = computed<string[]>(() => {
	return buildModifierClasses('button', [props.variant, props.size])
})
</script>

<template>
	<BaseLink
		v-if="props.href || props.routeName"
		variant="no-decoration"
		:href="props.href"
		:route-name="props.routeName"
		:params="props.params"
		:query="props.query"
		class="button"
		:class="[modifierClasses, props.class]"
	>
		<slot />
	</BaseLink>

	<button
		v-else
		:type="props.type"
		class="button"
		:class="[modifierClasses, props.class]"
	>
		<slot />
	</button>
</template>
