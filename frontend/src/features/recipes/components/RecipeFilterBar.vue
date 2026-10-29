<script setup lang="ts">
import type { FilterGroup, RecipeFilterValues } from '@features/recipes/recipes.types'

import { ChevronDownIcon } from '@lucide/vue'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'

import RecipeFilterGroup from '@features/recipes/components/RecipeFilterGroup.vue'
import { BaseIcon } from '@shared/ui'

import { FILTER_GROUPS } from '@features/recipes/recipes.constants'
import { activeFilters } from '@features/recipes/recipes.utils'

// From desktop up: one button with a popover per filter group. Selections apply immediately,
// the list below updates while the popover is open.
const filters = defineModel<RecipeFilterValues>({ required: true })

function selectedCount(group: FilterGroup): number {
	return activeFilters(filters.value).filter((filter) => filter.key.startsWith(`${group.id}:`))
		.length
}
</script>

<template>
	<ul
		class="flex flex-wrap gap-2"
		aria-label="Filter"
	>
		<li
			v-for="group in FILTER_GROUPS"
			:key="group.id"
		>
			<PopoverRoot>
				<PopoverTrigger
					class="chip"
					:class="{ 'border-brand bg-brand-soft text-brand-ink': selectedCount(group) }"
				>
					{{ group.legend }}
					<span
						v-if="selectedCount(group)"
						class="inline-grid place-items-center min-w-6 h-6 px-1.5 rounded-full bg-brand text-sm tabular-nums text-on-brand"
					>
						{{ selectedCount(group) }}
						<span class="sr-only">gewählt</span>
					</span>

					<BaseIcon
						:icon="ChevronDownIcon"
						:size="18"
					/>
				</PopoverTrigger>

				<PopoverPortal>
					<PopoverContent
						class="popover"
						align="start"
						:side-offset="8"
					>
						<RecipeFilterGroup
							v-model="filters"
							:group="group"
						/>
					</PopoverContent>
				</PopoverPortal>
			</PopoverRoot>
		</li>
	</ul>
</template>
