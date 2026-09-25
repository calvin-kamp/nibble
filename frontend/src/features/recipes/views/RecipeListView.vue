<script setup lang="ts">
import { PlusIcon } from '@lucide/vue'
import { computed, onUnmounted, ref, useTemplateRef, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { UiButton, UiIcon, UiPagination } from '@components/ui'
import { useAuthStore } from '@stores/auth.store'
import { useRecipeStore } from '@stores/recipe.store'
import RecipeFilterBar from '../components/RecipeFilterBar.vue'
import RecipeFilterChips from '../components/RecipeFilterChips.vue'
import RecipeList from '../components/RecipeList.vue'
import RecipeSearchBar from '../components/RecipeSearchBar.vue'
import { useRecipeFilters } from '../recipe-filters'
import { RECIPES_PER_PAGE } from '../recipes.data'

const { search, page, apiQuery } = useRecipeFilters()

const route = useRoute()

const auth = useAuthStore()

const recipeStore = useRecipeStore()

const heading = useTemplateRef<HTMLHeadingElement>('heading')

const searchInput = ref<string>(search.value)

let timer: ReturnType<typeof setTimeout> | undefined

watch(searchInput, (value) => {
  clearTimeout(timer)

  timer = setTimeout(() => {
    search.value = value.trim()
  }, 250)
})

watch(
  apiQuery,
  (query) => {
    // The watcher fires once more while leaving the page, with the next route's query.
    if (route.name !== 'recipe-list') return

    void recipeStore.loadRecipes(query)
  },
  { immediate: true },
)

onUnmounted(() => clearTimeout(timer))

const showPagination = computed<boolean>(
  () => !recipeStore.pageNotFound && recipeStore.totalCount > RECIPES_PER_PAGE,
)

const rangeText = computed<string | null>(() => {
  if (recipeStore.loadError) return null

  const from = (page.value - 1) * RECIPES_PER_PAGE + 1
  const to = Math.min(page.value * RECIPES_PER_PAGE, recipeStore.totalCount)

  return `Rezepte ${from}–${to} von ${recipeStore.totalCount}`
})

/** Announced after every change to search, filters or page, without moving the focus */
const resultStatus = computed<string>(() => {
  if (recipeStore.isLoading || recipeStore.loadError) return ''

  if (recipeStore.pageNotFound) return 'Diese Seite gibt es nicht'

  return recipeStore.totalCount === 1 ? '1 Rezept' : `${recipeStore.totalCount} Rezepte`
})

function changePage(value: number): void {
  page.value = value

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  window.scrollTo({ top: 0, behavior: reducedMotion ? 'auto' : 'smooth' })

  heading.value?.focus({ preventScroll: true })
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-4">
      <h1
        ref="heading"
        tabindex="-1"
        class="outline-hidden"
      >
        Rezepte
      </h1>

      <p class="text-muted-foreground max-w-prose">
        Finde Rezepte, die zu deinem Tag passen — gefiltert nach Ernährungsform, Mahlzeit und
        Ausstattung.
      </p>
    </div>

    <div
      class="sticky top-16 z-10 flex items-center gap-2 px-4 py-3 -mx-4 bg-background border-b md:gap-3 md:px-5 md:-mx-5 lg:static lg:z-auto lg:px-0 lg:mx-0"
    >
      <div class="min-w-0 flex-1 md:max-w-sm">
        <RecipeSearchBar v-model="searchInput" />
      </div>

      <RecipeFilterBar />

      <UiButton
        v-if="auth.isLoggedIn"
        as-child
        class="ml-auto w-11 justify-center px-0 md:w-auto md:px-4"
      >
        <RouterLink
          :to="{ name: 'recipe-create' }"
          aria-label="Rezept erstellen"
        >
          <UiIcon
            :icon="PlusIcon"
            :size="20"
          />

          <span class="hidden md:inline">Rezept erstellen</span>
        </RouterLink>
      </UiButton>
    </div>

    <RecipeFilterChips class="-mt-2" />

    <p
      role="status"
      class="sr-only"
    >
      {{ resultStatus }}
    </p>

    <RecipeList />

    <div
      v-if="showPagination"
      class="flex flex-col gap-3"
    >
      <p
        v-if="rangeText"
        class="text-muted-foreground text-sm tabular-nums"
      >
        {{ rangeText }}
      </p>

      <UiPagination
        :page="page"
        :total="recipeStore.totalCount"
        :items-per-page="RECIPES_PER_PAGE"
        @update:page="changePage"
      />
    </div>
  </div>
</template>
