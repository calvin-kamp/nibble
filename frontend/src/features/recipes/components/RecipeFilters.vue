<script setup lang="ts">
import type { RecipeFilterValues } from '@features/recipes/recipes.types'

import RecipeFilterGroup from '@features/recipes/components/RecipeFilterGroup.vue'

import { FILTER_GROUPS } from '@features/recipes/recipes.constants'

// All filter groups stacked, for the drawer on phone and tablet
const filters = defineModel<RecipeFilterValues>({ required: true })
</script>

<template>
	<div class="flex flex-col gap-6">
		<RecipeFilterGroup
			v-for="group in FILTER_GROUPS"
			:key="group.id"
			v-model="filters"
			:group="group"
		/>
	</div>
</template>
