<script setup lang="ts">
import type { ActiveFilter, RecipeFilterValues } from '@features/recipes/recipes.types'

import { XIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'

import { BaseIcon } from '@shared/ui'

import { EMPTY_FILTERS } from '@features/recipes/recipes.constants'
import { activeFilters } from '@features/recipes/recipes.utils'

const emit = defineEmits<{
	/** No filters left, the chips are gone. The page moves focus elsewhere. */
	cleared: []
}>()

// Active filters as removable chips, on every screen size. That way the user can see why
// the list is shorter even while the drawer is closed.
const filters = defineModel<RecipeFilterValues>({ required: true })

const items = computed<ActiveFilter[]>(() => activeFilters(filters.value))

// The removed chip disappears. Focus moves to the chip that takes its place, otherwise to
// "Alle zurücksetzen". The filters live in the address, so the list only changes after
// navigation, which is why a watcher waits for the new chips.
const list = ref<HTMLElement | null>(null)
let focusIndex: number | null = null

watch(
	items,
	() => {
		if (focusIndex === null) return

		const buttons = list.value?.querySelectorAll<HTMLElement>('button') ?? []

		if (buttons.length) buttons[Math.min(focusIndex, buttons.length - 1)]!.focus()
		else emit('cleared')

		focusIndex = null
	},
	{ flush: 'post' },
)

function remove(filter: ActiveFilter, index: number): void {
	focusIndex = index
	filters.value = filter.remove(filters.value)
}

function reset(): void {
	focusIndex = 0
	filters.value = { ...EMPTY_FILTERS, query: filters.value.query }
}
</script>

<template>
	<ul
		v-if="items.length"
		ref="list"
		class="flex flex-wrap items-center gap-2"
		aria-label="Aktive Filter"
	>
		<li
			v-for="(filter, index) in items"
			:key="filter.key"
		>
			<button
				type="button"
				class="chip border-brand bg-brand-soft text-brand-ink"
				:aria-label="`Filter ${filter.label} entfernen`"
				@click="remove(filter, index)"
			>
				{{ filter.label }}
				<BaseIcon
					:icon="XIcon"
					:size="18"
				/>
			</button>
		</li>

		<li>
			<button
				type="button"
				class="link link--underlined px-2"
				@click="reset"
			>
				Alle zurücksetzen
			</button>
		</li>
	</ul>
</template>
