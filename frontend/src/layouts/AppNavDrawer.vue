<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'
import type { Component } from 'vue'

import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { BaseButton, BaseDrawer, BaseIcon } from '@shared/ui'

import { isNavItemActive, navItemLocation, useNavVisibility } from '@layouts/navigation'

interface Props {
	id: string
	/** Text of the tab in the bottom bar, also the drawer title */
	label: string
	icon: Component
	items: NavItem[]
	/** Variants of the items by position, e.g. green and lime for the first two */
	itemVariants?: DrawerItemVariant[]
	/** Items beyond itemVariants */
	itemVariant?: DrawerItemVariant
}

type DrawerItemVariant = 'primary' | 'secondary' | 'outline' | 'muted'

const props = withDefaults(defineProps<Props>(), {
	itemVariants: () => ['primary', 'secondary'],
	itemVariant: 'outline',
})

function variantAt(index: number): DrawerItemVariant {
	return props.itemVariants[index] ?? props.itemVariant
}

const route = useRoute()
const isVisible = useNavVisibility()
const open = ref<boolean>(false)

const visibleItems = computed<NavItem[]>(() => props.items.filter(isVisible))

// The tab stays active on every page of the drawer, the drawer marks the current one
const isActive = computed<boolean>(() =>
	visibleItems.value.some((item) => isNavItemActive(item, route)),
)

function close(): void {
	open.value = false
}
</script>

<template>
	<button
		type="button"
		class="nav-item"
		:class="{ 'nav-item--active': isActive }"
		:aria-label="`${props.label} Menü öffnen`"
		aria-haspopup="dialog"
		:aria-controls="props.id"
		:aria-expanded="open"
		@click="open = true"
	>
		<BaseIcon
			:icon="props.icon"
			:size="24"
		/>

		<span class="text-md leading-none max-[359px]:sr-only">
			{{ props.label }}
		</span>
	</button>

	<BaseDrawer
		:id="props.id"
		v-model:open="open"
		:title="props.label"
	>
		<!-- Every item keeps its colour; the current page only has aria-current, the tab marks it -->

		<BaseButton
			v-for="(item, index) in visibleItems"
			:key="`${item.routeName}-${JSON.stringify(item.query ?? {})}`"
			:variant="variantAt(index)"
			size="lg"
			class="justify-start"
			:route-name="navItemLocation(item).name"
			:query="navItemLocation(item).query"
			:aria-current="isNavItemActive(item, route) ? 'page' : undefined"
			@click="close"
		>
			<BaseIcon :icon="item.icon!" />

			{{ item.label }}
		</BaseButton>

		<!-- Actions that are no page, e.g. logging out. Same size, own variant. -->
		<slot :close="close" />
	</BaseDrawer>
</template>
