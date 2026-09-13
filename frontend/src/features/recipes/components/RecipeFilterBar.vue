<script setup lang="ts">
import { Button } from '@/components/ui/button'
import RecipeFilter from './RecipeFilter.vue'
import RecipeFilterDrawer from './RecipeFilterDrawer.vue'
import { filterOptions } from '../recipes.data'
import { useRecipeFilters } from '../useRecipeFilters'

const { filters, activeCount, reset } = useRecipeFilters()
</script>

<template>
  <div class="sm:hidden">
    <RecipeFilterDrawer />
  </div>

  <div class="hidden flex-row flex-wrap items-center gap-2 sm:flex">
    <RecipeFilter
      v-for="filterOption in filterOptions"
      :key="filterOption.key"
      v-model="filters[filterOption.key]"
      :trigger-label="filterOption.triggerLabel"
      :filter-description="filterOption.filterDescription"
      :options="filterOption.options"
    />

    <Button
      v-if="activeCount > 0"
      variant="ghost"
      @click="reset"
    >
      Alle zurücksetzen
    </Button>
  </div>
</template>
