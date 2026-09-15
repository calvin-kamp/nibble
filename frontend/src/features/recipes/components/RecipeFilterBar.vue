<script setup lang="ts">
import { useBreakpoint } from '@composables/breakpoint.ts'
import { useRecipeFilters } from '../recipe-filters'
import { filterOptions } from '../recipes.data'
import RecipeFilter from './RecipeFilter.vue'
import RecipeFilterDrawer from './RecipeFilterDrawer.vue'
import { UiButton } from '@components/ui'

const { filters, activeCount, reset } = useRecipeFilters()

const { activeBreakpoint } = useBreakpoint()
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <template v-if="activeBreakpoint === 'mobile'">
      <RecipeFilterDrawer />
    </template>

    <template v-else>
      <RecipeFilter
        v-for="filterOption in filterOptions"
        :key="filterOption.key"
        v-model="filters[filterOption.key]"
        :trigger-label="filterOption.triggerLabel"
        :filter-description="filterOption.filterDescription"
        :options="filterOption.options"
      />

      <UiButton
        v-if="activeCount > 0"
        variant="ghost"
        @click="reset"
      >
        Alle zurücksetzen
      </UiButton>
    </template>
  </div>
</template>
