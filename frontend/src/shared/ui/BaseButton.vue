<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import type { LocationQueryRaw, RouteParamsRawGeneric } from 'vue-router'

import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { buildModifierClasses } from '@shared/utils/classes'

interface Props {
	/** selected for an on state, e.g. "Gespeichert". danger confirms a deletion, danger-soft starts one. */
	variant?:
		| 'primary'
		| 'secondary'
		| 'ghost'
		| 'outline'
		| 'muted'
		| 'danger'
		| 'danger-soft'
		| 'selected'
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

const isExternal = computed<boolean>(() => props.href?.startsWith('http') ?? false)
</script>

<template>
	<!-- A link that looks like a button gets no link classes: link.css loads after button.css
		and would override sizes such as button--lg -->
	<RouterLink
		v-if="props.routeName"
		:to="{ name: props.routeName, params: props.params, query: props.query }"
		class="button"
		:class="[modifierClasses, props.class]"
	>
		<slot />
	</RouterLink>

	<a
		v-else-if="props.href"
		:href="props.href"
		class="button"
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

	<button
		v-else
		:type="props.type"
		class="button"
		:class="[modifierClasses, props.class]"
	>
		<slot />
	</button>
</template>
