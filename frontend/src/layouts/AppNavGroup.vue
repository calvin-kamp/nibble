<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'

import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { BaseIcon } from '@shared/ui'

import { isNavItemActive, navItemLocation, useNavVisibility } from '@layouts/navigation'

// A navigation group with an optional heading, e.g. "Entdecken".
// Items that do not apply to the current user are dropped, an empty group entirely.
interface Props {
	items: NavItem[]
	label?: string
}

const props = withDefaults(defineProps<Props>(), {
	label: undefined,
})

const route = useRoute()
const isVisible = useNavVisibility()

const visibleItems = computed<NavItem[]>(() => props.items.filter(isVisible))
</script>

<template>
	<div
		v-if="visibleItems.length"
		class="flex flex-col gap-2"
	>
		<h2
			v-if="props.label"
			class="sidebar__heading"
		>
			{{ props.label }}
		</h2>

		<ul class="flex flex-col gap-1">
			<li
				v-for="item in visibleItems"
				:key="item.label"
			>
				<RouterLink
					:to="navItemLocation(item)"
					class="sidebar__link"
					:class="{ 'sidebar__link--active': isNavItemActive(item, route) }"
					:aria-current="isNavItemActive(item, route) ? 'page' : 'false'"
				>
					<BaseIcon
						v-if="item.icon"
						:icon="item.icon"
						:size="22"
					/>
					{{ item.label }}
				</RouterLink>
			</li>
		</ul>
	</div>
</template>
