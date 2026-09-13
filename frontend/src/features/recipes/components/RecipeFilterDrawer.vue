<script setup lang="ts">
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/components/ui/drawer'
import { Button } from '@/components/ui/button'
import { FormFieldset } from '@/components/form'
import { Separator } from '@/components/ui/separator'
import LucideIcon from '@/components/shared/LucideIcon.vue'
import { SlidersHorizontalIcon } from '@lucide/vue'
import RecipeFilterOption from './RecipeFilterOption.vue'
import { filterOptions } from '../recipes.data'
import { useRecipeFilters } from '../useRecipeFilters'
import type { RecipeFilterKey } from '../recipes.types'

const { filters, activeCount, reset } = useRecipeFilters()

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
  <Drawer>
    <DrawerTrigger as-child>
      <Button
        variant="outline"
        class="w-full"
      >
        <LucideIcon :icon="SlidersHorizontalIcon" />
        Filter

        <span
          v-if="activeCount > 0"
          class="bg-primary text-primary-foreground grid h-5 min-w-5 place-items-center rounded-full px-1 text-xs font-semibold tabular-nums"
          aria-hidden="true"
        >
          {{ activeCount }}
        </span>

        <span
          v-if="activeCount > 0"
          class="sr-only"
        >
          {{ activeCount }} Filter aktiv
        </span>
      </Button>
    </DrawerTrigger>

    <DrawerContent>
      <DrawerHeader>
        <DrawerTitle>Filter</DrawerTitle>
      </DrawerHeader>

      <div class="flex flex-col gap-6 overflow-y-auto px-1 pb-2">
        <template
          v-for="(filterOption, index) in filterOptions"
          :key="filterOption.key"
        >
          <Separator v-if="index > 0" />

          <FormFieldset
            :label="filterOption.triggerLabel"
            :description="filterOption.filterDescription"
          >
            <div class="flex flex-col">
              <RecipeFilterOption
                v-for="option in filterOption.options"
                :key="option.value"
                :label="option.label"
                :checked="isChecked(filterOption.key, option.value)"
                :disabled="option.disabled"
                @toggle="(checked) => toggle(filterOption.key, option.value, checked)"
              />
            </div>
          </FormFieldset>
        </template>
      </div>

      <DrawerFooter class="flex-col gap-3 sm:flex-row">
        <DrawerClose as-child>
          <Button>Rezepte anzeigen</Button>
        </DrawerClose>

        <Button
          variant="outline"
          :disabled="activeCount === 0"
          @click="reset"
        >
          Zurücksetzen
        </Button>
      </DrawerFooter>
    </DrawerContent>
  </Drawer>
</template>
