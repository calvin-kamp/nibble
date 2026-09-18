import type { LocationQueryValue } from 'vue-router'
import type {
  RecipeFilterKey,
  RecipeFilterMode,
  RecipeFilterState,
  RecipeListItem,
} from './recipes.types'

import { computed, reactive, type ComputedRef, type WritableComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { filterOptions } from './recipes.data'
import { toSlug } from './recipes.utils'

type QueryValue = LocationQueryValue | LocationQueryValue[] | undefined

function toSlugList(raw: QueryValue): string[] {
  const value = Array.isArray(raw) ? raw.join(',') : (raw ?? '')

  return value.split(',').filter(Boolean)
}

export function useRecipeFilters(): {
  filters: RecipeFilterState
  search: WritableComputedRef<string>
  activeCount: ComputedRef<number>
  reset: () => void
} {
  const route = useRoute()
  const router = useRouter()

  function write(param: string, value: string): void {
    void router.replace({ query: { ...route.query, [param]: value || undefined } })
  }

  const queries = {} as Record<RecipeFilterKey, WritableComputedRef<string[]>>

  for (const filterOption of filterOptions) {
    const valueBySlug = new Map(
      filterOption.options.map((option) => [toSlug(option.value), option.value]),
    )

    queries[filterOption.key] = computed<string[]>({
      get: () =>
        toSlugList(route.query[filterOption.param])
          .map((slug) => valueBySlug.get(slug))
          .filter((value): value is string => Boolean(value)),
      set: (values) => write(filterOption.param, values.map(toSlug).join(',')),
    })
  }

  const filters = reactive(queries)

  const search = computed<string>({
    get: () => {
      const raw = route.query.suche

      return (Array.isArray(raw) ? raw[0] : raw) ?? ''
    },
    set: (value) => write('suche', value),
  })

  const activeCount = computed<number>(() =>
    Object.values(filters).reduce((total, values) => total + values.length, 0),
  )

  function reset(): void {
    const query = { ...route.query }

    for (const filterOption of filterOptions) {
      delete query[filterOption.param]
    }

    void router.replace({ query })
  }

  return { filters, search, activeCount, reset }
}

function matchesMode(recipeValues: string[], selected: string[], mode: RecipeFilterMode): boolean {
  if (selected.length === 0) return true

  switch (mode) {
    case 'any':
      return selected.some((value) => recipeValues.includes(value))
    case 'all':
      return selected.every((value) => recipeValues.includes(value))
    case 'subset':
      // A recipe without equipment fits every selection.
      return recipeValues.every((value) => selected.includes(value))
  }
}

export function filterRecipes(
  recipes: RecipeListItem[],
  filters: RecipeFilterState,
  search: string,
): RecipeListItem[] {
  const term = search.trim().toLowerCase()

  return recipes.filter(
    (recipe) =>
      (term === '' || recipe.name.toLowerCase().includes(term)) &&
      filterOptions.every((filterOption) =>
        matchesMode(recipe[filterOption.key], filters[filterOption.key], filterOption.mode),
      ),
  )
}
