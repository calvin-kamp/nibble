<script setup lang="ts">
import type { RecipeFilterKey } from '../recipes.types'

import { XIcon } from '@lucide/vue'
import { computed, nextTick, useTemplateRef, watch } from 'vue'
import { UiButton, UiIcon } from '@components/ui'
import { useRecipeFilters } from '../recipe-filters'
import { FILTER_TRIGGER_ID, filterOptions } from '../recipes.data'

interface ActiveFilter {
  key: RecipeFilterKey
  value: string
  groupLabel: string
}

const { filters, activeCount, reset } = useRecipeFilters()

const chipRefs = useTemplateRef<HTMLButtonElement[]>('chip')

// Position of the removed chip; the focus moves there once the list has been rendered again.
let pendingIndex: number | null = null

const activeFilters = computed<ActiveFilter[]>(() =>
  filterOptions.flatMap((filterOption) =>
    filterOption.options
      .filter((option) => filters[filterOption.key].includes(option.value))
      .map((option) => ({
        key: filterOption.key,
        value: option.value,
        groupLabel: filterOption.triggerLabel,
      })),
  ),
)

function remove(chip: ActiveFilter, index: number): void {
  pendingIndex = index

  filters[chip.key] = filters[chip.key].filter((entry) => entry !== chip.value)
}

function removeAll(): void {
  pendingIndex = -1

  reset()
}

watch(activeFilters, async () => {
  if (pendingIndex === null) return

  const index = pendingIndex

  pendingIndex = null

  await nextTick()

  const chips = chipRefs.value ?? []
  const target = index < 0 ? undefined : (chips[index] ?? chips[index - 1])

  if (target) target.focus()
  else document.getElementById(FILTER_TRIGGER_ID)?.focus()
})
</script>

<template>
  <div
    v-if="activeFilters.length > 0"
    role="group"
    aria-label="Aktive Filter"
    class="flex flex-wrap items-center gap-2"
  >
    <button
      v-for="(chip, index) in activeFilters"
      :key="`${chip.key}-${chip.value}`"
      ref="chip"
      type="button"
      :aria-label="`${chip.value} entfernen, ${chip.groupLabel}`"
      class="relative inline-flex h-8 items-center gap-1 pr-2 pl-3 bg-muted rounded-full border border-border cursor-pointer transition-interactive after:absolute after:inset-x-0 after:-inset-y-1.5 hover:bg-accent focus-visible:focus-ring"
      @click="remove(chip, index)"
    >
      {{ chip.value }}

      <UiIcon
        :icon="XIcon"
        class="text-muted-foreground"
      />
    </button>

    <UiButton
      v-if="activeCount > 1"
      variant="ghost"
      @click="removeAll"
    >
      Alle zurücksetzen
    </UiButton>
  </div>
</template>
