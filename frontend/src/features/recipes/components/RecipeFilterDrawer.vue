<script setup lang="ts">
import type { RecipeFilterKey } from '../recipes.types'

import { useRecipeFilters } from '../recipe-filters'
import { filterOptions } from '../recipes.data'
import RecipeFilterOption from './RecipeFilterOption.vue'
import { UiBadge, UiButton, UiDrawer, UiIcon, UiSeparator } from '@components/ui'
import { SlidersHorizontalIcon } from '@lucide/vue'
import { ref } from 'vue'

const { filters, activeCount, reset } = useRecipeFilters()

const open = ref<boolean>(false)

function isChecked(key: RecipeFilterKey, value: string): boolean {
  return filters[key].includes(value)
}

function toggle(key: RecipeFilterKey, value: string, checked: boolean): void {
  filters[key] = checked
    ? [...filters[key], value]
    : filters[key].filter((entry) => entry !== value)
}
</script>

<template>
  <UiDrawer
    v-model:open="open"
    title="Filter"
    description="Mehrfachauswahl ist möglich. Die Auswahl wirkt sofort auf die Liste."
    sr-only-description
  >
    <template #trigger>
      <UiButton
        variant="ghost"
        class="w-full border border-input"
      >
        <UiIcon :icon="SlidersHorizontalIcon" />

        Filter

        <UiBadge
          v-if="activeCount > 0"
          class="min-w-5 justify-center px-1 tabular-nums"
          aria-hidden="true"
        >
          {{ activeCount }}
        </UiBadge>

        <span
          v-if="activeCount > 0"
          class="sr-only"
        >
          {{ activeCount }} Filter aktiv
        </span>
      </UiButton>
    </template>

    <template #content>
      <div class="flex max-h-[55vh] flex-col gap-6 overflow-y-auto px-1 pb-2">
        <template
          v-for="(filterOption, index) in filterOptions"
          :key="filterOption.key"
        >
          <UiSeparator v-if="index > 0" />

          <fieldset class="flex min-w-0 flex-col">
            <legend class="w-full font-medium">{{ filterOption.triggerLabel }}</legend>

            <p
              v-if="filterOption.filterDescription"
              class="mt-1 text-muted-foreground text-sm"
            >
              {{ filterOption.filterDescription }}
            </p>

            <div class="mt-2 flex flex-col">
              <RecipeFilterOption
                v-for="option in filterOption.options"
                :key="option.value"
                :label="option.label"
                :checked="isChecked(filterOption.key, option.value)"
                :disabled="option.disabled"
                @toggle="(checked) => toggle(filterOption.key, option.value, checked)"
              />
            </div>
          </fieldset>
        </template>
      </div>
    </template>

    <template #footer>
      <UiButton
        class="w-full"
        @click="open = false"
      >
        Rezepte anzeigen
      </UiButton>

      <UiButton
        variant="ghost"
        class="w-full border border-input"
        :disabled="activeCount === 0"
        @click="reset"
      >
        Zurücksetzen
      </UiButton>
    </template>
  </UiDrawer>
</template>
