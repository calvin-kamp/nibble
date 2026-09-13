<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouteQuery } from '@vueuse/router'
import { useDebounceFn } from '@vueuse/core'
import RecipeSearchBar from '../components/RecipeSearchBar.vue'
import RecipeFilterBar from '../components/RecipeFilterBar.vue'
import RecipeList from '../components/RecipeList.vue'

const search = useRouteQuery<string>('suche', '')
const searchValue = ref(search.value)

const commit = useDebounceFn((value: string): void => {
  search.value = value.trim()
}, 250)

watch(searchValue, commit)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-4">
      <h1>Rezepte</h1>

      <p class="text-muted-foreground max-w-[60ch]">
        Finde Rezepte, die zu deinem Tag passen — gefiltert nach Ernährungsform, Mahlzeit und
        Ausstattung.
      </p>
    </div>

    <div class="flex flex-col gap-3">
      <div class="sm:max-w-sm">
        <RecipeSearchBar v-model="searchValue" />
      </div>

      <RecipeFilterBar />
    </div>

    <RecipeList />
  </div>
</template>
