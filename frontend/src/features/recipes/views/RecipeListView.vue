<script setup lang="ts">
import RecipeFilterBar from '../components/RecipeFilterBar.vue'
import RecipeList from '../components/RecipeList.vue'
import RecipeSearchBar from '../components/RecipeSearchBar.vue'
import { useRecipeFilters } from '../recipe-filters'
import { onUnmounted, ref, watch } from 'vue'

const { search } = useRecipeFilters()

const searchInput = ref<string>(search.value)

let timer: ReturnType<typeof setTimeout> | undefined

watch(searchInput, (value) => {
  clearTimeout(timer)

  timer = setTimeout(() => {
    search.value = value.trim()
  }, 250)
})

onUnmounted(() => clearTimeout(timer))
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-4">
      <h1>Rezepte</h1>

      <p class="text-muted-foreground max-w-prose">
        Finde Rezepte, die zu deinem Tag passen — gefiltert nach Ernährungsform, Mahlzeit und
        Ausstattung.
      </p>
    </div>

    <div class="flex flex-col gap-3 lg:flex-row lg:justify-between">
      <div class="md:max-w-sm">
        <RecipeSearchBar v-model="searchInput" />
      </div>

      <RecipeFilterBar />
    </div>

    <RecipeList />
  </div>
</template>
