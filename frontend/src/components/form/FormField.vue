<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import { Field as VeeField, useFieldError } from 'vee-validate'
import { Label as RekaLabel } from 'reka-ui'
import { UiIcon } from '@components/ui'
import { CircleAlertIcon } from '@lucide/vue'
import { useFieldIds } from './field-ids'
import { toRef, useSlots } from 'vue'

const props = defineProps<FormFieldProps>()
const error = useFieldError(toRef(props, 'fieldName'))

const slots = useSlots()

const { fieldId, descriptionId, errorId, describedBy } = useFieldIds(
  () => Boolean(props.description) || Boolean(slots.description),
)
</script>

<template>
  <VeeField
    v-slot="{ componentField, errors }"
    :name="props.fieldName"
    :validate-on-blur="false"
    :validate-on-model-update="Boolean(error)"
  >
    <div class="flex flex-col gap-2 w-full">
      <RekaLabel
        :for="fieldId"
        class="font-medium"
      >
        {{ props.label }}

        <span
          v-if="props.required"
          aria-hidden="true"
        >
          *
        </span>
      </RekaLabel>

      <p
        v-if="props.description || $slots.description"
        :id="descriptionId"
        class="text-sm text-muted-foreground"
      >
        <slot name="description">{{ props.description }}</slot>
      </p>

      <slot
        :id="fieldId"
        :component-field="componentField"
        :invalid="Boolean(error)"
        :described-by="describedBy(Boolean(error))"
        name="control"
      />

      <div
        v-if="errors.length"
        :id="errorId"
        role="alert"
        class="flex items-start gap-1 text-destructive text-sm"
      >
        <UiIcon
          :icon="CircleAlertIcon"
          class="mt-0.5"
        />

        <span v-if="errors.length === 1">{{ errors[0] }}</span>

        <ul
          v-else
          class="flex flex-col gap-1"
        >
          <li
            v-for="error in errors"
            :key="error"
          >
            {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </VeeField>
</template>
