import { computed, reactive, type ComputedRef, type Ref } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { filterOptions } from './recipes.data'
import type { RecipeFilterKey, RecipeFilterState } from './recipes.types'

function toSlug(value: string): string {
  return value
    .toLowerCase()
    .replace(/ä/g, 'ae')
    .replace(/ö/g, 'oe')
    .replace(/ü/g, 'ue')
    .replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

export function useRecipeFilters(): {
  filters: RecipeFilterState
  activeCount: ComputedRef<number>
  reset: () => void
} {
  const queries = {} as Record<RecipeFilterKey, Ref<string[]>>

  for (const filterOption of filterOptions) {
    const valueBySlug = new Map(
      filterOption.options.map((option) => [toSlug(option.value), option.value]),
    )

    queries[filterOption.key] = useRouteQuery<string, string[]>(filterOption.param, '', {
      transform: {
        get: (raw) =>
          (Array.isArray(raw) ? raw.join(',') : raw)
            .split(',')
            .map((slug) => valueBySlug.get(slug))
            .filter((value): value is string => Boolean(value)),
        set: (values) => values.map(toSlug).join(','),
      },
    })
  }

  const filters = reactive(queries)

  const activeCount = computed<number>(() =>
    Object.values(filters).reduce((total, values) => total + values.length, 0),
  )

  function reset(): void {
    for (const key of Object.keys(filters) as RecipeFilterKey[]) {
      filters[key] = []
    }
  }

  return { filters, activeCount, reset }
}
