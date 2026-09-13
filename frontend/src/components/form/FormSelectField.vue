<script setup lang="ts">
import { Field as VeeField } from 'vee-validate'
import { computed, useId, useSlots } from 'vue'
import { Field, FieldDescription, FieldError, FieldLabel } from '../ui/field'
import {
  Select as SelectRoot,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '../ui/select'
import type { Option, OptionGroup } from '@/types/form.types'

interface Props {
  fieldName: string
  label: string
  options: Option[] | OptionGroup[]
  placeholder: string
  srOnlyLabel?: boolean
  description?: string
  srOnlyDescription?: boolean
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  srOnlyLabel: false,
  description: undefined,
  srOnlyDescription: false,
  required: false,
  disabled: false,
})

const slots = useSlots()

const fieldId: string = useId()
const descriptionId: string = `${fieldId}-description`
const errorId: string = `${fieldId}-error`

const hasDescription = computed<boolean>(() => Boolean(props.description || slots.description))

function describedBy(invalid: boolean): string | undefined {
  const ids: string[] = []

  if (hasDescription.value) ids.push(descriptionId)
  if (invalid) ids.push(errorId)

  return ids.join(' ') || undefined
}

function isOptionGroup(option: Option | OptionGroup): option is OptionGroup {
  return 'options' in option
}
</script>

<template>
  <VeeField
    v-slot="{ componentField, errors }"
    :name="props.fieldName"
  >
    <Field :data-invalid="errors.length > 0">
      <FieldLabel
        :for="fieldId"
        :required-mark="props.required"
        :class="{ 'sr-only': props.srOnlyLabel }"
      >
        {{ props.label }}
      </FieldLabel>

      <FieldDescription
        v-if="hasDescription"
        :id="descriptionId"
        :class="{ 'sr-only': props.srOnlyDescription }"
      >
        <slot name="description">
          {{ props.description }}
        </slot>
      </FieldDescription>

      <SelectRoot v-bind="componentField">
        <SelectTrigger
          :id="fieldId"
          :disabled="props.disabled"
          :aria-invalid="errors.length > 0"
          :aria-required="props.required"
          :aria-describedby="describedBy(errors.length > 0)"
        >
          <SelectValue :placeholder="props.placeholder" />
        </SelectTrigger>

        <SelectContent>
          <template
            v-for="(option, index) in props.options"
            :key="index"
          >
            <SelectGroup v-if="isOptionGroup(option)">
              <SelectLabel>
                {{ option.label }}
              </SelectLabel>

              <SelectItem
                v-for="groupedOption in option.options"
                :key="groupedOption.value"
                :value="groupedOption.value"
                :disabled="groupedOption.disabled"
              >
                {{ groupedOption.label }}
              </SelectItem>
            </SelectGroup>

            <SelectItem
              v-else
              :value="option.value"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </SelectItem>
          </template>
        </SelectContent>
      </SelectRoot>

      <FieldError
        v-if="errors.length > 0"
        :id="errorId"
        :errors="errors"
      />
    </Field>
  </VeeField>
</template>
