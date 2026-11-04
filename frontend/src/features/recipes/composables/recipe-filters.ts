import type {
	RecipeFilterValues,
	RecipeListView,
	RecipeSort,
} from '@features/recipes/recipes.types'
import type { ComputedRef, WritableComputedRef } from 'vue'
import type { LocationQuery } from 'vue-router'

import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { EMPTY_FILTERS, SORT_QUERY } from '@features/recipes/recipes.constants'
import { filtersFromQuery, filtersToQuery, viewFromQuery } from '@features/recipes/recipes.utils'

// Most recently used list filters. Breadcrumbs and "Abbrechen" use them to return to the list
// as the user left it, not to the unfiltered one.
const lastListQuery = ref<LocationQuery>({})

export function useRecipeListLocation(): ComputedRef<{ name: string; query: LocationQuery }> {
	return computed(() => ({ name: 'recipe-list', query: lastListQuery.value }))
}

/**
 * Filters and page of the recipe list, stored in the address. That way filtered lists can be
 * shared, and Back from a recipe returns to the same list.
 */
export function useRecipeFilters(): {
	filters: WritableComputedRef<RecipeFilterValues>
	page: WritableComputedRef<number>
	view: ComputedRef<RecipeListView>
	sort: WritableComputedRef<RecipeSort>
	reset: () => void
} {
	const route = useRoute()
	const router = useRouter()

	watch(
		() => route.query,
		(query) => {
			if (route.name === 'recipe-list') lastListQuery.value = query
		},
		{ immediate: true },
	)

	const filters = computed<RecipeFilterValues>({
		get: () => filtersFromQuery(route.query),
		set: (values) => {
			router.replace({
				query: {
					...filtersToQuery(values),
					ansicht: route.query.ansicht,
					sortierung: route.query.sortierung,
				},
			})
		},
	})

	const view = computed<RecipeListView>(() => viewFromQuery(route.query))

	const page = computed<number>({
		get: () => {
			const value = Number(route.query.seite)

			return Number.isInteger(value) && value > 1 ? value : 1
		},
		set: (target) => {
			router.push({ query: { ...route.query, seite: target > 1 ? target : undefined } })
		},
	})

	const sort = computed<RecipeSort>({
		get: () => (route.query.sortierung === SORT_QUERY.popular ? 'popular' : 'newest'),
		set: (value) => {
			router.replace({
				query: { ...route.query, seite: undefined, sortierung: SORT_QUERY[value] },
			})
		},
	})

	function reset(): void {
		filters.value = { ...EMPTY_FILTERS }
	}

	return { filters, page, view, sort, reset }
}
