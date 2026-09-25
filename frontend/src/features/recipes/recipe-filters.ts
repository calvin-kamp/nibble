import type { LocationQueryValue } from 'vue-router'
import type { RecipeFilterKey, RecipeFilterState, RecipeListQuery } from './recipes.types'

import { computed, reactive, type ComputedRef, type WritableComputedRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { filterOptions } from './recipes.data'
import { toSlug } from './recipes.utils'

type QueryValue = LocationQueryValue | LocationQueryValue[] | undefined

function firstValue(raw: QueryValue): string {
  return (Array.isArray(raw) ? raw[0] : raw) ?? ''
}

function toSlugList(raw: QueryValue): string[] {
  const value = Array.isArray(raw) ? raw.join(',') : (raw ?? '')

  return value.split(',').filter(Boolean)
}

export function useRecipeFilters(): {
  filters: RecipeFilterState
  search: WritableComputedRef<string>
  page: WritableComputedRef<number>
  apiQuery: ComputedRef<RecipeListQuery>
  activeCount: ComputedRef<number>
  reset: () => void
  resetPage: () => void
} {
  const route = useRoute()
  const router = useRouter()

  /** A changed filter or search starts again on page 1 */
  function write(param: string, value: string): void {
    void router.replace({
      query: { ...route.query, [param]: value || undefined, seite: undefined },
    })
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
    get: () => firstValue(route.query.suche),
    set: (value) => write('suche', value),
  })

  /** Page 1 stays out of the URL; push instead of replace, so the browser back button returns to the previous page */
  const page = computed<number>({
    get: () => {
      const value = Number.parseInt(firstValue(route.query.seite), 10)

      return Number.isInteger(value) && value > 1 ? value : 1
    },
    set: (value) =>
      void router.push({ query: { ...route.query, seite: value > 1 ? String(value) : undefined } }),
  })

  /** Only known values go to the server, in the same form as in the URL */
  const apiQuery = computed<RecipeListQuery>(() => {
    const query: RecipeListQuery = {}

    for (const filterOption of filterOptions) {
      const values = filters[filterOption.key]

      if (values.length > 0) query[filterOption.param] = values.map(toSlug).join(',')
    }

    if (search.value) query.suche = search.value
    if (page.value > 1) query.seite = String(page.value)

    return query
  })

  const activeCount = computed<number>(() =>
    Object.values(filters).reduce((total, values) => total + values.length, 0),
  )

  function reset(): void {
    const query = { ...route.query }

    for (const filterOption of filterOptions) {
      delete query[filterOption.param]
    }

    delete query.seite

    void router.replace({ query })
  }

  function resetPage(): void {
    void router.replace({ query: { ...route.query, seite: undefined } })
  }

  return { filters, search, page, apiQuery, activeCount, reset, resetPage }
}
