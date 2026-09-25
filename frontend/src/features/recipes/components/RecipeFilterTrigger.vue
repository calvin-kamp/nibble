<script setup lang="ts">
import { SlidersHorizontalIcon } from '@lucide/vue'
import { UiBadge, UiButton, UiIcon } from '@components/ui'
import { useRecipeFilters } from '../recipe-filters'
import { FILTER_TRIGGER_ID } from '../recipes.data'

const { activeCount } = useRecipeFilters()
</script>

<template>
  <UiButton
    :id="FILTER_TRIGGER_ID"
    variant="ghost"
    :data-active="activeCount > 0"
    :aria-label="activeCount > 0 ? `Filter, ${activeCount} aktiv` : 'Filter'"
    class="w-11 justify-center px-0 rounded-md border border-input data-[active=true]:border-primary data-[active=true]:bg-primary/10 md:w-auto md:px-4"
  >
    <UiIcon
      :icon="SlidersHorizontalIcon"
      :size="20"
    />

    <span class="hidden md:inline">Filter</span>

    <UiBadge
      v-if="activeCount > 0"
      class="absolute -top-1 -right-1 min-w-5 justify-center px-1 tabular-nums md:static md:top-auto md:right-auto"
      aria-hidden="true"
    >
      {{ activeCount }}
    </UiBadge>
  </UiButton>
</template>
