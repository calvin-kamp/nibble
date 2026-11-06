<script setup lang="ts">
import type { NavItem } from '@layouts/navigation'

import { NotebookPenIcon } from '@lucide/vue'

import AppNavDrawer from '@layouts/AppNavDrawer.vue'

import { TRACKING_NAV } from '@layouts/navigation'

// The sidebar says "Essen", here the two diaries are named after what they hold
const items: NavItem[] = TRACKING_NAV.map((item) =>
	item.routeName === 'diary-food' ? { ...item, label: 'Ernährung' } : item,
)
</script>

<template>
	<AppNavDrawer
		id="diary-drawer"
		label="Tagebuch"
		:icon="NotebookPenIcon"
		:items="items"
	/>
</template>
