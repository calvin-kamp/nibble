<script setup lang="ts">
import type { FormFieldProps } from '@interfaces/form.types'

import { Field as VeeField, useFieldError } from 'vee-validate'
import { UiIcon } from '@components/ui'
import { CircleAlertIcon } from '@lucide/vue'
import { toRef, useId } from 'vue'
import { useFieldIds } from './field-ids'

const props = defineProps<FormFieldProps>()

const error = useFieldError(toRef(props, 'fieldName'))

const { fieldId, descriptionId, errorId, describedBy } = useFieldIds(() =>
  Boolean(props.description),
)

const legendId = useId()
</script>

<template>
  <VeeField
    v-slot="{ componentField, errors }"
    :name="props.fieldName"
    :validate-on-blur="false"
    :validate-on-model-update="Boolean(error)"
  >
    <fieldset class="w-full min-w-0">
      <legend
        :id="legendId"
        class="w-full font-medium"
      >
        {{ props.label }}

        <span
          v-if="props.required"
          aria-hidden="true"
        >
          *
        </span>
      </legend>

      <div class="mt-2 flex flex-col gap-2">
        <p
          v-if="props.description"
          :id="descriptionId"
          class="text-muted-foreground text-sm"
        >
          {{ props.description }}
        </p>

        <slot
          :id="fieldId"
          :labelled-by="legendId"
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
              v-for="message in errors"
              :key="message"
            >
              {{ message }}
            </li>
          </ul>
        </div>
      </div>
    </fieldset>
  </VeeField>
</template>
