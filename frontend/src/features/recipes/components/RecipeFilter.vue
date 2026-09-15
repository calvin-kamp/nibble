<script setup lang="ts">
import type { SelectOption } from '@components/form'

import RecipeFilterOption from './RecipeFilterOption.vue'
import { UiBadge, UiButton, UiIcon, UiPopover } from '@components/ui'
import { ChevronDownIcon } from '@lucide/vue'
import { computed } from 'vue'

interface Props {
  triggerLabel: string
  filterDescription?: string
  options: SelectOption[]
}

const props = withDefaults(defineProps<Props>(), {
  filterDescription: undefined,
})

const filterValue = defineModel<string[]>({ default: () => [] })

const selectedCount = computed<number>(() => filterValue.value.length)

function isChecked(value: string): boolean {
  return filterValue.value.includes(value)
}

function toggle(value: string, checked: boolean): void {
  filterValue.value = checked
    ? [...filterValue.value, value]
    : filterValue.value.filter((entry) => entry !== value)
}
</script>

<template>
  <UiPopover
    :title="props.triggerLabel"
    :description="props.filterDescription"
    align="start"
  >
    <template #trigger>
      <UiButton
        variant="ghost"
        :data-active="selectedCount > 0"
        class="rounded-full border border-input data-[active=true]:border-primary data-[active=true]:bg-primary/10"
      >
        {{ props.triggerLabel }}

        <UiBadge
          v-if="selectedCount > 0"
          class="min-w-5 justify-center px-1 tabular-nums"
          aria-hidden="true"
        >
          {{ selectedCount }}
        </UiBadge>

        <span
          v-if="selectedCount > 0"
          class="sr-only"
        >
          {{ selectedCount }} ausgewählt
        </span>

        <UiIcon :icon="ChevronDownIcon" />
      </UiButton>
    </template>

    <template #content>
      <RecipeFilterOption
        v-for="option in props.options"
        :key="option.value"
        :label="option.label"
        :checked="isChecked(option.value)"
        :disabled="option.disabled"
        @toggle="(checked) => toggle(option.value, checked)"
      />
    </template>
  </UiPopover>
</template>
