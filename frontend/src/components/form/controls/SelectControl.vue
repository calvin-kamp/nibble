<script setup lang="ts">
import type { SelectEntry } from '@interfaces/form.types'

import {
  SelectContent,
  SelectGroup,
  SelectIcon,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectLabel,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from 'reka-ui'
import { CheckIcon, ChevronDownIcon } from '@lucide/vue'
import { UiIcon } from '@components/ui'
import { isOptionGroup } from '@interfaces/form.types'

interface Props {
  options: SelectEntry[]
  placeholder?: string
  required?: boolean
  disabled?: boolean
}

defineOptions({ inheritAttrs: false })

const props = defineProps<Props>()

const modelValue = defineModel<string>()
</script>

<template>
  <SelectRoot
    v-model="modelValue"
    :required="props.required"
    :disabled="props.disabled"
  >
    <SelectTrigger
      v-bind="$attrs"
      :class="[
        'flex w-full h-11 items-center justify-between gap-2 px-4',
        'bg-input/30 border border-input rounded-md',
        'text-base',
        'data-placeholder:text-muted-foreground',
        'transition-interactive focus-visible:focus-ring',
        'aria-invalid:border-destructive aria-invalid:focus-visible:focus-ring-destructive',
        'disabled:inactive',
      ]"
    >
      <SelectValue :placeholder="props.placeholder" />

      <SelectIcon as-child>
        <UiIcon
          :icon="ChevronDownIcon"
          :size="18"
        />
      </SelectIcon>
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        position="popper"
        align="start"
        :side-offset="4"
        class="z-50 min-w-(--reka-select-trigger-width) p-1 bg-popover rounded-md border text-popover-foreground"
      >
        <SelectViewport>
          <template
            v-for="(entry, index) in props.options"
            :key="index"
          >
            <SelectGroup v-if="isOptionGroup(entry)">
              <SelectLabel class="px-3 py-2 text-sm text-muted-foreground">{{
                entry.label
              }}</SelectLabel>

              <SelectItem
                v-for="option in entry.options"
                :key="option.value"
                :value="option.value"
                :disabled="option.disabled"
                class="flex items-center justify-between gap-2 px-3 py-2 rounded-sm outline-hidden data-highlighted:bg-accent data-highlighted:text-accent-foreground data-disabled:inactive"
              >
                <SelectItemText>{{ option.label }}</SelectItemText>

                <SelectItemIndicator>
                  <UiIcon
                    :icon="CheckIcon"
                    :size="18"
                  />
                </SelectItemIndicator>
              </SelectItem>
            </SelectGroup>

            <SelectItem
              v-else
              :value="entry.value"
              :disabled="entry.disabled"
              class="flex items-center justify-between gap-2 px-3 py-2 rounded-sm outline-hidden data-highlighted:bg-accent data-highlighted:text-accent-foreground data-disabled:inactive"
            >
              <SelectItemText>{{ entry.label }}</SelectItemText>

              <SelectItemIndicator>
                <UiIcon
                  :icon="CheckIcon"
                  :size="18"
                />
              </SelectItemIndicator>
            </SelectItem>
          </template>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
