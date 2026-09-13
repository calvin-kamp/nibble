<script setup lang="ts">
import { computed } from 'vue'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Button } from '@/components/ui/button'
import { FormFieldset } from '@/components/form'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { ChevronDownIcon } from '@lucide/vue'
import RecipeFilterOption from './RecipeFilterOption.vue'
import type { Option } from '@/types/form.types'

interface Props {
  triggerLabel: string
  filterDescription?: string
  options: Option[]
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
  <Popover>
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        :data-active="selectedCount > 0"
        class="data-[active=true]:border-primary data-[active=true]:bg-primary-subtle data-[active=true]:text-primary-subtle-foreground rounded-full"
      >
        {{ props.triggerLabel }}

        <span
          v-if="selectedCount > 0"
          class="bg-primary text-primary-foreground grid h-5 min-w-5 place-items-center rounded-full px-1 text-xs font-semibold tabular-nums"
          aria-hidden="true"
        >
          {{ selectedCount }}
        </span>

        <span
          v-if="selectedCount > 0"
          class="sr-only"
        >
          {{ selectedCount }} ausgewählt
        </span>

        <LucideIcon :icon="ChevronDownIcon" />
      </Button>
    </PopoverTrigger>

    <PopoverContent align="start">
      <FormFieldset
        :label="props.triggerLabel"
        :description="props.filterDescription"
        sr-only-label
      >
        <div class="flex flex-col">
          <RecipeFilterOption
            v-for="option in props.options"
            :key="option.value"
            :label="option.label"
            :checked="isChecked(option.value)"
            :disabled="option.disabled"
            @toggle="(checked) => toggle(option.value, checked)"
          />
        </div>
      </FormFieldset>
    </PopoverContent>
  </Popover>
</template>
