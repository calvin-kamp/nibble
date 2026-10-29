<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { LocationQueryRaw, RouteParamsRawGeneric } from 'vue-router'

import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	variant?: 'underlined' | 'inline' | 'no-decoration' | 'standalone'
	class?: HTMLAttributes['class']
	href?: string
	routeName?: string
	/** Route params, e.g. { id: 'linsen-bowl' } */
	params?: RouteParamsRawGeneric
	/** Route query, e.g. active filters */
	query?: LocationQueryRaw
	hash?: string
}

const props = withDefaults(defineProps<Props>(), {
	variant: 'underlined',
	class: undefined,
	href: undefined,
	routeName: undefined,
	params: undefined,
	query: undefined,
	hash: undefined,
})

const modifierClasses = computed<string[]>(() => {
	return buildModifierClasses('link', [props.variant])
})

const isExternal = computed<boolean>(() => props.href?.startsWith('http') ?? false)
</script>

<template>
	<RouterLink
		v-if="props.routeName"
		:to="{ name: props.routeName, params: props.params, query: props.query, hash: props.hash }"
		class="link"
		:class="[modifierClasses, props.class]"
	>
		<slot />
	</RouterLink>

	<a
		v-else
		:href="props.href"
		class="link"
		:class="[modifierClasses, props.class]"
		:target="isExternal ? '_blank' : undefined"
		:rel="isExternal ? 'noopener noreferrer' : undefined"
	>
		<slot />

		<span
			v-if="isExternal"
			class="sr-only"
		>
			(öffnet in neuem Tab)
		</span>
	</a>
</template>
