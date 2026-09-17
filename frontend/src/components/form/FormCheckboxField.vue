<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import { Field as VeeField, useFieldError } from 'vee-validate'
import { CheckboxControl } from './controls'
import { Label as RekaLabel } from 'reka-ui'
import { UiIcon } from '@components/ui'
import { CircleAlertIcon } from '@lucide/vue'
import { toRef } from 'vue'
import { useFieldIds } from './field-ids'

defineOptions({ inheritAttrs: false })

const props = defineProps<FormFieldProps>()

const error = useFieldError(toRef(props, 'fieldName'))

const { fieldId, descriptionId, errorId, describedBy } = useFieldIds(() =>
  Boolean(props.description),
)
</script>

<template>
  <VeeField
    v-slot="{ componentField, errors }"
    :name="props.fieldName"
    :validate-on-blur="false"
    :validate-on-model-update="Boolean(error)"
  >
    <div class="flex w-full flex-col gap-2">
      <div class="flex items-start gap-3">
        <span class="flex h-6 items-center">
          <CheckboxControl
            v-bind="{ ...$attrs, ...componentField }"
            :id="fieldId"
            :required="props.required"
            :aria-invalid="Boolean(error) || undefined"
            :aria-describedby="describedBy(Boolean(error))"
          />
        </span>

        <RekaLabel :for="fieldId">
          <slot name="label">{{ props.label }}</slot>

          <span
            v-if="props.required"
            aria-hidden="true"
          >
            *
          </span>
        </RekaLabel>
      </div>

      <div
        v-if="props.description || errors.length"
        class="flex flex-col gap-2"
      >
        <p
          v-if="props.description"
          :id="descriptionId"
          class="text-muted-foreground text-sm"
        >
          {{ props.description }}
        </p>

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
              v-for="message in errors"
              :key="message"
            >
              {{ message }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </VeeField>
</template>
