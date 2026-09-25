<script setup lang="ts">
import type { RecipeFilterKey } from '../recipes.types'

import { useTemplateRef } from 'vue'
import { UiButton, UiPopover } from '@components/ui'
import { useRecipeFilters } from '../recipe-filters'
import { filterOptions } from '../recipes.data'
import RecipeFilterOption from './RecipeFilterOption.vue'
import RecipeFilterTrigger from './RecipeFilterTrigger.vue'

const { filters, activeCount, reset } = useRecipeFilters()

const groups = useTemplateRef<HTMLDivElement>('groups')

function isChecked(key: RecipeFilterKey, value: string): boolean {
  return filters[key].includes(value)
}

function toggle(key: RecipeFilterKey, value: string, checked: boolean): void {
  filters[key] = checked
    ? [...filters[key], value]
    : filters[key].filter((entry) => entry !== value)
}

/** Without this the focus lands on the panel itself and the first option is one tab away */
function focusFirstOption(event: Event): void {
  event.preventDefault()

  groups.value?.querySelector<HTMLElement>('[role="checkbox"]')?.focus()
}
</script>

<template>
  <UiPopover
    title="Filter"
    description="Mehrfachauswahl ist möglich. Die Auswahl wirkt sofort auf die Liste."
    sr-only-description
    align="start"
    content-class="w-256"
    @open-auto-focus="focusFirstOption"
  >
    <template #trigger>
      <RecipeFilterTrigger />
    </template>

    <template #content>
      <div
        ref="groups"
        class="grid grid-cols-5 gap-6"
      >
        <fieldset
          v-for="filterOption in filterOptions"
          :key="filterOption.key"
          class="flex min-w-0 flex-col"
        >
          <legend class="w-full font-medium">{{ filterOption.triggerLabel }}</legend>

          <p
            v-if="filterOption.filterDescription"
            class="sr-only"
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
      </div>

      <div class="flex justify-end pt-4 border-border border-t">
        <UiButton
          variant="ghost"
          class="border border-input"
          :disabled="activeCount === 0"
          @click="reset"
        >
          Zurücksetzen
        </UiButton>
      </div>
    </template>
  </UiPopover>
</template>
